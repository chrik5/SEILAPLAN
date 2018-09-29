# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SeilaplanPluginDialog
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
import re
from operator import itemgetter
import unicodedata
from math import atan, pi

# GUI and QGIS libraries
from qgis.PyQt.QtCore import QSettings, QFileInfo, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QAction, QMessageBox, QFileDialog
from qgis.PyQt.QtGui import QIcon, QColor, QPixmap
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsGeometry, QgsPoint, \
    QgsPointXY, QgsFeature, QgsProject
from qgis.gui import QgsRubberBand
from processing import run

# Further GUI modules for functionality
from .gui.guiHelperFunctions import Raster, valueToIdx, QgsStueMarker, \
    strToNum, DialogOutputOptions, generateName, DialogWithImage, formatNum, \
    readFromTxt, castToNumber
from .bo.ptmaptool import ProfiletoolMapTool
from .bo.createProfile import CreateProfile
# GUI elements
from .gui.ui_seilaplanDialog import Ui_Dialog
from .gui.profileDialog import ProfileWindow


# UTF-8 coding
# try:
#     utf8 = QString.fromUtf8
# except AttributeError:
#     utf8 = lambda s: s

# OS dependent line break
nl = os.linesep

# Source of icons in GUI
greenIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
            'icons/icon_green.png"/></p></body></html>'
yellowIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
             'icons/icon_yellow.png"/></p></body></html>'
redIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
          'icons/icon_red.png"/></p></body></html>'
# Text next to coord status
greenTxt = ''
yellowTxt = 'zu definieren'
redTxt = 'ausserhalb Raster'

# Titles of info images
infImg = {'Bodenabstand': u'Erklärungen zum Bodenabstand',
          'VerankerungA': u'Erklärungen zur Verankerung am Anfangspunkt',
          'VerankerungE': u'Erklärungen zur Verankerung am Anfangspunkt',
          'Stuetzen': u'Erklärungen zu den Zwischenstützen'}

# Info button text
infoTxt = ("SEILAPLAN - Seilkran-Layoutplaner\n\n"
    "SEILAPLAN berechnet auf Grund eines digitalen Höhenmodells zwischen "
    "definierten Anfangs- und Endkoordinaten sowie technischen Parametern das "
    "optimale Seillinienlayout. Es werden Position und Höhe der Stütze,"
    "sowie die wichtigsten Kennwerte der Seillinie bestimmt.\n\n"
    "Realisierung:\nProfessur für forstliches Ingenieurwesen\n"
    "ETH Zürich\n8092 Zürich\n\nBeteiligte Personen:\n"
    "Leo Bont (Konzept, Mechanik)\nPatricia Moll "
    "(Implementation in Python / QGIS)\n\n"
    "SEILAPLAN ist freie Software: Sie können sie unter den Bedingungen "
    "der GNU General Public License, wie von der Free Software Foundation, "
    "Version 2 der Lizenz oder (nach Ihrer Wahl) jeder neueren "
    "veröffentlichten Version, weiterverbreiten und/oder modifizieren.\n")


class SeilaplanPluginDialog(QDialog, Ui_Dialog):
    def __init__(self, interface, helper):
        QDialog.__init__(self, interface.mainWindow())
        # import pydevd
        # pydevd.settrace('localhost', port=53100,
        #             stdoutToServer=True, stderrToServer=True)

        # QGIS interface
        self.iface = interface
        # QGIS map canvas
        self.canvas = self.iface.mapCanvas()
        self.action = QAction(
            QIcon(":/plugins/SeilaplanPlugin/icons/icon_app.png"),
            "SEILAPLAN", self.iface.mainWindow())
        self.action.setWhatsThis("SEILAPLAN")
        # Separate class to start algorithm
        self.threadingControl = helper
        # Interaction with canvas, is used to draw onto map canvas
        self.tool = ProfiletoolMapTool(self.canvas, self.action)
        self.savedTool = self.canvas.mapTool()
        # Setup GUI of SEILAPLAN (import from ui_seilaplanDialog.py)
        self.setupUi(self)

        # Define some important paths and locations
        self.userHomePath = os.path.join(os.path.expanduser('~'))
        self.homePath = os.path.dirname(__file__)
        # Config file 'params.txt' stores parameters of cable types
        self.paramPath = os.path.join(self.homePath, 'config', 'params.txt')
        # Config file 'commonPaths.txt' stores previous output folders
        self.commonPathsFile = os.path.join(self.homePath, 'config',
                                            'commonPaths.txt')
        self.commonPaths, outputOpt = self.createCommonPathList()
        # Get the preferences for output options
        self.outputOpt = {'outputPath': self.commonPaths[-1],   # last used output path
                          'report': outputOpt[0],
                          'plot': outputOpt[1],
                          'geodata': outputOpt[2],
                          'coords': outputOpt[3]}

        # Initialize cable parameters
        self.param = None               # All parameters of a certain cable type
        self.paramOrder = None          # Order of parameters
        self.header = None
        self.paramSet = None            # Name of cable type
        self.settingFields = {}         # Dictionary of all GUI setting fields

        # GUI fields and variables handling coordinate information
        self.coordFields = {}
        self.pointA = [-100, -100]
        self.pointE = [-100, -100]
        self.azimut = 0
        self.coordStateA = 'yellow'
        self.coordStateE = 'yellow'
        self.groupFields()

        # Dictionary containing information about selected elevation model
        self.dhm = {}
        # User defined fixed intermediate support
        self.fixStue = {}

        # Dialog with explanatory images
        self.imgBox = DialogWithImage(self.iface)

        # Variables handling additional GIS-Layers
        self.osmLayer = None            # OpenStreetMap Layer (TileMapService)
        self.osmLyrOn = False
        self.osmLyrButton.setEnabled(False)
        self.contourLyrButton.setEnabled(False)     # Contour Layer
        self.contourLyr = None
        self.contourLyrOn = False

        # Connect signals and slots
        self.connectFields()
        self.buttonShowProf.setEnabled(False)

        # Initialize variables handling drawing on map
        self.draw.setEnabled(False)
        self.polygon = False
        # Drawn line
        self.rubberband = QgsRubberBand(self.canvas, self.polygon)
        self.rubberband.setWidth(3)
        self.rubberband.setColor(QColor(231, 28, 35))
        self.markers = []           # Point markers on each end of the line
        self.pointsToDraw = []
        self.dblclktemp = None
        self.drawnLine = None
        self.line = False
        self.lineLyr = None
        self.vl = None
        self.lineID = None

        # Dialog window with height profile
        self.profileWin = None
        # Dialog windows with output options
        self.optionWin = DialogOutputOptions(self.iface, self)
        self.optionWin.fillInDropDown(self.commonPaths)


    def connectFields(self):
        """Connect GUI fields.
        """
        self.buttonOkCancel.rejected.connect(self.Reject)
        self.buttonOkCancel.accepted.connect(self.apply)
        self.buttonOpenPr.clicked.connect(self.onLoadProjects)
        self.buttonSavePr.clicked.connect(self.onSaveProjects)
        self.rasterField.currentIndexChanged.connect(self.setRaster)
        self.buttonRefreshRa.clicked.connect(self.updateRasterList)
        self.buttonInfo.clicked.connect(self.onInfo)
        self.buttonOptionen.clicked.connect(self.onShowOutputOpt)
        
        # Info buttons
        self.infoBodenabstand.clicked.connect(self.onShowInfoImg)
        self.infoVerankerungA.clicked.connect(self.onShowInfoImg)
        self.infoVerankerungE.clicked.connect(self.onShowInfoImg)
        self.infoStuetzen.clicked.connect(self.onShowInfoImg)
        
        # OSM map and contour buttons
        self.osmLyrButton.clicked.connect(self.onClickOsmButton)
        self.contourLyrButton.clicked.connect(self.onClickContourButton)

        self.fieldProjName.textChanged.connect(self.setProjName)
        self.draw.clicked.connect(self.drawLine)
        self.buttonShowProf.clicked.connect(self.onShowProfile)
        self.fieldParamSet.currentIndexChanged.connect(self.setParamSet)

        # Action for changed Coordinates (when coordinate is changed by hand)
        self.coordAx.editingFinished.connect(self.changedPointAField)
        self.coordAy.editingFinished.connect(self.changedPointAField)
        self.coordEx.editingFinished.connect(self.changedPointEField)
        self.coordEy.editingFinished.connect(self.changedPointEField)



    def groupFields(self):
        """Combine all GUI fields in dictionary for faster access.
        """
        self.settingFields = {'Q': self.fieldQ,
                              'qT': self.fieldQt,
                              'A': self.fieldA,
                              'E': self.fieldE,
                              'zul_SK': self.fieldzulSK,
                              'min_SK': self.fieldminSK,
                              'qz1': self.fieldqz1,
                              'qz2': self.fieldqz2,
                              'Bodenabst_min': self.fieldBabstMin,
                              'Bodenabst_A': self.fieldBabstA,
                              'Bodenabst_E': self.fieldBabstE,
                              'GravSK': self.fieldGravSK,
                              'Befahr_A': self.fieldBefA,
                              'Befahr_E': self.fieldBefE,
                              'HM_Anfang': self.fieldHManf,
                              'd_Anker_A': self.fieldDAnkA,
                              'HM_Ende_min': self.fieldHMeMin,
                              'HM_Ende_max': self.fieldHMeMax,
                              'd_Anker_E': self.fieldDAnkE,
                              'Min_Dist_Mast': self.fieldMinDist,
                              'L_Delta': self.fieldLdelta,
                              'N_Zw_Mast_max': self.fieldNzwSt,
                              'HM_min': self.fieldHMmin,
                              'HM_max': self.fieldHMmax,
                              'HM_Delta': self.fieldHMdelta,
                              'HM_nat': self.fieldHMnat}
        self.coordFields = {'Ax': self.coordAx,
                            'Ay': self.coordAy,
                            'Ex': self.coordEx,
                            'Ey': self.coordEy}

    def loadInitialVals(self):
        """Some initial values are filled into the GUI fields.
        """
        # Load existing parameter sets of cable types
        [self.param, self.header] = readFromTxt(self.paramPath)
        avaSets = []
        for item in self.header:
            if item[:4] == 'set_':
                avaSets.append(item.replace('set_', '', 1))
        self.fieldParamSet.blockSignals(True)
        for i in range(self.fieldParamSet.count()):
            self.fieldParamSet.removeItem(i)
        self.fieldParamSet.addItems(avaSets)
        # self.fieldParamSet.setCurrentIndex(-1)
        self.fieldParamSet.blockSignals(False)
        # Generate project name
        self.fieldProjName.setText(generateName())
        self.enableToolTips()

    def enableToolTips(self):
        for [name, field] in list(self.settingFields.items()):
            try:
                field.setToolTip(self.param[name]['tooltip'])
            except KeyError:
                # If parameter is not present on GUI, ignore
                pass

    def setParamSet(self, idx):
        setName = self.fieldParamSet.currentText()
        self.paramSet = 'set_' + setName
        # Fill in values of parameter set
        self.fillInValues(self.param, self.paramSet)

    def fillInValues(self, data, datafield):
        """Fills in GUI fields with parameters of a certain cable type.
        """
        for name, field in list(self.settingFields.items()):
            val = data[name][datafield]
            if self.param[name]['ftype'] == 'drop_field':
                field.setCurrentIndex(valueToIdx(val))
                continue
            # Float values without decimal places are converted: 10.0 --> 10
            if val[-2:] == '.0':
                val = val[:-2]
            if val == '-':
                val = ''
            field.setText(val)

    def updateRasterList(self):
        rasterlist = self.getAvailableRaster()
        self.addRastersToGui(rasterlist)

    def getAvailableRaster(self):
        """Go trough table of content and collect all raster layers.
        """
        availLayers = QgsProject.instance().mapLayers().values()
        rColl = []

        for lyr in availLayers:
            # TODO: Nur auswählen, falls im TOC aktiviert / sichtbar
            # if legend.isLayerVisible(lyr):
            lyrType = lyr.type()
            if lyrType == 1:        # = raster
                lyrName = lyr.name()
                r = Raster(lyr.id(), lyrName, lyr)
                rColl.append(r)
        return rColl

    def addRastersToGui(self, rasterList):
        """Put list of raster layers into drop down menu of self.rasterField.
        If raster name contains some kind of "DHM", select it.
        """
        for i in reversed(list(range(self.rasterField.count()))):
            self.rasterField.removeItem(i)
        idx = None
        searchStr = ['dhm', 'Dhm', 'DHM', 'dtm', 'DTM', 'Dtm']
        for i, rLyr in enumerate(rasterList):
            self.rasterField.addItem(rLyr.name)
            if not idx and sum([item in rLyr.name for item in searchStr]) > 0:
                idx = i
        # Set an elevation model as current selection
        if idx and idx >= 0:
            self.rasterField.setCurrentIndex(idx)
        # If a raster was added to the drop down menu, get raster information
        if not self.rasterField.currentText() == '':
            self.setRaster(self.rasterField.currentText())
            self.draw.setEnabled(True)

    def setRaster(self, rastername):
        """Get the current selected Raster in self.rasterField and collect
        useful information about it.
        """
        rasterlist = self.getAvailableRaster()
        for rlyr in rasterlist:
            if rlyr.name == rastername:
                path = rlyr.grid.dataProvider().dataSourceUri()
                spatialRef = rlyr.grid.crs().authid()
                ext = rlyr.grid.extent()
                self.dhm['name'] = rastername
                self.dhm['path'] = path
                self.dhm['layer'] = rlyr.grid
                self.dhm['ncols'] = rlyr.grid.width()
                self.dhm['nrows'] = rlyr.grid.height()
                self.dhm['cellsize'] = float(rlyr.grid.rasterUnitsPerPixelX())
                self.dhm['spatialRef'] = spatialRef
                self.dhm['extent'] = [ext.xMinimum(),
                                      ext.yMaximum(),
                                      ext.xMaximum(),
                                      ext.yMinimum()]
                # Contour Layer is calculated on demand
                self.dhm['contour'] = None
        # If a raster was selected, OSM and Contour Layers can be generated
        self.osmLyrButton.setEnabled(True)
        self.contourLyrButton.setEnabled(True)

    def searchForRaster(self, path):
        """ Checks if a raster from a saved project is present in the table
        of content or exists at the given location (path).
        """
        rasterFound = False
        availRaster = self.getAvailableRaster()
        for rlyr in availRaster:
            lyrPath = rlyr.grid.dataProvider().dataSourceUri()
            if lyrPath == path:
                self.setRaster(rlyr.name)
                rasterFound = True
                self.setCorrectRasterInField(rlyr.name)
                break
        if not rasterFound:
            if os.path.exists(path):
                baseName = QFileInfo(path).baseName()
                rlayer = QgsRasterLayer(path, baseName)
                QgsProject.instance().addMapLayer(rlayer)
                self.updateRasterList()
                self.setCorrectRasterInField(baseName)
                self.setRaster(baseName)
                self.draw.setEnabled(True)
            else:
                txt = "Raster mit dem Pfad {} ist " \
                      "nicht vorhanden".format(path)
                title = "Fehler beim Laden des Rasters"
                QMessageBox.information(self, title, txt)

    def setCorrectRasterInField(self, rasterName):
        for idx in range(self.rasterField.count()):
            if rasterName == self.rasterField.itemText(idx):
                self.rasterField.setCurrentIndex(idx)
                self.draw.setEnabled(True)
                break

    def createCommonPathList(self):
        """Gets the output options and earlier used output paths from the file
        'commonPaths.txt' an returns them.
        """
        commonPaths = []
        homePathPresent = False
        # Standard values for when the file is defect or no file is present
        #   [report, plot, shape-files, coordinate tables]
        outputOpt = [1, 1, 0, 0]
        # Output is  saved in home directory when output path is not defined
        userPath = os.path.join(self.userHomePath, 'Seilaplan')

        if os.path.exists(self.commonPathsFile):
            with io.open(self.commonPathsFile, encoding='utf-8') as f:
                lines = f.read().splitlines()
                # First line contains output options
                try:
                    outputOpt = lines[0].split()
                    outputOpt = [int(x) for x in outputOpt]
                except IndexError:    # if file/fist line is empty
                    pass
                except ValueError:    # if there are letters instead of numbers
                    pass
                # Go through paths from most recent to oldest
                for path in lines[1:]:
                    try:
                        if path == '': continue
                        if os.path.exists(path):   # If path still exists
                            if path == userPath:
                                homePathPresent = True
                            commonPaths.append(path)
                    except:
                        continue

        if not homePathPresent:  # If current user path is not present
            if not os.path.exists(userPath):
                os.mkdir(userPath)
            commonPaths.append(userPath)
        # Delete duplicates in list
        unique = []
        [unique.append(item) for item in commonPaths if item not in unique]
        commonPaths = unique
        # Maximum length of drop down menu is 12 entries
        if len(commonPaths) > 12:
            del commonPaths[0]      # Delete oldest entry
        return commonPaths, outputOpt

    def updateCommonPathList(self, newPath):
        """Updates the list of common paths so that the current selected
        path is first in the list.
        """
        dublicateIdx = None
        # Checks if path already exists
        for idx, path in enumerate(self.commonPaths):
            if newPath == path:
                dublicateIdx = idx
                break
        # Adds entry
        if os.path.exists(newPath):
            self.commonPaths.append(newPath)
        # If a duplicate is present, it gets removed
        if dublicateIdx+1:
            del self.commonPaths[dublicateIdx]
        if len(self.commonPaths) > 12:
            # Firs (=oldest) entry is removed
            del self.commonPaths[0]

    def updateCommonPathFile(self):
        """File 'commonPaths.txt' is updated.
        """
        if os.path.exists(self.commonPathsFile):
            os.remove(self.commonPathsFile)
        with io.open(self.commonPathsFile, encoding='utf-8', mode='w+') as f:
            f.writelines("{} {} {} {} {}".format(self.outputOpt['report'],
                    self.outputOpt['plot'], self.outputOpt['geodata'],
                    self.outputOpt['coords'], nl))
            for path in self.commonPaths:
                f.writelines(path + nl)

    def setProjName(self, projname):
        self.projName = projname

    # TODO Unset Focus of field when clicking on something else, doesnt work yet
    # def mousePressEvent(self, event):
    #     focused_widget = QtGui.QApplication.focusWidget()
    #     if isinstance(focused_widget, QtGui.QLineEdit):
    #         focused_widget.clearFocus()
    #     QtGui.QDialog.mousePressEvent(self, event)


    ###########################################################################
    ### Methods for drawing line on map canvas
    ###########################################################################

    def drawLine(self):
        self.dblclktemp = None
        self.clearMap()
        self.rubberband.reset(self.polygon)
        self.cleanDigi()
        self.activateDigiTool()
        self.canvas.setMapTool(self.tool)

    def clearMap(self):
        if self.profileWin:
            self.profileWin.deactivateMapMarker()
            self.profileWin.removeLines()
            del self.profileWin
            self.profileWin = None
        self.removeStueMarker()

    def createDigiFeature(self, pnts):
        line = QgsGeometry.fromPolyline(pnts)
        qgFeat = QgsFeature()
        qgFeat.setGeometry(line)
        return qgFeat

    def lineFinished(self):
        lastPoint = self.pointsToDraw[-1]
        if len(self.pointsToDraw) < 2:
            self.removeStueMarker()
            self.cleanDigi()
            self.pointsToDraw = []
            self.dblclktemp = lastPoint
            self.drawnLine = None
            self.buttonShowProf.setEnabled(False)
        self.drawnLine = self.createDigiFeature(self.pointsToDraw)
        self.changeCoordA(self.pointsToDraw[0])
        self.changeCoordE(self.pointsToDraw[1])
        self.createProfile()
        self.cleanDigi()
        self.dblclktemp = lastPoint

    def lineFromFields(self):
        self.dblclktemp = None
        self.rubberband.reset(self.polygon)
        lastPoint = self.pointsToDraw[-1]
        if self.coordStateA == self.coordStateE == 'green':
            self.buttonShowProf.setEnabled(True)
        else:
            self.buttonShowProf.setEnabled(False)
        self.pointsToDraw = []
        self.dblclktemp = lastPoint

    def drawStueMarker(self, point):
        marker = QgsStueMarker(self.canvas)
        marker.setCenter(QgsPointXY(point))
        self.markers.append(marker)
        self.canvas.refresh()

    def removeStueMarker(self, position=None):
        if position:
            marker = self.markers[position]
            self.canvas.scene().removeItem(marker)
            self.markers.pop(position)
        else:
            for marker in self.markers:
                self.canvas.scene().removeItem(marker)
            self.markers = []
        self.canvas.refresh()

    def cleanDigi(self):
        self.pointsToDraw = []
        self.canvas.unsetMapTool(self.tool)     # Signal DEACTIVATE is sent
        self.canvas.setMapTool(self.savedTool)

    def activateDigiTool(self):
        # self.tool.canvasMoveEvent.connect(self.moved)
        # self.tool.rightClicked.connect(self.rightClicked)
        # self.tool.leftClicked.connect(self.leftClicked)
        # self.tool.doubleClicked.connect(self.doubleClicked)
        # self.tool.deactivate.connect(self.deactivateDigiTool)
        return

    def deactivateDigiTool(self):
        # self.tool.moved.disconnect(self.moved)
        # self.tool.leftClicked.disconnect(self.leftClicked)
        # self.tool.rightClicked.disconnect(self.rightClicked)
        # self.tool.doubleClicked.disconnect(self.doubleClicked)
        return

    def moved(self, position):
        if len(self.pointsToDraw) > 0:
            mapPos = self.canvas.getCoordinateTransform().\
                toMapCoordinates(position["x"], position["y"])
            self.rubberband.reset(self.polygon)
            newPnt = QgsPoint(mapPos.x(), mapPos.y())
            # if QGis.QGIS_VERSION_INT < 10900:
            #     for i in range(0, len(self.pointsToDraw)):
            #         self.rubberband.addPoint(self.pointsToDraw[i])
            #     self.rubberband.addPoint(newPnt)
            # else:
            pnts = self.pointsToDraw + [newPnt]
            self.rubberband.setToGeometry(QgsGeometry.fromPolyline(pnts), None)

    def rightClicked(self, position):
        # Reroute signal, it doesn't matter which mouse button is clicked
        self.leftClicked(position)

    def leftClicked(self, position):
        mapPos = self.canvas.getCoordinateTransform().\
            toMapCoordinates(position["x"], position["y"])
        newPoint = QgsPoint(mapPos.x(), mapPos.y())
        if newPoint == self.dblclktemp:
            self.dblclktemp = None
            return
        else:
            # Mark point with marker symbol
            self.drawStueMarker(newPoint)
            if len(self.pointsToDraw) == 0:
                self.rubberband.reset(self.polygon)
                self.pointsToDraw.append(newPoint)
            else:
                self.pointsToDraw.append(newPoint)
                self.lineFinished()

    def doubleClicked(self, position):
        pass

    ###########################################################################
    ### Methods handling start and end point coordinates
    ###########################################################################

    def changedPointAField(self):
        x = strToNum(self.coordFields['Ax'].text())
        y = strToNum(self.coordFields['Ay'].text())
        # Only do something if coordinates have changed
        if not (x == self.pointA[0] and y == self.pointA[1]):
            self.changeCoordA([x, y])
            self.updateLineFromGui()

    def changedPointEField(self):
        x = strToNum(self.coordFields['Ex'].text())
        y = strToNum(self.coordFields['Ey'].text())
        # Only do something if coordinates have changed
        if not (x == self.pointE[0] and y == self.pointE[1]):
            self.changeCoordE([x, y])
            self.updateLineFromGui()

    def changeCoordA(self, newpoint):
        # Delete fixed intermediate support from previous cable line
        self.fixStue = {}
        # Check if point is inside elevation model
        state = self.checkPoint(newpoint)
        self.coordStateA = state
        # Update coordinate state icon
        self.changePointSym(state, 'A')
        if state != 'yellow':
            # Update coordinate field
            self.coordFields['Ax'].setText(formatNum(newpoint[0]))
            self.coordFields['Ay'].setText(formatNum(newpoint[1]))
            self.pointA = newpoint
            self.setAzimut()
        # Update profile and length fields
        self.checkProfileStatus()
        self.checkLenghtStatus()

    def changeCoordE(self, newpoint):
        # Delete fixed intermediate support from previous cable line
        self.fixStue = {}
        # Check if point is inside elevation model
        state = self.checkPoint(newpoint)
        self.coordStateE = state
        # Update coordinate state icon
        self.changePointSym(state, 'E')
        if state != 'yellow':
            # Update coordinate field
            self.coordFields['Ex'].setText(formatNum(newpoint[0]))
            self.coordFields['Ey'].setText(formatNum(newpoint[1]))
            self.pointE = newpoint
            self.setAzimut()
        # Update profile and length fields
        self.checkProfileStatus()
        self.checkLenghtStatus()

    def setAzimut(self):
        dx = (self.pointE[0] - self.pointA[0]) * 1.0
        dy = (self.pointE[1] - self.pointA[1]) * 1.0
        if dx == 0:
            dx = 0.0001
        azimut = atan(dy/dx)
        if dx > 0:
            azimut += 2 * pi
        else:
            azimut += pi
        self.azimut = azimut

    def checkLenghtStatus(self):
        if self.coordStateA != 'yellow' and self.coordStateE != 'yellow':
            self.updateLenghtField(self.pointA, self.pointE)
        else:
            self.laenge.setText('')

    def checkProfileStatus(self):
        if self.coordStateA == self.coordStateE == 'green':
            self.buttonShowProf.setEnabled(True)
        else:
            self.buttonShowProf.setEnabled(False)

    def updateLenghtField(self, pointA, pointE):
        [Ax, Ay] = pointA
        [Ex, Ey] = pointE
        l = ((Ex - Ax)**2 + (Ey - Ay)**2)**0.5
        self.laenge.setText(formatNum(l))

    def updateLineFromGui(self):
        self.rubberband.reset(self.polygon)
        if self.coordStateA != 'yellow' and self.coordStateE != 'yellow':
            points = [QgsPoint(self.pointA[0], self.pointA[1]),
                      QgsPoint(self.pointE[0], self.pointE[1])]
            self.rubberband.setToGeometry(QgsGeometry.fromPolyline(points), None)
            self.drawnLine = self.createDigiFeature(points)
            self.clearMap()
            self.drawStueMarker(points[0])
            self.drawStueMarker(points[1])
            # TODO: Pofileerstellung funktioniert nicht wegen fehlendem package shapely
            # self.createProfile()
        else:
            self.clearMap()

    def checkPoint(self, point):
        state = 'yellow'
        if self.dhm != {}:
            extent = self.dhm['extent']
            [extLx, extHy, extHx, extLy] = extent
            try:
                [x, y] = point
                if extLx <= float(x) <= extHx and extLy <= float(y) <= extHy:
                    state = 'green'
                else:
                    state = 'red'
            except ValueError:
                state = 'yellow'
        return state

    def changePointSym(self, state, point):
        if point == 'A':
            if state == 'green':
                self.symA.setText(greenIcon)
                self.symTxtA.setText(greenTxt)
            if state == 'yellow':
                self.symA.setText(yellowIcon)
                self.symTxtA.setText(yellowTxt)
            if state == 'red':
                self.symA.setText(redIcon)
                self.symTxtA.setText(redTxt)
        if point == 'E':
            if state == 'green':
                self.symE.setText(greenIcon)
                self.symTxtE.setText(greenTxt)
            if state == 'yellow':
                self.symE.setText(yellowIcon)
                self.symTxtE.setText(yellowTxt)
            if state == 'red':
                self.symE.setText(redIcon)
                self.symTxtE.setText(redTxt)

    def removeCoords(self):
        for field in list(self.coordFields.values()):
            field.setText('')

    def transform2MapCoords(self, dist):
        import math
        x = self.pointA[0] + dist * math.cos(self.azimut)
        y = self.pointA[1] + dist * math.sin(self.azimut)
        return [x, y]


    ###########################################################################
    ### Methods for adding additional layer
    ###########################################################################

    def onClickOsmButton(self):
        """ Load OpenStreetMap Layer to canvas.
        """
        self.osmLyrOn = False
        # Check if there is already an OSM layer
        legend = self.iface.legendInterface()
        availLayers = legend.layers()
        for lyr in availLayers:
            if lyr.name() == 'OSM_Karte':
                self.osmLayer = lyr
                self.osmLyrOn = True
                break

        if self.osmLyrOn:
            # Remove OSM layer
            QgsProject.instance().removeMapLayer(self.osmLayer.id())
            self.osmLyrOn = False
        else:
            # Add OSM layer
            xmlPath = os.path.join(self.homePath, 'config', 'OSM_Karte.xml')
            baseName = QFileInfo(xmlPath).baseName()
            self.osmLayer = QgsRasterLayer(xmlPath, baseName)
            QgsProject.instance().addMapLayer(self.osmLayer)
            self.osmLyrOn = True

    def onClickContourButton(self):
        # Get current CRS of qgis project
        s = QSettings()
        oldValidation = s.value("/Projections/defaultBehaviour")
        crs = self.canvas.mapSettings().destinationCrs()
        crsEPSG = crs.authid()
        # If project and raster CRS are equal and set correctly
        if crsEPSG == self.dhm['spatialRef'] and "USER" not in crsEPSG:
            s.setValue("/Projections/defaultBehaviour", "useProject")
        else:
            crs = self.dhm['layer'].crs()

        contourLyr = self.dhm['contour']
        if contourLyr:
            QgsProject.instance().removeMapLayer(contourLyr.id())
        else:
            algOutput = run("gdalogr:contour", self.dhm['layer'],
                                          20.0, "Hoehe", None, None)
            contourPath = algOutput['OUTPUT_VECTOR']
            contourName = "Hoehenlinien_" + self.dhm['name']
            contour = QgsVectorLayer(contourPath, contourName, "ogr")
            # Set the same CRS as qgis project
            contour.setCrs(crs)
            QgsProject.instance().addMapLayer(contour)
            self.dhm['contour'] = contour
            s.setValue("/Projections/defaultBehaviour", oldValidation)

        # More useful stuff
        # uri = "linestring?crs=epsg:{}".format(crsNum)
        # contourName = "Hoehenlinien_" + self.dhm['name']
        # contour = QgsVectorLayer(uri, contourName,  "memory")

    ###########################################################################
    ### Methods for loading and saving projects
    ###########################################################################

    def createProfile(self):
        createProf = CreateProfile(self.iface, self.drawnLine, self.dhm['layer'])
        profile = createProf.create()
        self.profileWin = ProfileWindow(self, self.iface, profile[0])

    def onShowProfile(self):
        if not self.profileWin:
            self.createProfile()
        self.profileWin.show()

    def onLoadProjects(self):
        title = 'Projekt laden'
        fFilter = 'Txt Dateien (*.txt)'
        filename, __ = QFileDialog.getOpenFileName(self, title,
                                        self.outputOpt['outputPath'], fFilter)
        if filename:
            self.loadProj(filename)
        else:
            return False

    def loadProj(self, path):
        # Read project data from file
        projHeader, projData  = self.openProjFromTxt(path)
        # Set project data
        self.setProjName(projHeader['Projektname'])
        self.searchForRaster(projHeader['Hoehenmodell'])
        # Update coordinates
        pointA = projHeader['Anfangspunkt'].split('/')
        pointE = projHeader['Endpunkt'].split('/')
        self.changeCoordA([strToNum(pointA[0]), strToNum(pointA[1])])
        self.changeCoordE([strToNum(pointE[0]), strToNum(pointE[1])])
        self.updateLineFromGui()
        # Set the correct parameter set name in drop down menu
        self.fieldParamSet.blockSignals(True)
        idx = self.fieldParamSet.findText(projHeader['Parameterset'])
        self.fieldParamSet.setCurrentIndex(idx)
        self.fieldParamSet.blockSignals(False)

        # Extract and update data of fixed intermediate support
        fixStueString = projHeader['Fixe Stuetzen'].split('/')[:-1]
        for stue in fixStueString:
            [key, values] = stue.split(':')
            [posX, posY, posH] = [string.strip() for string in values.split(',')]
            self.fixStue[int(key)] = [posX, posY, posH]
        self.fieldProjName.setText(self.projName)
        # Fill in parameter values
        self.fillInValues(projData, 'Wert')
        self.createProfile()

    def onSaveProjects(self):
        title = 'Projekt speichern'
        fFilter = 'TXT (*.txt)'
        dialog = QFileDialog(self, title, self.outputOpt['outputPath'])
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter(fFilter)
        dialog.setDefaultSuffix('txt')
        if self.projName != '':
            defaultFilename = u'{}.txt'.format(self.projName)
            dialog.selectFile(defaultFilename)
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            fileExtention = u'.txt'
            if filename[-4:] != fileExtention:
                filename += fileExtention
            self.saveProjToTxt(filename)
        else:
            return False

    def saveProjToTxt(self, path):
        # Extract field data
        noError, userData, projInfo = self.verifyFieldData()
        if not noError:
            # If there where invalid values
            return False
        if not self.paramOrder:
            # Get the order of the parameter values for the output
            self.getParamOrder()
        # Extract project data (project name, elevation model...)
        _, fileheader = self.getProjectInfo(userData)
        if os.path.exists(path):
            os.remove(path)
        with io.open(path, encoding='utf-8', mode='w+') as f:
            # Write header
            f.writelines(fileheader)
            # Write parameter values
            for name, sortNr in self.paramOrder:
                try:
                    d = userData[name][0]
                except KeyError:
                    continue
                p = self.param[name]

                line = '{0: <17}{1: <12}{2: <45}{3: <9}{4}'.format(name, d, p['label'], p['unit'], '\n')
                f.writelines(line)

    def openProjFromTxt(self, path):
        """Opens a saved project and saves it to a dictionary.
        """
        fileData = {}
        projInfo = {}
        if os.path.exists(path):
            with io.open(path, encoding='utf-8') as f:
                lines = f.read().splitlines()
                for hLine in lines[:6]:
                    # Dictionary keys cant be in unicode
                    name = hLine[:17].rstrip()
                    projInfo[name] = hLine[17:]
                for line in lines[11:]:
                    if line == '': break
                    line = re.split(r'\s{2,}', line)
                    if line[1] == '-':
                        line[1] = ''
                    key = line[0]
                    fileData[key] = {'Wert': line[1]}
            return projInfo, fileData
        else:
            return False, False

    def onInfo(self):
        QMessageBox.information(self, "SEILAPLAN Info", infoTxt,
                                QMessageBox.Ok)

    def getParamOrder(self):
        """Get order of parameters to layout them correctly for the output
        report.
        """
        orderList = []
        for name, d in list(self.param.items()):
            orderList.append([name, int(d['sort'])])
        self.paramOrder = sorted(orderList, key=itemgetter(1))

    def onShowInfoImg(self):
        sender = self.sender().objectName()
        infoType = sender[4:]
        infoTitle = infImg[infoType]
        imgPath = os.path.join(self.homePath, 'img', infoType + '.png')
        self.imgBox.setWindowTitle(infoTitle)
        # Load image
        myPixmap = QPixmap(imgPath)
        self.imgBox.label.setPixmap(myPixmap)
        self.imgBox.setLayout(self.imgBox.container)
        self.imgBox.show()

    def onShowOutputOpt(self):
        self.optionWin.show()

    ###########################################################################
    ### Methods for extracting and checking GUI field values
    ###########################################################################

    def verifyFieldData(self):
        fieldData = self.getFieldValues()
        userData = {}
        errTxt = []
        finalErrorState = True
        errorCount = 0
        for name, d in list(self.param.items()):
            if d['ftype'] ==  'no_field':
                val = d['std_val']
            else:
                val = fieldData[name]
            # Check value type
            cval, errState  = castToNumber(val, d['dtype'])
            if errState:
                errTxt.append("-->Der Wert '{}' im Feld '{}' ist ungültig. "
                              "Bitte geben Sie eine korrekte "
                              "Zahl ein.".format(val, d['label']))
                finalErrorState = False
                errorCount += 1
                continue
            # Check value range
            if d['ftype'] not in ['drop_field', 'no_field']:
                result, [rMin, rMax] = self.checkValues(cval, d['dtype'],
                                                        d['min'],d['max'])
                # Additional check for special fields
                ankerError = False
                if name == 'd_Anker_A':
                    if int(fieldData['HM_Anfang']) == 0:
                        ankerError = True
                if name == 'd_Anker_E':
                    if int(fieldData['HM_Ende_max']) == 0:
                        ankerError = True
                if ankerError:
                    errTxt.append("--> Der Wert '{}' im Feld '{}' ist "
                                  "ungültig. Anker können nur definiert "
                                  "werden, wenn die entsprechende Stütze "
                                  "höher als 0 Meter ist.".format(cval,
                                                        d['label']))
                    finalErrorState = False
                if result is False:
                    errTxt.append("--> Der Wert '{}' im Feld '{}' ist "
                                  "ungültig. Bitte wählen Sie einen Wert "
                                  "zwischen {} und {} {}.".format(cval,
                                   d['label'], rMin, rMax, d['unit']))
                    finalErrorState = False
                    continue
            # If there was no error value is saved to dictionary
            userData[name] = [cval, d['label'], d['unit'], d['sort']]


        # Show dialog window with error messages
        if finalErrorState is False:
            errorMsg = "Es wurden folgende Fehler gefunden:" + nl
            errorMsg += nl.join(errTxt)
            if errorCount >= 10:
                errorMsg = "Bitte definieren Sie einen Parametersatz."
            QMessageBox.information(self, 'Fehler', errorMsg, QMessageBox.Ok)
            return finalErrorState, {}, {}

        # Get general project info
        try:
            projInfo, projHeader = self.getProjectInfo(userData)
        except:
            return False, False, False
        projInfo['header'] = projHeader

        return finalErrorState, userData, projInfo

    def getFieldValues(self):
        """Read out values from GUI fields.
        """
        fieldData = {}

        for name, field in list(self.settingFields.items()):
            d = self.param[name]
            if d['ftype'] == 'drop_field':
                val = field.currentText()
            else:
                val = field.text()
            if val == '':
                val = '-'
            fieldData[name] = val
        return fieldData

    def checkValues(self, val, dtype, rangeMin, rangeMax):
        """Checks field data for correct range.
        """
        rangeSet = []
        for rangeItem in [rangeMin, rangeMax]:
            try:
                # If range is a variable name
                if any(c.isalpha() for c in rangeItem):
                    # Read out value of variable name
                    rangeSet.append(float(self.settingFields[rangeItem].text()))
                else:
                    if dtype == 'float':
                        rangeSet.append(float(rangeItem))
                    else:   # dtype = int
                        rangeSet.append(int(rangeItem))
            except ValueError:
                return False, [None, None]
        # Check range
        if rangeSet[0] <= val <= rangeSet[1]:
            return True, rangeSet
        else:
            return False, rangeSet

    def getProjectInfo(self, userData):
        Ax = strToNum(self.coordAx.text())
        Ay = strToNum(self.coordAy.text())
        Ex = strToNum(self.coordEx.text())
        Ey = strToNum(self.coordEy.text())
        # Checks if predefine parameter data has been changed by the user or not
        parameterSet = self.checkParamSet(userData)
        noStue = []
        if self.profileWin:
            noStue = self.profileWin.sc.getNoStue()
        projInfo = {'Projektname': self.projName,
                    'Hoehenmodell': self.dhm,
                    'Anfangspunkt': [Ax, Ay],
                    'Endpunkt': [Ex, Ey],
                    'Laenge': self.laenge.text(),
                    'fixeStuetzen': self.fixStue,
                    'keineStuetzen': noStue,
                    'Parameterset': parameterSet}
        # Layout project data
        projHeader = ''
        coord = []
        for i in [Ax, Ay, Ex, Ey]:
            val = formatNum(i)
            coord.append(val)

        info = [['Projektname', projInfo['Projektname']],
                ['Hoehenmodell', '{}'. format(self.dhm['path'])],
                ['Anfangspunkt', '{0: >7} / {1: >7}'.format(*tuple(coord[:2]))],
                ['Endpunkt', '{0: >7} / {1: >7}'.format(*tuple(coord[2:]))],
                ['Parameterset', parameterSet]]
                # TODO: save cable line sections that shouldn't contain
                # TODO:     intermediate support
        fixStueString = ''
        for key, values in list(self.fixStue.items()):
                fixStueString += '{0:0>2}: {1: >7}, {2: >7}, ' \
                                 '{3: >4}  /  '.format(key, *tuple(values))
        info.append(['Fixe Stuetzen', fixStueString])

        for title, txt in info:
            line = '{0: <17}{1}'.format(title, txt)
            projHeader += line + '\n'
        paramHeader = '{5}{5}{0}{5}{1: <17}{2: <12}{3: <45}{4: <9}' \
                      '{5:-<84}{5}'.format('Parameter:', 'Name', 'Wert',
                                            'Label', 'Einheit', '\n')
        projHeader += paramHeader
        return projInfo, projHeader

    def layoutToolParams(self, fieldData):
        """ """
        if not self.paramOrder:
            self.getParamOrder()
        txt = []
        for name, sortNr in self.paramOrder:
            try:
                value = str(fieldData[name][0])
            except KeyError:
                continue
            p = self.param[name]
            # Shorten whole-numbered floats
            if value[-2:] == '.0':
                value = value[:-2]
            # Combine values and units
            if p['unit']:
                value += " {}".format(p['unit'])
            line = [p['label'], value]
            txt.append(line)
        return txt

    def getStueInfo(self, userData):
        userData['HM_fix_d'] = []
        userData['HM_fix_h'] = []
        userData['noStue'] = []
        if self.fixStue:
            for [pointX, _, pointH] in self.fixStue.values():
                userData['HM_fix_d'].append(int(pointX))
                userData['HM_fix_h'].append(int(pointH))
        if self.profileWin:
            userData['noStue'] = self.profileWin.sc.getNoStue()
        return userData

    def checkParamSet(self, userData):
        """ Checks if the user has changed parameter data. If yes, the
        parameter set changes to 'user defined'. This information is used to
        write it (1) to a saved project (2) to the drop down menu when a
        project is opened.
        """
        paramName = 'benutzerdefiniert'
        valChanged = False

        if self.paramSet:
            for name, row in list(self.param.items()):
                if row['ftype'] == 'no_field':
                    continue
                # Special treatment for drop down value
                if name == 'GravSK':
                    setVal = valueToIdx(row[self.paramSet])
                    userVal = valueToIdx(userData[name][0])
                else:
                    setVal = float(row[self.paramSet])
                    userVal = userData[name][0]
                if setVal != userVal:
                    valChanged = True
                    break
            if not valChanged:
                paramName = self.paramSet
        return paramName


    ###########################################################################
    ### Methods for OK and Cancel Button
    ###########################################################################

    def apply(self):
        # ERSETZEN mit PICKLE

        # # Extract values from GUI fields
        # noError, userData, projInfo = self.verifyFieldData()
        # if noError:
        #     self.threadingControl.setState(True)
        # else:
        #     # If there was an error extracting the values, return to GUI
        #     return False
        #
        # # Project data gets layout for report generation
        # projInfo['Params'] = self.layoutToolParams(userData)
        # projInfo['outputOpt'] = self.outputOpt
        # # Project data is saved to reload it later
        # projInfo['projFile'] = os.path.join(projInfo['outputOpt']['outputPath'],
        #                                     self.projName + '_Projekt.txt')
        # self.saveProjToTxt(projInfo['projFile'])
        # # Save fixed intermediate supports
        # userData = self.getStueInfo(userData)
        #


        picklefile = '20180923_1145.pckl'

        # import pickle
        # homePath = os.path.dirname(__file__)
        # storefile = os.path.join(homePath, 'backups+testFiles', picklefile)
        # projInfo['Hoehenmodell'].pop('layer')
        # f = open(storefile, 'wb')
        # pickle.dump([userData, projInfo], f)
        # f.close()

        import pickle
        homePath = os.path.dirname(__file__)
        storefile = os.path.join(homePath, 'backups+testFiles',
                                 '{}'.format(picklefile))
        f = open(storefile, 'rb')
        dump = pickle.load(f)
        f.close()
        [userData, projInfo] = dump
        self.threadingControl.setState(True)
        
        
        
        # All user data is handed over to class that handles calculation
        self.threadingControl.setValue(userData, projInfo)
        self.close()

    def cleanUp(self):
        self.removeCoords()
        # Clean markers and lines from map canvas
        self.clearMap()
        self.rubberband.reset(self.polygon)
        self.drawnLine = None
        self.cleanDigi()
        # Close additional dialogs
        self.imgBox.close()
        if self.profileWin:
            self.profileWin.close()
        self.updateCommonPathFile()
        self.optionWin.close()

    def Reject(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        self.cleanUp()

