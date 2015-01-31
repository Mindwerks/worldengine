#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI Interface for Lands
"""

import sys
from PyQt4 import QtGui

class LandsGui(QtGui.QMainWindow):
    
    def __init__(self):
        super(LandsGui, self).__init__()
        
        self.initUI()
        
    def set_status(self, message):
    	self.statusBar().showMessage(message)
        
    def initUI(self):            
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
    	print("Generate...")
        

def main():
    
    app = QtGui.QApplication(sys.argv)

    lg = LandsGui()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
