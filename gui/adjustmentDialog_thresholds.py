"""
/***************************************************************************
 SeilaplanPlugin
                                 A QGIS plugin
 Seilkran-Layoutplaner
                              -------------------
        begin                : 2013
        copyright            : (C) 2015 by ETH Zürich
        email                : seilaplanplugin@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import (Qt, QObject, QAbstractTableModel, QModelIndex,
                              pyqtSignal)
from qgis.PyQt.QtGui import (QColor, QBrush, QStandardItem, QStandardItemModel,
                             QIcon, QPixmap)


class AdjustmentDialogThresholds(QObject):
    
    COLOR_ERROR = QColor(224, 103, 103)
    COLOR_NEUTRAL = QColor(255, 255, 255)
    
    sig_clickedRow = pyqtSignal(int)
    
    def __init__(self, parent, datasetSize):
        """
        :type parent: gui.adjustmentDialog.AdjustmentDialog
        """
        super().__init__()
        self.parent = parent
        self.tbl = self.parent.tableThresholds
        self.model = QStandardItemModel(datasetSize[0], datasetSize[1], self.tbl)
        self.initState = True
        self.thresholdExeeded = False
        self.tbl.setModel(self.model)
        self.tbl.resizeColumnsToContents()
        self.tbl.resizeRowsToContents()
        # Icons
        self.iconOk = QIcon()
        self.iconOk.addPixmap(
            QPixmap(":/plugins/SeilaplanPlugin/gui/icons/icon_green.png"),
            QIcon.Normal, QIcon.Off)
        self.iconErr = QIcon()
        self.iconErr.addPixmap(
            QPixmap(":/plugins/SeilaplanPlugin/gui/icons/icon_exclamation.png"),
            QIcon.Normal, QIcon.Off)

        self.tbl.clicked.connect(self.onClick)
    
    def populate(self, header, dataset, valueColumn):
        self.model.setHorizontalHeaderLabels(header)
        self.tbl.hideColumn(4)
        
        # Insert data into cells
        for i, row in enumerate(dataset):
            for j, cell in enumerate(row):
                if j < 4:
                    item = QStandardItem(cell)
                    self.model.setItem(i, j, item)
                # Set background color for cells where threshold is exceeded
                if j == 4 and len(cell) != 0:
                    self.colorBackground(i, valueColumn, self.COLOR_ERROR)
        
        # Adjust column widths
        self.tbl.resizeColumnsToContents()
        self.tbl.setColumnWidth(0, 300)
        for idx in range(1, self.model.columnCount()):
            currSize = self.tbl.sizeHintForColumn(idx)
            self.tbl.setColumnWidth(idx, max(currSize, 90))
        self.tbl.resizeRowsToContents()
        self.updateTabIcon()
    
    def updateData(self, row, col, newVal):
        # Update background color of new values
        if col == 4:
            newVal = len(newVal)
            color = self.COLOR_NEUTRAL
            if newVal != 0:
                color = self.COLOR_ERROR
            self.colorBackground(row, 3, color)
        # Update value itself
        self.model.setData(self.model.index(row, col), newVal)
        self.updateTabIcon()

        # Remove the background color from initially calculated
        # cable line data
        if self.initState:
            self.initState = False
            for row in range(self.model.rowCount()):
                self.colorBackground(row, 2, self.COLOR_NEUTRAL)
    
    def colorBackground(self, row, col, color):
        self.model.setData(self.model.index(row, col),
                           QBrush(color), Qt.BackgroundRole)
    
    def updateTabIcon(self):
        """ Updates icon of QTabWidget with an exclamation mark or check
        mark depending on presents of exceeded thresholds."""
        thresholdExceeded = False
        for i in range(0, 5):
            data = self.model.data(self.model.index(i, 4))
            if data and data > 0:
                thresholdExceeded = True
                break
        if thresholdExceeded:
            self.parent.tabWidget.setTabIcon(2, self.iconErr)
        else:
            self.parent.tabWidget.setTabIcon(2, self.iconOk)
    
    def onClick(self, item):
        # Row is already selected
        if self.parent.selectedThresholdRow == item.row():
            # Deselect
            self.tbl.clearSelection()
        # Emit select signal
        self.sig_clickedRow.emit(item.row())


class ThresholdTblModel(QAbstractTableModel):
    
    def __init__(self, dataset, header, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dataset = dataset
        self.header = header
    
    def rowCount(self, index=QModelIndex()):
        return len(self.dataset)
    
    def columnCount(self, index=QModelIndex()):
        return len(self.header)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.dataset[index.row()][index.column()]
        if role == Qt.BackgroundColorRole:
            return QBrush(Qt.red)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter
        else:
            return None
    
    def headerData(self, col, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role."""
        if role != Qt.EditRole and role != Qt.BackgroundColorRole:
            return False
        
        if index.isValid() and 0 <= index.row() < len(self.dataset) \
                and 0 <= index.column() < len(self.header):

            self.dataset[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
