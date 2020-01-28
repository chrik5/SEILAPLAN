# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SeilaplanPluginDialog
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

import os

# GUI and QGIS libraries
from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog, QComboBox
from qgis.PyQt.QtGui import QPixmap
from qgis.core import (QgsRasterLayer, QgsPointXY, QgsProject,
                       QgsCoordinateReferenceSystem)
from processing.core.Processing import Processing

# Further GUI modules for functionality
from .gui.guiHelperFunctions import (DialogWithImage, createContours,
                                     loadOsmLayer, createProfileLayers)
from .configHandler import ConfigHandler, castToNum
# GUI elements
from .gui.saveDialog import DialogSaveParamset
from .gui.mapMarker import MapMarkerTool
from .gui.ui_seilaplanDialog import Ui_SeilaplanDialog
from .gui.profileDialog import ProfileDialog

# OS dependent line break
nl = os.linesep

# Source of icons in GUI
greenIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
            'gui/icons/icon_green.png"/></p></body></html>'
yellowIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
             'gui/icons/icon_yellow.png"/></p></body></html>'
redIcon = '<html><head/><body><p><img src=":/plugins/SeilaplanPlugin/' \
          'gui/icons/icon_red.png"/></p></body></html>'
# Text next to coord status
greenTxt = ''
yellowTxt = 'zu definieren'
redTxt = 'ausserhalb Raster'

# Titles of info images
infImg = {'Bodenabstand': 'Erklärungen zum Bodenabstand',
          'VerankerungA': 'Erklärungen zur Verankerung am Anfangspunkt',
          'VerankerungE': 'Erklärungen zur Verankerung am Anfangspunkt',
          'Stuetzen': 'Erklärungen zu den Zwischenstützen'}

# Info button text
infoTxt = ("SEILAPLAN - Seilkran-Layoutplaner\n\n"
           "SEILAPLAN berechnet auf Grund eines digitalen Höhenmodells zwischen "
           "definierten Anfangs- und Endkoordinaten sowie technischen Parametern das "
           "optimale Seillinienlayout. Es werden Position und Höhe der Stütze,"
           "sowie die wichtigsten Kennwerte der Seillinie bestimmt.\n\n"
           "Realisierung:\n\nProfessur für forstliches Ingenieurwesen\n"
           "ETH Zürich\n8092 Zürich\n(Konzept, Realisierung Version 1.x für QGIS 2)\n\n"
           "Gruppe Forstliche Produktionssysteme FPS\n"
           "Eidgenössische Forschungsanstalt WSL\n"
           "8903 Birmensdorf\n(Realisierung Version 2.x für QGIS 3)\n\n"
           "\nBeteiligte Personen:\n\n"
           "Leo Bont, Hans Rudolf Heinimann (Konzept, Mechanik)\nPatricia Moll "
           "(Implementation in Python / QGIS)\n\n\n"
           "SEILAPLAN ist freie Software: Sie können sie unter den Bedingungen "
           "der GNU General Public License, wie von der Free Software Foundation, "
           "Version 2 der Lizenz oder (nach Ihrer Wahl) jeder neueren "
           "veröffentlichten Version, weiterverbreiten und/oder modifizieren."
           "\n\nPfad zu Dokumentation:\n"
           + os.path.join(os.path.dirname(__file__), 'help', 'docs') + '\n')


class SeilaplanPluginDialog(QDialog, Ui_SeilaplanDialog):
    def __init__(self, interface, confHandler):
        """

        :type confHandler: ConfigHandler
        """
        QDialog.__init__(self, interface.mainWindow())
        
        # QGIS interface
        self.iface = interface
        # QGIS map canvas
        self.canvas = self.iface.mapCanvas()
        # Management of Parameters and settings
        self.confHandler = confHandler
        self.confHandler.setDialog(self)
        self.paramHandler = confHandler.params
        self.projectHandler = confHandler.project
        self.startAlgorithm = False
        self.goToAdjustment = False
        self.homePath = os.path.dirname(__file__)
        
        # Setup GUI of SEILAPLAN (import from ui_seilaplanDialog.py)
        self.setupUi(self)
        
        # Interaction with canvas, is used to draw onto map canvas
        self.drawTool = MapMarkerTool(self.canvas)
        # Connect emitted signals
        self.drawTool.sig_lineFinished.connect(self.onFinishedLineDraw)
        # Survey data line layer
        self.surveyLineLayer = None
        self.surveyPointLayer = None
        
        # Dictionary of all GUI setting fields
        self.parameterFields = {}
        
        # GUI fields and variables handling coordinate information
        self.coordFields = {}
        self.linePoints = {
            'A': QgsPointXY(-100, -100),
            'E': QgsPointXY(-100, -100)
        }
        
        # Organize parameter GUI fields in dictionary
        self.groupFields()
        self.enableToolTips()
        
        # Dialog with explanatory images
        self.imgBox = DialogWithImage()
        
        # Additional GIS-Layers
        self.osmLyrButton.setEnabled(False)
        self.contourLyrButton.setEnabled(False)
        
        # Connect GUI elements from dialog window with functions
        self.connectGuiElements()
        
        # Dialog window with height profile
        self.profileWin = ProfileDialog(self, self.iface, self.drawTool,
                                        self.projectHandler)

        # Dialog windows for saving parameter and cable sets
        self.paramSetWindow = DialogSaveParamset(self)

        # Set initial sate of some buttons
        # Choosing height data
        self.enableRasterHeightSource()
        # Button to show profile
        self.buttonShowProf.setEnabled(False)
        # Button that activates drawing on map
        self.draw.setEnabled(False)
        # Button stays down when pressed
        self.draw.setCheckable(True)
        
        Processing.initialize()
    
    def connectGuiElements(self):
        """Connect GUI elements with functions.
        """
        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonRun.clicked.connect(self.apply)
        self.btnAdjustment.clicked.connect(self.goToAdjustmentWindow)
        self.buttonOpenPr.clicked.connect(self.onLoadProjects)
        self.buttonSavePr.clicked.connect(self.onSaveProject)
        self.rasterField.currentTextChanged.connect(self.onChangeRaster)
        self.buttonRefreshRa.clicked.connect(self.updateRasterList)
        self.buttonInfo.clicked.connect(self.onInfo)

        self.radioRaster.toggled.connect(self.onToggleHeightSource)
        self.radioSurveyData.toggled.connect(self.onToggleHeightSource)
        self.buttonLoadSurveyData.clicked.connect(self.onLoadSurveyData)
        
        self.fieldTypeA.currentTextChanged.connect(self.onTypeAChange)
        self.fieldTypeE.currentTextChanged.connect(self.onTypeEChange)
        
        # Info buttons
        self.infoRasterlayer.clicked.connect(self.onHeightDataInfoShow)
        self.infoSurveyData.clicked.connect(self.onHeightDataInfoShow)
        self.infoPointA.clicked.connect(self.onPointAInfoShow)
        self.infoPointE.clicked.connect(self.onPointEInfoShow)
        self.infoBodenabstand.clicked.connect(self.onShowInfoImg)
        self.infoStuetzen.clicked.connect(self.onShowInfoImg)
        self.infoFieldE.clicked.connect(self.onShowInfoFieldE)
        self.infoFieldSFT.clicked.connect(self.onShowInfoFieldSFT)
        
        # OSM map and contour buttons
        self.osmLyrButton.clicked.connect(self.onClickOsmButton)
        self.contourLyrButton.clicked.connect(self.onClickContourButton)
        
        # Filed that contains project names
        self.fieldProjName.textChanged.connect(self.setProjName)
        # Button starts map drawing
        self.draw.clicked.connect(self.drawLine)
        # Button shows profile window
        self.buttonShowProf.clicked.connect(self.onShowProfile)
        # Drop down field for parameter set choices
        self.fieldParamSet.currentIndexChanged.connect(self.setParameterSet)
        self.buttonSaveParamset.clicked.connect(self.onSaveParameterSet)
        
        # Action for changed Coordinates (when coordinate is changed by hand)
        self.coordAx.editingFinished.connect(
            lambda: self.onCoordFieldChange('A'))
        self.coordAy.editingFinished.connect(
            lambda: self.onCoordFieldChange('A'))
        self.coordEx.editingFinished.connect(
            lambda: self.onCoordFieldChange('E'))
        self.coordEy.editingFinished.connect(
            lambda: self.onCoordFieldChange('E'))
        
        for name, inputField in self.parameterFields.items():
            # lambda definition is put in its own function "getListener" to
            # preserve scope, otherwise var "name" gets overwritten in every
            # iteration of this loop
            if isinstance(inputField, QComboBox) and name == 'Seilsys':
                inputField.currentIndexChanged.connect(
                    self.getListenerComboBox(name))
            else:
                inputField.editingFinished.connect(
                    self.getListenerLineEdit(name))
    
    def groupFields(self):
        """Combine all GUI fields in dictionary for faster access.
        """
        self.parameterFields = {
            'Seilsys': self.fieldSeilsys,
            'HM_Kran': self.fieldHMKran,
            'Befahr_A': self.fieldBefA,
            'Befahr_E': self.fieldBefE,
            'Bodenabst_min': self.fieldBabstMin,
            'Bodenabst_A': self.fieldBabstA,
            'Bodenabst_E': self.fieldBabstE,
            
            'Q': self.fieldQ,
            'qT': self.fieldQt,
            'A': self.fieldA,
            'MBK': self.fieldMBK,
            'qZ': self.fieldqZ,
            'qR': self.fieldqR,
            
            'Min_Dist_Mast': self.fieldMinDist,
            'L_Delta': self.fieldLdelta,
            'HM_min': self.fieldHMmin,
            'HM_max': self.fieldHMmax,
            'HM_Delta': self.fieldHMdelta,
            'HM_nat': self.fieldHMnat,
            'min_SK': self.fieldminSK,
            
            'E': self.fieldE,
            'SF_T': self.fieldSFT
        }
        self.coordFields = {
            'Ax': self.coordAx,
            'Ay': self.coordAy,
            'Ex': self.coordEx,
            'Ey': self.coordEy
        }
    
    def onToggleHeightSource(self):
        if self.radioRaster.isChecked():
            self.enableRasterHeightSource()
        else:
            self.enableSurveyDataHeightSource()
        # Reset profile data
        self.projectHandler.resetProfile()
        self.drawTool.surveyDataMode = False
        self.removeSurveyDataLayer()
        self.checkPoints()
    
    def enableRasterHeightSource(self):
        if not self.radioRaster.isChecked():
            self.radioRaster.blockSignals(True)
            self.radioSurveyData.blockSignals(True)
            self.radioRaster.setChecked(True)
            self.radioRaster.blockSignals(False)
            self.radioSurveyData.blockSignals(False)
        self.fieldSurveyDataPath.setText('')
        self.rasterField.setEnabled(True)
        self.buttonRefreshRa.setEnabled(True)
        self.fieldSurveyDataPath.setEnabled(False)
        self.buttonLoadSurveyData.setEnabled(False)

    def enableSurveyDataHeightSource(self):
        if not self.radioSurveyData.isChecked():
            self.radioRaster.blockSignals(True)
            self.radioSurveyData.blockSignals(True)
            self.radioSurveyData.setChecked(True)
            self.radioRaster.blockSignals(False)
            self.radioSurveyData.blockSignals(False)
        self.rasterField.setCurrentIndex(-1)
        self.rasterField.setEnabled(False)
        self.buttonRefreshRa.setEnabled(False)
        self.fieldSurveyDataPath.setEnabled(True)
        self.buttonLoadSurveyData.setEnabled(True)

    def getListenerLineEdit(self, property_name):
        return lambda: self.parameterChangedLineEdit(property_name)
    
    def getListenerComboBox(self, property_name):
        return lambda: self.parameterChangedComboBox(property_name)
    
    def parameterChangedLineEdit(self, property_name):
        # Deactivate editFinished signal so it is not fired twice when
        # setParameter() shows a QMessageBox
        self.parameterFields[property_name].blockSignals(True)
        newVal = self.parameterFields[property_name].text()
        newValAsStr = self.paramHandler.setParameter(property_name, newVal)
        if newValAsStr is not False:
            self.updateParametersetField()
            # Insert correctly formatted value
            self.parameterFields[property_name].setText(newValAsStr)
        self.parameterFields[property_name].blockSignals(False)
    
    def parameterChangedComboBox(self, property_name):
        newVal = self.parameterFields[property_name].currentIndex()
        newValAsIdx = self.paramHandler.setParameter(property_name, newVal)
        if newValAsIdx is not False:
            self.updateParametersetField()
    
    def updateParametersetField(self):
        # Change current parameter set name
        if self.paramHandler.currentSetName:
            self.fieldParamSet.setCurrentText(self.paramHandler.currentSetName)
        else:
            self.fieldParamSet.setCurrentIndex(-1)
    
    def setupContentForFirstRun(self):
        # Generate project name
        self.fieldProjName.setText(self.projectHandler.generateProjectName())
        # Check QGIS table of content for raster layer
        rasterlist = self.updateRasterList()
        # Select first raster that has the word "dhm" in it, else select first
        # layer
        dhm = self.searchForDhm(rasterlist)
        if dhm:
            self.setRaster(dhm)
            self.checkPoints()
        
        # Load all predefined and user-defined parameter sets from the
        # config folder
        parameterSetNames = self.paramHandler.getParametersetNames()
        # Add set names to drop down
        self.fieldParamSet.blockSignals(True)
        self.fieldParamSet.addItems(parameterSetNames)
        self.fieldParamSet.blockSignals(False)
        # Set standard parameter set
        self.paramHandler.setParameterSet(self.paramHandler.DEFAULTSET)
        self.fieldParamSet.setCurrentIndex(
            self.fieldParamSet.findText(self.paramHandler.DEFAULTSET))
        self.fillInValues()
        
        # Set point types
        self.fieldTypeA.setCurrentIndex(
            self.projectHandler.getPointTypeAsIdx('A'))
        self.fieldTypeE.setCurrentIndex(
            self.projectHandler.getPointTypeAsIdx('E'))
    
    def setupContent(self):
        self.startAlgorithm = False
        self.goToAdjustment = False
        # Generate project name
        self.fieldProjName.setText(self.projectHandler.getProjectName())
        
        if self.projectHandler.heightSourceType == 'dhm':
            # Enable gui elements
            self.enableRasterHeightSource()
            # Search raster and if necessary load it from disk
            rastername = self.searchForRaster(
                self.projectHandler.getHeightSourceAsStr())
            self.setRaster(rastername)
    
        elif self.projectHandler.heightSourceType == 'survey':
            # Enable gui elements
            self.enableSurveyDataHeightSource()
            # Show data on map and in gui
            self.loadSurveyData()
        
        # Update start and end point
        self.checkPoints()
        
        # Tell profile window to update its content on next show
        self.updateProfileWinContent()
        
        # Load all predefined and user-defined parameter sets from the
        # config folder (maybe a new set was added when project was opened)
        parameterSetNames = self.paramHandler.getParametersetNames()
        # Add set names to drop down
        self.fieldParamSet.blockSignals(True)
        self.fieldParamSet.clear()
        self.fieldParamSet.addItems(parameterSetNames)
        self.fieldParamSet.blockSignals(False)
        if self.paramHandler.currentSetName:
            self.fieldParamSet.setCurrentText(self.paramHandler.currentSetName)
        else:
            self.fieldParamSet.setCurrentIndex(-1)
        # Fill in parameter values
        self.fillInValues()

        # Set point types
        self.fieldTypeA.setCurrentIndex(
            self.projectHandler.getPointTypeAsIdx('A'))
        self.fieldTypeE.setCurrentIndex(
            self.projectHandler.getPointTypeAsIdx('E'))
    
    def enableToolTips(self):
        for field_name, field in list(self.parameterFields.items()):
            field.setToolTip(self.paramHandler.getParameterTooltip(field_name))
    
    def setParameterSet(self):
        name = self.fieldParamSet.currentText()
        if name:
            self.paramHandler.setParameterSet(name)
            # Fill in values of parameter set
            self.fillInValues()
    
    def fillInValues(self):
        """Fills parameter values into GUI fields."""
        for field_name, field in self.parameterFields.items():
            val = self.paramHandler.getParameterAsStr(field_name)
            if val:
                if isinstance(field, QComboBox):
                    val = self.paramHandler.getParameter(field_name)
                    field.setCurrentIndex(val)
                    continue
                
                field.setText(val)
    
    def onSaveParameterSet(self):
        if not self.paramHandler.checkValidState():
            return
        self.paramSetWindow.setData(self.paramHandler.getParametersetNames(),
                                    self.paramHandler.SETS_PATH)
        self.paramSetWindow.exec()
        setname = self.paramSetWindow.getNewSetname()
        if setname:
            self.paramHandler.saveParameterSet(setname)
            self.fieldParamSet.addItem(setname)
            self.fieldParamSet.setCurrentText(setname)
    
    def updateRasterList(self):
        rasterlist = self.getAvailableRaster()
        self.addRastersToDropDown(rasterlist)
        return rasterlist
    
    @staticmethod
    def getAvailableRaster():
        """Go trough table of content and collect all raster layers.
        """
        rColl = []
        for l in QgsProject.instance().layerTreeRoot().findLayers():
            lyr = l.layer()
            if lyr.type() == 1 and lyr.name() != 'OSM_Karte':  # = raster
                lyrName = lyr.name()
                r = {
                    'lyr': lyr,
                    'name': lyrName
                }
                rColl.append(r)
        return rColl
    
    def addRastersToDropDown(self, rasterList):
        """Put list of raster layers into drop down menu of self.rasterField.
        If raster name contains some kind of "DHM", select it.
        """
        self.rasterField.blockSignals(True)
        selectedRaster = self.rasterField.currentText()
        for i in reversed(list(range(self.rasterField.count()))):
            self.rasterField.removeItem(i)
        for rLyr in rasterList:
            self.rasterField.addItem(rLyr['name'])
        if selectedRaster != '' and selectedRaster in rasterList:
            self.rasterField.setCurrentText(selectedRaster)
        else:
            self.rasterField.setCurrentIndex(-1)
        self.rasterField.blockSignals(False)
    
    def searchForDhm(self, rasterlist):
        """ Search for a dhm to set as initial raster when the plugin is
        opened."""
        self.rasterField.blockSignals(True)
        dhmName = ''
        searchStr = ['dhm', 'Dhm', 'DHM', 'dtm', 'DTM', 'Dtm']
        for rLyr in rasterlist:
            if sum([item in rLyr['name'] for item in searchStr]) > 0:
                dhmName = rLyr['name']
                self.rasterField.setCurrentText(dhmName)
                break
        if not dhmName and len(rasterlist) > 0:
            dhmName = rasterlist[0]['name']
            self.rasterField.setCurrentText(dhmName)
        self.rasterField.blockSignals(False)
        return dhmName
    
    def onChangeRaster(self, rastername):
        """Triggered by choosing a raster from the drop down menu."""
        self.setRaster(rastername)
        # Update start and end point
        self.checkPoints()
    
    def setRaster(self, rastername):
        """Get the current selected Raster in self.rasterField and collect
        useful information about it.
        """
        rasterFound = False
        if isinstance(rastername, int):
            rastername = self.rasterField.currentText()
        rasterlist = self.getAvailableRaster()
        for rlyr in rasterlist:
            if rlyr['name'] == rastername:
                self.projectHandler.setHeightSource(rlyr['lyr'], 'dhm')
                # Check spatial reference of selected raster and show message
                if not self.checkEqualSpatialRef():
                    self.rasterField.blockSignals(True)
                    self.rasterField.setCurrentIndex(-1)
                    self.rasterField.blockSignals(False)
                    break
                self.iface.setActiveLayer(rlyr['lyr'])
                self.iface.zoomToActiveLayer()
                rasterFound = True
                break
        if not rasterFound:
            self.projectHandler.setHeightSource(None)
        
        # If a raster was selected, OSM and Contour Layers can be generated
        self.osmLyrButton.setEnabled(rasterFound)
        self.contourLyrButton.setEnabled(rasterFound)
        self.draw.setEnabled(rasterFound)
    
    def searchForRaster(self, path):
        """ Checks if a raster from a saved project is present in the table
        of content or exists at the given location (path).
        """
        availRaster = self.getAvailableRaster()
        rasterName = None
        self.rasterField.blockSignals(True)
        for rlyr in availRaster:
            lyrPath = rlyr['lyr'].dataProvider().dataSourceUri()
            # Raster has been loaded in QGIS project already
            if lyrPath == path:
                # Sets the dhm name in the drop down
                self.rasterField.setCurrentText(rlyr['name'])
                rasterName = rlyr['name']
                break
        if not rasterName:
            # Raster is still at same location in file system
            if os.path.exists(path):
                # Load raster
                rasterName = QFileInfo(path).baseName()
                rasterLyr = QgsRasterLayer(path, rasterName)
                QgsProject.instance().addMapLayer(rasterLyr)
                # Update drop down menu
                self.updateRasterList()
                self.rasterField.blockSignals(True)
                self.rasterField.setCurrentText(rasterName)
            else:
                self.rasterField.setCurrentIndex(-1)
                txt = f"Raster {path} nicht vorhanden"
                title = "Fehler beim Laden des Rasters"
                QMessageBox.information(self, title, txt)
        self.rasterField.blockSignals(False)
        return rasterName
    
    def checkEqualSpatialRef(self):
        # Check spatial reference of newly added raster
        heightSource = self.projectHandler.heightSource
        if not heightSource:
            return False
        hsType = self.projectHandler.heightSourceType
        mapCrs = self.canvas.mapSettings().destinationCrs()
        lyrCrs = heightSource.spatialRef
        title = 'Fehler Koordinatenbezugssystem (KBS)'
        msg = ''
        success = True
        
        # Height source has a different crs than map --> map crs is changed
        if lyrCrs.isValid() and not lyrCrs.isGeographic() and lyrCrs != mapCrs:
            self.canvas.setDestinationCrs(lyrCrs)
            self.canvas.refresh()
            return True
        
        # Height source is in a geographic crs
        elif lyrCrs.isValid() and lyrCrs.isGeographic():
            # Raster is in geographic coordinates --> automatic transformation
            # not possible
            if hsType == 'dhm':
                msg = (f"Raster mit geografischem KBS '{lyrCrs.description()}' "
                       f"({lyrCrs.authid()}) kann nicht benutzt werden. "
                       'Seilaplan kann Höhenraster nur verarbeiten wenn sie '
                       'in einem projizierten KBS vorliegen.')
                success = False
            # Survey data can be transformed to map crs
            elif hsType == 'survey' and not mapCrs.isGeographic():
                # Transform survey data to projected map coordinates
                heightSource.reprojectToCrs(mapCrs)
                msg = ('Felddaten liegen in einem geografischen KBS vor!\n\n'
                       'Seilaplan kann nur mit Daten in einem projizierten KBS '
                       'arbeiten. Die Daten werden automatisch in das QGIS Projekt-KBS '
                       f"'{mapCrs.description()}' ({mapCrs.authid()}) transformiert.")
                success = True
            
            elif hsType == 'survey' and mapCrs.isGeographic():
                # Transform to LV95 by default
                heightSource.reprojectToCrs(None)
                msg = ('Felddaten liegen in einem geografischen KBS vor!\n\n'
                       'Seilaplan kann nur mit Daten in einem projizierten '
                       'KBS arbeiten. Die Daten werden automatisch ins '
                       "Schweizer KBS 'LV95' (EPSG:2056) transformiert.")
                self.canvas.setDestinationCrs(heightSource.spatialRef)
                self.canvas.refresh()
                success = True
        
        elif not lyrCrs.isValid():
            if mapCrs.isGeographic():
                msg = ('Bezugssystem des Rasters unbekannt.\n\nDas Raster wird '
                       "im Schweizer KBS 'LV95' (EPSG:2056) dargestellt. Soll "
                       "ein anderes KBS benutzt werden, richten Sie ihr QGIS "
                       "Projekt bitte vor dem Laden der Höhendaten "
                       "entsprechend ein.")
                heightSource.spatialRef = QgsCoordinateReferenceSystem('EPSG:2056')
                self.canvas.setDestinationCrs(heightSource.spatialRef)
                self.canvas.refresh()
                success = True
            else:
                msg = ('Bezugssystem der Höhendaten unbekannt.\n\nEs wird '
                       'angenommen, dass die Daten dasselbe KBS wie das '
                       f"aktuelle QGIS-Projekt besitzen: "
                       f"{mapCrs.description()} ({mapCrs.authid()}).")
                heightSource.spatialRef = mapCrs
                success = True
        
        if msg:
            QMessageBox.information(self, title, msg)
        return success
    
    def onLoadSurveyData(self):
        title = 'Feldaufnahmen laden'
        fFilter = 'csv Dateien (*.csv *.CSV)'
        filename, _ = QFileDialog.getOpenFileName(self, title,
                self.confHandler.getCurrentPath(), fFilter)
        if filename:
            self.projectHandler.resetProfile()
            # Load data from csv file
            self.projectHandler.setHeightSource(None, 'survey', filename)
            self.loadSurveyData()
            self.checkPoints()
        else:
            return False
    
    def loadSurveyData(self):
        # Remove earlier survey data layer
        self.removeSurveyDataLayer()

        # Check the spatial reference and inform user if necessary
        if not self.checkEqualSpatialRef():
            self.projectHandler.setHeightSource(None)
            self.projectHandler.resetProfile()
        
        heightSource = self.projectHandler.heightSource
        if heightSource and heightSource.valid:
            # Create and add QGS layers of data to the map
            self.surveyLineLayer, \
                self.surveyPointLayer = createProfileLayers(heightSource)
            # Zoom to layer
            self.iface.setActiveLayer(self.surveyPointLayer)
            self.iface.zoomToActiveLayer()

            # Set path to csv in read only lineEdit
            self.fieldSurveyDataPath.setText(heightSource.getAsStr())
            # Activate draw tool
            self.drawTool.surveyDataMode = True
            self.draw.setEnabled(True)
            # Activate OSM button
            self.osmLyrButton.setEnabled(True)
        else:
            self.fieldSurveyDataPath.setText('')
            self.drawTool.surveyDataMode = False
            self.draw.setEnabled(False)
            self.osmLyrButton.setEnabled(False)
    
    def removeSurveyDataLayer(self):
        if self.surveyLineLayer:
            QgsProject.instance().removeMapLayer(self.surveyLineLayer.id())
            self.surveyLineLayer = None
        if self.surveyPointLayer:
            QgsProject.instance().removeMapLayer(self.surveyPointLayer.id())
            self.surveyPointLayer = None
    
    def setProjName(self, projname):
        self.projectHandler.setProjectName(projname)
    
    # TODO Unset Focus of field when clicking on something else, doesnt work yet
    # def mousePressEvent(self, event):
    #     focused_widget = QtGui.QApplication.focusWidget()
    #     if isinstance(focused_widget, QtGui.QLineEdit):
    #         focused_widget.clearFocus()
    #     QtGui.QDialog.mousePressEvent(self, event)

    def drawLine(self):
        if self.projectHandler.heightSourceType == 'dhm':
            self.drawTool.drawLine()
        elif self.projectHandler.heightSourceType == 'survey':
            self.drawTool.drawLine(self.projectToProfileLine)
    
    def projectToProfileLine(self, mapPosition):
        point = self.projectHandler.heightSource.projectPositionOnToLine(mapPosition)
        return QgsPointXY(point[0], point[1])
    
    def onCoordFieldChange(self, pointType):
        x = castToNum(self.coordFields[pointType + 'x'].text())
        y = castToNum(self.coordFields[pointType + 'y'].text())
        [x, y], coordState, hasChanged = self.projectHandler.setPoint(
            pointType, [x, y])
        if hasChanged:
            self.changePoint(pointType, [x, y], coordState)
            self.updateLineByCoordFields()
    
    def changePoint(self, pointType, coords, coordState):
        x = coords[0]
        y = coords[1]
        # Update profile line geometry
        if x and y:
            self.linePoints[pointType] = QgsPointXY(x, y)
        else:
            self.linePoints[pointType] = QgsPointXY(-100, -100)
        
        # Update coordinate state icon
        self.changePointSym(coordState[pointType], pointType)
        
        # Update coordinate field (formatted string)
        [xStr, yStr] = self.projectHandler.getPointAsStr(pointType)
        self.coordFields[pointType + 'x'].setText(xStr)
        self.coordFields[pointType + 'y'].setText(yStr)
        
        # Update profile button and profile length
        self.buttonShowProf.setEnabled(self.projectHandler.profileIsValid())
        self.laenge.setText(self.projectHandler.getProfileLenAsStr())
    
    def checkPoints(self):
        [Ax, Ay], coordState = self.projectHandler.getPoint('A')
        [Ex, Ey], coordState = self.projectHandler.getPoint('E')
        self.changePoint('A', [Ax, Ay], coordState)
        self.changePoint('E', [Ex, Ey], coordState)
        # Draw line
        self.updateLineByCoordFields()
    
    def updateLineByCoordFields(self):
        self.drawTool.reset()
        self.profileWin.doReset = True
        if self.projectHandler.profileIsValid():
            self.drawTool.updateLine(list(self.linePoints.values()))
    
    def updateLineByMapDraw(self, newpoint, pointType):
        [x, y], coordState, hasChanged = self.projectHandler.setPoint(
            pointType, [newpoint.x(), newpoint.y()])
        self.changePoint(pointType, [x, y], coordState)
    
    def changePointSym(self, state, point):
        if point == 'A':
            if state == 'green':
                self.symA.setText(greenIcon)
                self.symA.setToolTip(greenTxt)
            if state == 'yellow':
                self.symA.setText(yellowIcon)
                self.symA.setToolTip(yellowTxt)
            if state == 'red':
                self.symA.setText(redIcon)
                self.symA.setToolTip(redTxt)
        if point == 'E':
            if state == 'green':
                self.symE.setText(greenIcon)
                self.symE.setToolTip(greenTxt)
            if state == 'yellow':
                self.symE.setText(yellowIcon)
                self.symE.setToolTip(yellowTxt)
            if state == 'red':
                self.symE.setText(redIcon)
                self.symE.setToolTip(redTxt)
    
    def onClickOsmButton(self):
        """Add a OpenStreetMap layer."""
        loadOsmLayer(self.homePath)
        self.canvas.refresh()
    
    def onClickContourButton(self):
        """Calcluate contour lines from currently selected dhm and add them to
        as a layer."""
        if self.projectHandler.heightSource.contourLayer is None:
            createContours(self.canvas, self.projectHandler.heightSource)
    
    def onFinishedLineDraw(self, linecoord):
        self.projectHandler.resetProfile()
        self.updateLineByMapDraw(linecoord[0], 'A')
        self.updateLineByMapDraw(linecoord[1], 'E')
        # Stop pressing down button
        self.draw.setChecked(False)
    
    def updateProfileWinContent(self):
        profile = self.projectHandler.preparePreviewProfile()
        if profile:
            self.profileWin.setProfile(profile)
            self.profileWin.setPoleData(self.projectHandler.fixedPoles['poles'],
                                        self.projectHandler.noPoleSection)
    
    def onShowProfile(self):
        if not self.profileWin.dataSet:
            self.updateProfileWinContent()
        self.profileWin.exec()
    
    def onLoadProjects(self):
        title = 'Projekt laden'
        fFilter = 'Txt Dateien (*.txt)'
        filename, _ = QFileDialog.getOpenFileName(self, title,
                                                  self.confHandler.getCurrentPath(),
                                                  fFilter)
        if filename:
            success = self.confHandler.loadFromFile(filename)
            if success:
                self.setupContent()
            else:
                QMessageBox.critical(self, 'Fehler beim Laden',
                                'Projektdatei konnte nicht geladen werden.')
        else:
            return False
    
    def onSaveProject(self):
        title = 'Projekt speichern'
        fFilter = 'TXT (*.txt)'
        if not self.confHandler.checkValidState():
            return
        projname = self.projectHandler.getProjectName()
        defaultFilename = f'{projname}.txt'
        filename, _ = QFileDialog.getSaveFileName(self, title,
                        os.path.join(self.confHandler.getCurrentPath(),
                                     defaultFilename), fFilter)
        
        if filename:
            fileExtention = '.txt'
            if filename[-4:] != fileExtention:
                filename += fileExtention
            self.confHandler.saveToFile(filename)
        else:
            return False
    
    def onTypeAChange(self):
        idx = self.fieldTypeA.currentIndex()
        self.projectHandler.setPointType('A', idx)
        # Update GUI: fieldHMKran
        if idx in [0, 1]:       # pole, pole_anchor
            self.fieldHMKran.setEnabled(False)
            self.fieldHMKran.setText('')
        elif idx == 2:          # crane
            paramVal = self.paramHandler.getParameterAsStr('HM_Kran')
            self.fieldHMKran.setText(paramVal)
            self.fieldHMKran.setEnabled(True)
        self.updateParametersetField()
    
    def onTypeEChange(self):
        idx = self.fieldTypeE.currentIndex()
        self.projectHandler.setPointType('E', idx)
    
    def onInfo(self):
        QMessageBox.information(self, "SEILAPLAN Info", infoTxt,
                                QMessageBox.Ok)
    
    def onHeightDataInfoShow(self):
        msg = ''
        if self.sender().objectName() == 'infoRasterlayer':
            msg = ('Höheninformation aus einem Höhenraster auslesen. Die Liste'
                   ' beinhaltet alle im aktuellen QGIS-Projekt vorhanden Raster.'
                   '<br>Wird ein neuer Raster zu QGIS hinzugefügt, kann die Liste '
                   'per Aktualisieren-Schaltfläche ergänzt werden.')
        elif self.sender().objectName() == 'infoSurveyData':
            msg = ("Profil-Messpunkte aus Feldaufnahmen laden.<br><br>"
                   "Unterstützte Dateitypen:<br>"
                   "1) CSV-Exportdatei des Haglöf Sweden Vertex Messgerätes.<br>"
                   "2) Generische CSV-Datei (Komma-separiert) mit den "
                   "Koordinaten-Spalten 'x', 'y' und 'z'. Die Datei darf keine "
                   "Kommentare enthalten und die Punkte sind sortiert aufzulisten.")
        QMessageBox.information(self, "Höheninformationen laden", msg,
                                QMessageBox.Ok)
    
    def onPointAInfoShow(self):
        # TODO
        msg = ('')
        QMessageBox.information(self, "Anfangspunkt", msg,
                                QMessageBox.Ok)

    def onPointEInfoShow(self):
        # TODO
        msg = ('')
        QMessageBox.information(self, "Endpunkt", msg,
                                QMessageBox.Ok)
    
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
    
    def onShowInfoFieldE(self):
        msg = ('Materialkennwert des Tragseils, welcher den Zusammenhang '
               'zwischen Spannung und Dehnung des Seils beschreibt. Der '
               'Kennwert variiert kaum, weshalb der Default-Wert für die '
               'meisten üblichen Seile übernommen werden kann.')
        QMessageBox.information(self, "Elastizitätsmodul Tragseil", msg,
                                QMessageBox.Ok)
    
    def onShowInfoFieldSFT(self):
        msg = ('Europaweit wird ein Sicherheitsfaktor von 3.0 für das '
               'Tragseil verwendet.')
        QMessageBox.information(self, "Sicherheitsfaktor Tragseil", msg,
                                QMessageBox.Ok)
        
    def goToAdjustmentWindow(self):
        if self.confHandler.checkValidState() \
                and self.checkEqualSpatialRef \
                and self.confHandler.prepareForCalculation():
            self.startAlgorithm = False
            self.goToAdjustment = True
            self.close()
        else:
            return False
    
    def apply(self):
        if self.confHandler.checkValidState() \
                and self.checkEqualSpatialRef \
                and self.confHandler.prepareForCalculation():
            self.startAlgorithm = True
            self.goToAdjustment = False
            self.close()
        else:
            # If project info or parameter are missing or wrong, algorithm
            # can not start
            return False
    
    def cancel(self):
        """ Called when 'Cancel' is pressed."""
        self.close()
    
    def cleanUp(self):
        # Save user settings
        self.confHandler.updateUserSettings()
        # Clean markers and lines from map canvas
        self.drawTool.reset()
        # Remove survey line
        self.removeSurveyDataLayer()
    
    def closeEvent(self, QCloseEvent):
        """Last method that is called before main window is closed."""
        # Close additional dialogs
        self.imgBox.close()
        if self.profileWin.isVisible():
            self.profileWin.close()
        
        if self.startAlgorithm or self.goToAdjustment:
            self.drawTool.reset()
        else:
            self.cleanUp()
