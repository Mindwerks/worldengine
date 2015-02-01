#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI Interface for Lands
"""

import sys
from PyQt4 import QtGui, QtCore
import random
import threading
import platec
from draw import elevation_color
from world import World
import geo

def _draw_simple_elevation_on_screen(world, canvas):
    width = world.width
    height = world.height
    for y in range(0, height):
        for x in range(0, width):
            e = world.elevation['data'][y][x]
            r, g, b = elevation_color(e)
            col = QtGui.QColor(int(r*255),int(g*255),int(b*255))
            canvas.setPixel(x, y, col.rgb())    

def _draw_bw_elevation_on_screen(world, canvas):
    width = world.width
    height = world.height
    max_el = world.max_elevation()
    min_el = world.min_elevation()
    delta_el = max_el - min_el
    for y in range(0, height):
        for x in range(0, width):
            e = world.elevation['data'][y][x]
            e_normalized = (e - min_el) / delta_el
            r = g = b = e_normalized
            col = QtGui.QColor(int(r*255),int(g*255),int(b*255))             
            canvas.setPixel(x, y, col.rgb())

class GenerateDialog(QtGui.QDialog):

    def __init__(self,parent):
        QtGui.QDialog.__init__(self, parent)
        self._init_ui()

    def _init_ui(self):            
        self.resize(500, 300)
        self.setWindowTitle('Generate a new world')
        grid = QtGui.QGridLayout()

        seed =  random.randint(0, 65535)

        name_label = QtGui.QLabel('Name')
        grid.addWidget(name_label, 0,0,1,1)
        name = 'world_seed_%i' % seed 
        self.name_value = QtGui.QLineEdit(name)
        grid.addWidget(self.name_value, 0,1,1,2)

        seed_label = QtGui.QLabel('Seed')
        grid.addWidget(seed_label, 1,0,1,1)        
        self.seed_value = self._spinner_box(0, 65525, seed)
        grid.addWidget(self.seed_value, 1,1,1,2)

        width_label = QtGui.QLabel('Width')
        grid.addWidget(width_label, 2,0,1,1)        
        self.width_value = self._spinner_box(100, 8192, 512)
        grid.addWidget(self.width_value, 2,1,1,2)

        height_label = QtGui.QLabel('Height')
        grid.addWidget(height_label, 3,0,1,1)
        self.height_value = self._spinner_box(100, 8192, 512)
        grid.addWidget(self.height_value, 3,1,1,2)        

        plates_num_label = QtGui.QLabel('Number of plates')
        grid.addWidget(plates_num_label, 4,0,1,1)
        self.plates_num_value = self._spinner_box(2, 100, 10)
        grid.addWidget(self.plates_num_value, 4,1,1,2)

        platesres_w_label = QtGui.QLabel('Plates resolution (width)')
        grid.addWidget(platesres_w_label, 5,0,1,1)
        self.platesres_w_value = self._spinner_box(50, 4096, 512)
        grid.addWidget(self.platesres_w_value, 5,1,1,2)

        platesres_h_label = QtGui.QLabel('Plates resolution (height)')
        grid.addWidget(platesres_h_label, 6,0,1,1)
        self.platesres_h_value = self._spinner_box(50, 4096, 512)
        grid.addWidget(self.platesres_h_value, 6,1,1,2)

        buttons_row = 7
        cancel   = QtGui.QPushButton('Cancel')
        generate = QtGui.QPushButton('Generate')
        grid.addWidget(cancel,   buttons_row, 1, 1, 1)
        grid.addWidget(generate, buttons_row, 2, 1, 1)
        cancel.clicked.connect(self._on_cancel)
        generate.clicked.connect(self._on_generate)

        self.setLayout(grid)

    def _spinner_box(self, min, max, value):
        spinner = QtGui.QSpinBox()
        spinner.setMinimum(min)
        spinner.setMaximum(max)
        spinner.setValue(value)
        return spinner

    def _on_cancel(self):
        QtGui.QDialog.reject(self)

    def _on_generate(self):        
        QtGui.QDialog.accept(self)

    def seed(self):
        return self.seed_value.value()

    def width(self):
        return self.platesres_w_value.value()

    def height(self):
        return self.platesres_h_value.value()

    def num_plates(self):        
        return self.plates_num_value.value()

    def name(self):
        return self.name_value.text()        

class GenerationProgressDialog(QtGui.QDialog):

    def __init__(self, parent, seed, name, width, height, num_plates):
        QtGui.QDialog.__init__(self, parent)
        self._init_ui()
        self.world = None
        self.gen_thread = GenerationThread(self, seed, name, width, height, num_plates)
        self.gen_thread.start()

    def _init_ui(self):            
        self.resize(400, 100)
        self.setWindowTitle('Generating a new world...')
        grid = QtGui.QGridLayout()

        self.status = QtGui.QLabel('....') 
        grid.addWidget(self.status, 0, 0, 1, 3)          

        cancel   = QtGui.QPushButton('Cancel')
        grid.addWidget(cancel, 1, 0, 1, 1)
        cancel.clicked.connect(self._on_cancel)

        done   = QtGui.QPushButton('Done')
        grid.addWidget(done, 1, 2, 1, 1)
        done.clicked.connect(self._on_done)
        done.setEnabled(False)
        self.done = done

        self.setLayout(grid)

    def _on_cancel(self):
        QtGui.QDialog.reject(self)       

    def _on_done(self):        
        QtGui.QDialog.accept(self)       

    def on_finish(self):
        self.done.setEnabled(True) 

    def set_status(self, message):
        self.status.setText(message)


class GenerationThread(threading.Thread):

    def __init__(self, ui, seed, name, width, height, num_plates):
        threading.Thread.__init__(self)
        self.plates_generation = PlatesGeneration(seed, name, width, height, num_plates=num_plates)
        self.ui = ui
    
    def run(self):        
        finished = False
        while not finished:
            (finished, n_steps) = self.plates_generation.step() 
            self.ui.set_status('Plate simulation: step %i' % n_steps)
        self.ui.set_status('Plate simulation: finalization')
        w = self.plates_generation.world()
        geo.initialize_ocean_and_thresholds(w)
        self.ui.set_status('Plate simulation: completed')
        self.ui.world = w
        self.ui.on_finish()

def array_to_matrix(array, width, height):
    if (len(array) != (width * height)):
        raise Exception("Array as not expected length")
    matrix = []
    for y in xrange(height):
        matrix.append([])
        for x in xrange(width):
            matrix[y].append(array[y * width + x])
    return matrix

class PlatesGeneration():

    def __init__(self, seed, name, width, height, 
                 sea_level=0.65, erosion_period=60,
                 folding_ratio=0.02, aggr_overlap_abs=1000000, aggr_overlap_rel=0.33,
                 cycle_count=2, num_plates=10):
        self.name   = name
        self.width  = width
        self.height = height
        self.p = platec.create(seed, width, height, sea_level, erosion_period, folding_ratio,
                               aggr_overlap_abs, aggr_overlap_rel, cycle_count, num_plates)
        self.steps = 0

    def step(self):
        if platec.is_finished(self.p) == 0:
            platec.step(self.p)
            self.steps += 1
            return (False, self.steps)
        else:
            return (True, self.steps)      

    def world(self):
        world = World(self.name, self.width, self.height)
        hm = platec.get_heightmap(self.p)
        world.set_elevation(array_to_matrix(hm, self.width, self.height), None)
        return world

class MapCanvas(QtGui.QImage):

    def __init__(self, label, width, height):
        QtGui.QImage.__init__(self, width, height, QtGui.QImage.Format_RGB32);
        self.label = label
        self._update()

    def draw_world(self, world):
        #_draw_simple_elevation_on_screen(world, self)
        self.label.resize(world.width, world.height)
        _draw_bw_elevation_on_screen(world, self)
        self._update()

    def _update(self):
        self.label.setPixmap(QtGui.QPixmap.fromImage(self))

class LandsGui(QtGui.QMainWindow):
    
    def __init__(self):
        super(LandsGui, self).__init__()        
        self._init_ui()
        self.world = None

    def set_status(self, message):
        self.statusBar().showMessage(message)
        
    def _init_ui(self):            
        self.resize(800, 600)
        self.setWindowTitle('Lands - A world generator')        
        self.set_status('No world selected: create or load a world')
        self._prepare_menu()
        self.label = QtGui.QLabel()
        self.canvas = MapCanvas(self.label, 0, 0)            

        self.main_widget = QtGui.QWidget(self) # dummy widget to contain the
                                               # layout manager
        self.setCentralWidget(self.main_widget)
        self.layout = QtGui.QGridLayout(self.main_widget)
        # Set the stretch
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(2, 1)
        # Add widgets
        self.layout.addWidget(self.label, 1, 1)
        self.show()

    def _prepare_menu(self):
        generateAction = QtGui.QAction('&Generate', self)        
        generateAction.setShortcut('Ctrl+G')
        generateAction.setStatusTip('Generate new world')
        generateAction.triggered.connect(self._on_generate)

        exitAction = QtGui.QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(generateAction)
        fileMenu.addAction(exitAction)

    def _on_generate(self):
        dialog = GenerateDialog(self)
        ok = dialog.exec_()
        if ok:            
            seed = dialog.seed()
            width = dialog.width()
            height = dialog.height()
            num_plates = dialog.num_plates()
            name = dialog.name()
            dialog2 = GenerationProgressDialog(self, seed, name, width, height, num_plates)            
            ok2     = dialog2.exec_()
            if ok2:                
                self.world = dialog2.world
                self.canvas = MapCanvas(self.label, self.world.width, self.world.height) 
                self.canvas.draw_world(self.world)

def main():
    
    app = QtGui.QApplication(sys.argv)

    lg = LandsGui()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
