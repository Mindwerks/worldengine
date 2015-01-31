#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI Interface for Lands
"""

import sys
from PyQt4 import QtGui

class LandsGui(QtGui.QWidget):
    
    def __init__(self):
        super(LandsGui, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))        
    
        self.show()


def main():
    
    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    w.resize(800, 600)
    w.setWindowTitle('Lands - A world generator')
    w.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
