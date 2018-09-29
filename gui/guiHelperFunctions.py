# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SeilaplanPlugin
                                 A QGIS plugin
 Seilkran-Layoutplaner
                              -------------------
        begin                : 2013
        copyright            : (C) 2015 by ETH Zürich
        email                : pi1402@gmail.com
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
import os
import io

from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget, QLabel, QDialogButtonBox, \
    QLayout, QHBoxLayout, QComboBox, QSizePolicy, QPushButton, QCheckBox, \
    QVBoxLayout, QFileDialog
from qgis.PyQt.QtGui import QColor, QIcon, QPixmap
from qgis.gui import QgsVertexMarker


class Raster(object):
    def __init__(self, ide, name, grid):
        self.id = ide
        self.name = name
        self.grid = grid
        self.selected = False


class DialogWithImage(QDialog):
    def __init__(self, interface):
        QDialog.__init__(self, interface.mainWindow())
        self.iface = interface
        self.main_widget = QWidget(self)
        self.main_widget.setMinimumSize(QSize(100, 100))
        self.label = QLabel()
        self.buttonBox = QDialogButtonBox(self.main_widget)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.Apply)
        # Access the layout of the MessageBox to add the checkbox
        self.container = QVBoxLayout(self.main_widget)
        self.container.addWidget(self.label)
        self.container.addWidget(self.buttonBox)
        self.container.setAlignment(Qt.AlignCenter)
        self.container.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.container)

    def Apply(self):
        self.close()


class QgsStueMarker(QgsVertexMarker):
    def __init__(self, canvas):
        QgsVertexMarker.__init__(self, canvas)
        self.setColor(QColor(1, 1, 213))
        self.setIconType(QgsVertexMarker.ICON_BOX)
        self.setIconSize(11)
        self.setPenWidth(3)


class QgsMovingCross(QgsVertexMarker):
    def __init__(self, canvas):
        QgsVertexMarker.__init__(self, canvas)
        self.setColor(QColor(27, 25, 255))
        self.setIconType(QgsVertexMarker.ICON_CROSS)
        self.setIconSize(20)
        self.setPenWidth(3)


class DialogOutputOptions(QDialog):
    def __init__(self, interface, toolWindow):
        QDialog.__init__(self, interface.mainWindow())
        self.iface = interface
        self.tool = toolWindow
        self.setWindowTitle("Output Optionen")
        self.main_widget = QWidget(self)

        # Build up gui
        self.hbox = QHBoxLayout()
        self.saveLabel = QLabel("Speicherpfad")
        self.pathField = QComboBox()
        self.pathField.setMinimumWidth(400)
        self.pathField.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding,
                              QSizePolicy.Fixed))
        self.openButton = QPushButton()
        self.openButton.setMaximumSize(QSize(27, 27))
        icon = QIcon()
        iconPath = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                'icons', 'icon_open.png')
        icon.addPixmap(QPixmap(iconPath), QIcon.Normal,
                       QIcon.Off)
        self.openButton.setIcon(icon)
        self.openButton.setIconSize(QSize(24, 24))
        self.openButton.clicked.connect(self.onOpenDialog)

        self.hbox.addWidget(self.saveLabel)
        self.hbox.addWidget(self.pathField)
        self.hbox.addWidget(self.openButton)
        # Create checkboxes
        self.questionLabel = \
            QLabel(u"Welche Produkte sollen erzeugt werden?")
        self.checkBoxReport = QCheckBox(u"Technischer Bericht")
        self.checkBoxPlot = QCheckBox(u"Diagramm")
        self.checkBoxGeodata = \
            QCheckBox(u"Shape-Daten der Stützen und Seillinie")
        self.checkBoxCoords = \
            QCheckBox(u"Koordinaten-Tabellen der Stützen und Seillinie")
        # Set tick correctly
        self.checkBoxReport.setChecked(self.tool.outputOpt['report'])
        self.checkBoxPlot.setChecked(self.tool.outputOpt['plot'])
        self.checkBoxGeodata.setChecked(self.tool.outputOpt['geodata'])
        self.checkBoxCoords.setChecked(self.tool.outputOpt['coords'])
        # Create Ok/Cancel Button and connect signal
        self.buttonBox = QDialogButtonBox(self.main_widget)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.Apply)
        self.buttonBox.rejected.connect(self.Reject)
        # Layout
        self.container = QVBoxLayout(self.main_widget)
        self.container.addLayout(self.hbox)
        self.container.addWidget(QLabel(""))
        self.container.addWidget(self.questionLabel)
        self.container.addWidget(self.checkBoxReport)
        self.container.addWidget(self.checkBoxPlot)
        self.container.addWidget(self.checkBoxGeodata)
        self.container.addWidget(self.checkBoxCoords)
        self.container.addWidget(self.buttonBox)
        self.container.setAlignment(Qt.AlignLeft)
        self.setLayout(self.container)

    def fillInDropDown(self, pathList):
        for i in reversed(range(self.pathField.count())):
            self.pathField.removeItem(i)
        for path in reversed(pathList):
            self.pathField.addItem(path)

    def onOpenDialog(self):
        title = u"Output Pfad auswählen"
        directory = QFileDialog.getExistingDirectory(self, title,
                                            self.tool.outputOpt['outputPath'])
        self.tool.updateCommonPathList(directory)
        self.fillInDropDown(self.tool.commonPaths)

    def Apply(self):
        # Save checkbox status
        self.tool.outputOpt['outputPath'] = self.pathField.currentText()
        self.tool.outputOpt['report'] = int(self.checkBoxReport.isChecked())
        self.tool.outputOpt['plot'] = int(self.checkBoxPlot.isChecked())
        self.tool.outputOpt['geodata'] = int(self.checkBoxGeodata.isChecked())
        self.tool.outputOpt['coords'] = int(self.checkBoxCoords.isChecked())

        # Update output location with currently selected path
        self.tool.updateCommonPathList(self.pathField.currentText())
        self.close()

    def Reject(self):
        self.close()


def readFromTxt(path):
    """Generic Method to read a txt file with header information and save it
    to a dictionary. The keys of the dictionary are the header items.
    """
    fileData = {}
    if os.path.exists(path):
        with io.open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
            header = lines[0].split('\t')
            for line in lines[1:]:
                if line == '': break
                line = line.split('\t')
                row = {}
                for i in range(1, len(header)):
                    row[header[i]] = line[i]
                key = line[0]
                fileData[key] = row
        return fileData, header
    else:
        return False, False


def strToNum(coord):
    """ Convert string to number by removing the ' sign.
    """
    try:
        num = int(coord.replace("'", ''))
    except ValueError:
        num = ''
    return num


def generateName():
    """ Generate a unique project name.
    """
    import time
    now = time.time()
    timestamp = time.strftime("%d.%m_%H'%M", time.localtime(now))
    name = "seilaplan_{}".format(timestamp)
    return name


def valueToIdx(val):
    if val == 'ja':
        return 0
    else:
        return 1


def formatNum(number):
    """ Layout Coordinates with thousand markers.
    """
    roundNum = int(round(number))
    strNum = str(roundNum)
    if roundNum > 999:
        b, c = divmod(roundNum, 1000)
        if b > 999:
            a, b = divmod(b, 1000)
            strNum = "{:0d}'{:0>3n}'{:0>3n}".format(a, b, c)
        else:
            strNum = "{:0n}'{:0>3n}".format(b, c)
    return strNum


def castToNumber(val, dtype):
    errState = None
    try:
        if dtype == 'string':
            cval = val
            # result = True
        elif dtype == 'float':
            cval = float(val)
        else:
            cval = int(val)
    except ValueError:
        cval = None
        errState = True
    return cval, errState