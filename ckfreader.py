#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import operator
import os
import sys 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 

# extract relevant table from file
def extracttable(filename):
    data = open(filename,'r').read().split('Section')
    hkltable = []

    for line in data[2].split('\n'):
        row = []
        line = " ".join(line.split())
        items = line.split(' ')
        try:
            if len(items) == 11:
                for item in items:
                    try:
                        item = int(item)
                    except:
                        try:
                            item = float(item)
                        except:
                            pass
                    row.append(item)
                hkltable.append(row)
        except:
            pass
    return hkltable
 
def main():
    app = QApplication(sys.argv) 
    w = MyWindow() 
    w.setWindowTitle('Manage outlier from PLATON ckf files')
    w.show() 
    sys.exit(app.exec_()) 

class MyWindow(QWidget): 
    def __init__(self, *args): 
        QWidget.__init__(self, *args) 

        # create table
        self.get_table_data()
        self.table = self.createTable() 

        # create button
        self.button = QPushButton('Generate OMIT', self)
        self.button.clicked.connect(self.handleButton)
         
        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.table) 
        layout.addWidget(self.button)
        self.setLayout(layout)

    # make h k l look nice again
    def hklindendter(self, value):
        if len(value) == 1:
            return "  " + value
        elif len(value) == 2:
            return " " + value
        else:
            return value

    def handleButton(self):
        # get selected rows from QTableView
        indexes = self.table.selectionModel().selectedRows()

        instructions = ""
        # data from rows
        for index in sorted(indexes):
            h = self.table.model().index(index.row(), 1).data().toPyObject()
            k = self.table.model().index(index.row(), 2).data().toPyObject()
            l = self.table.model().index(index.row(), 3).data().toPyObject()
            ratiow = self.table.model().index(index.row(), 10).data().toPyObject()
            # description for OMIT
            if ratiow > 0:
                comment = "! Outlier, Fo > Fc"
            elif ratiow < 0:
                comment = "! Behind beam stop shadow"
            else:
                comment = " "
            # generate OMIT line for .ins file
            omitline = "OMIT " + self.hklindendter(str(h)) + " " + self.hklindendter(str(k)) + " " + self.hklindendter(str(l)) + "   " + comment
            # add OMIT line to multi-line OMIT block
            instructions = instructions + omitline + "\n"
        # OMIT block as HTML
        htmlinstructions = instructions.replace("\n", "<br>")
        htmlinstructions = htmlinstructions.replace(" ", "&nbsp;")

        # put OMIT block in clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(instructions)

        # popup with OMIT instructions
        msg = QMessageBox()
        msg.setWindowTitle("OMIT instructions")
        msg.setInformativeText("OMIT instructions copied to clipboard!")
        msg.setText("<tt>" + htmlinstructions + "</tt>")
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()


    # file dialog for file selection
    # only ckf files allowed
    # runs at program start
    def get_table_data(self):
        dialog = QFileDialog()
        dialog.setWindowTitle('Open PLATON ckf File')
        dialog.setNameFilter('PLATON ckf files (*.ckf)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            filename = dialog.selectedFiles()[0]
        self.tabledata = extracttable(filename)

    def createTable(self):
        # create the view
        tv = QTableView()

        # set the table model
        header = self.tabledata[0]
        header.append("Checked")
        tm = MyTableModel(self.tabledata[1:], header, self) 
        tv.setModel(tm)

        # set the minimum size
        tv.setMinimumSize(700, 600)

        # hide grid
        tv.setShowGrid(False)

        # set the font
        font = QFont("Courier New", 10)
        tv.setFont(font)

        # hide vertical header
        vh = tv.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties
        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        tv.resizeColumnsToContents()

        # set row height
        nrows = len(self.tabledata)
        for row in xrange(nrows):
            tv.setRowHeight(row, 20)

        # enable sorting
        tv.setSortingEnabled(True)

        tv.setSelectionBehavior(QAbstractItemView.SelectRows)

        return tv
 
class MyTableModel(QAbstractTableModel): 
    def __init__(self, datain, headerdata, parent=None, *args): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata
 
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent): 
        return len(self.arraydata[0])
 
    def data(self, index, role): 
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant(self.arraydata[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order != Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

if __name__ == "__main__": 
    main()