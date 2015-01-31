#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI Interface for Lands
"""

import sys
from PyQt4 import QtGui
import random

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
        name_value = QtGui.QLineEdit(name)
        grid.addWidget(name_value, 0,1,1,2)

        seed_label = QtGui.QLabel('Seed')
        grid.addWidget(seed_label, 1,0,1,1)        
        seed_value = self._spinner_box(0, 65525, seed)
        grid.addWidget(seed_value, 1,1,1,2)

        width_label = QtGui.QLabel('Width')
        grid.addWidget(width_label, 2,0,1,1)        
        width_value = self._spinner_box(100, 8192, 512)
        grid.addWidget(width_value, 2,1,1,2)

        height_label = QtGui.QLabel('Height')
        grid.addWidget(height_label, 3,0,1,1)
        height_value = self._spinner_box(100, 8192, 512)
        grid.addWidget(height_value, 3,1,1,2)        

        plates_num_label = QtGui.QLabel('Number of plates')
        grid.addWidget(plates_num_label, 4,0,1,1)
        plates_num_value = self._spinner_box(2, 100, 10)
        grid.addWidget(plates_num_value, 4,1,1,2)

        platesres_w_label = QtGui.QLabel('Plates resolution (width)')
        grid.addWidget(platesres_w_label, 5,0,1,1)
        platesres_w_value = self._spinner_box(50, 4096, 512)
        grid.addWidget(platesres_w_value, 5,1,1,2)

        platesres_h_label = QtGui.QLabel('Plates resolution (height)')
        grid.addWidget(platesres_h_label, 6,0,1,1)
        platesres_h_value = self._spinner_box(50, 4096, 512)
        grid.addWidget(platesres_h_value, 6,1,1,2)

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

class GenerationProgressDialog(QtGui.QDialog):

    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self._init_ui()

    def _init_ui(self):            
        self.resize(400, 100)
        self.setWindowTitle('Generating a new world...')
        grid = QtGui.QGridLayout()

        status = QtGui.QLabel('....') 
        grid.addWidget(status, 0, 0, 1, 3)       

        progress = QtGui.QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        grid.addWidget(progress, 1, 0, 1, 3)       

        cancel   = QtGui.QPushButton('Cancel')
        grid.addWidget(cancel, 2, 0, 1, 1)
        cancel.clicked.connect(self._on_cancel)

        self.setLayout(grid)

    def _on_cancel(self):
        QtGui.QDialog.reject(self)        

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
            dialog2 = GenerationProgressDialog()
            ok2     = dialog2.exec_()         

def main():
    
    app = QtGui.QApplication(sys.argv)

    lg = LandsGui()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
