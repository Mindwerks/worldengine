#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI Interface for Lands
"""

import sys
from PyQt4 import QtGui
import random
import threading
import platec

class GenerateDialog(QtGui.QDialog):

    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
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

class GenerationProgressDialog(QtGui.QDialog):

    def __init__(self, seed, width, height, num_plates):
        QtGui.QDialog.__init__(self)
        self._init_ui()
        self.gen_thread = GenerationThread(self, seed, width, height, num_plates)
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

        self.setLayout(grid)

    def _on_cancel(self):
        QtGui.QDialog.reject(self)       

    def set_status(self, message):
        self.status.setText(message)


class GenerationThread(threading.Thread):

    def __init__(self, ui, seed, width, height, num_plates):
        threading.Thread.__init__(self)
        print('seed %i' % seed)
        print('width %i' % width)
        print('height %i' % height)
        print('num_plates %i' % num_plates)
        self.plates_generation = PlatesGeneration(seed, width, height, num_plates=num_plates)
        self.ui = ui
    
    def run (self):        
        finished = False
        while not finished:
            (finished, n_steps) = self.plates_generation.step() 
            print("n_steps %i %s" % (n_steps, finished))       
            self.ui.set_status('Step %i' % n_steps)        

class PlatesGeneration():

    def __init__(self, seed, width, height, 
                 sea_level=0.65, erosion_period=60,
                 folding_ratio=0.02, aggr_overlap_abs=1000000, aggr_overlap_rel=0.33,
                 cycle_count=2, num_plates=10):
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

class LandsGui(QtGui.QMainWindow):
    
    def __init__(self):
        super(LandsGui, self).__init__()        
        self._init_ui()

    def set_status(self, message):
        self.statusBar().showMessage(message)
        
    def _init_ui(self):            
        self.resize(800, 600)
        self.setWindowTitle('Lands - A world generator')        
        self.set_status('No world selected: create or load a world')
        self._prepare_menu()
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
        dialog = GenerateDialog()
        ok = dialog.exec_()
        if ok:            
            seed = dialog.seed()
            width = dialog.width()
            height = dialog.height()
            num_plates = dialog.num_plates()
            dialog2 = GenerationProgressDialog(seed, width, height, num_plates)            
            ok2     = dialog2.exec_()         

def main():
    
    app = QtGui.QApplication(sys.argv)

    lg = LandsGui()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
