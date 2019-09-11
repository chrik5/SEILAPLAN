# -*- coding: utf-8 -*-
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

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
import qgis.utils
# Initialize Qt resources from file resources.py
from .gui import resources_rc
# GUI
from .seilaplanPluginDialog import SeilaplanPluginDialog
# Algorithm
from .gui.progressDialog import ProgressDialog
from .processingThread import ProcessingTask
from .gui.adjustmentDialog import AdjustmentDialog


class SeilaplanPlugin(object):
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n',
                                  'SeilaplanPlugin_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.action = None
        self.progressDialog = None
        self.dlg = None
        self.adjustmentWindow = None
        
        # try:
        #     import pydevd
        #     pydevd.settrace('localhost', port=53100,
        #                 stdoutToServer=True, stderrToServer=True)
        # except ConnectionRefusedError:
        #     pass
        # except ImportError:
        #     pass


    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/SeilaplanPlugin/gui/icons/icon_app.png"),
            "SEILAPLAN", self.iface.mainWindow())
        self.action.setWhatsThis("SEILAPLAN")
        # Connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&SEILAPLAN", self.action)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu('&SEILAPLAN', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run method that performs all the real work"""

        # Control variables for possible rerun of algorithm
        reRun = True
        reRunProj = None

        while reRun:
    
            
            
            # Create seperate threa for calculations so that QGIS stays
            # responsive
            workerThread = ProcessingTask()
            
            # Initialize dialog window
            self.dlg = SeilaplanPluginDialog(self.iface, workerThread)
            # Get available raster from table of content in QGIS
            self.dlg.updateRasterList()
            # Load initial values of dialog
            self.dlg.loadInitialVals()

            # If this is a rerun of the algorithm the previous user values are
            #   loaded into the GUI
            if reRunProj:
                self.dlg.loadProj(reRunProj)

            self.dlg.show()
            # Start event loop
            self.dlg.exec_()

            reRun = False
            reRunProj = None

            
            # The algorithm is executed in a separate thread. To see progress,
            # a new gui shows a progress bar.
            
            # If all needed data has been input in the gui and the user has
            # clicked 'ok'
            if workerThread.state is True:
                # Initialize gui to show progress
                self.progressDialog = ProgressDialog(self.iface)
                self.progressDialog.setThread(workerThread)

                # Add task to taskmanager of QGIS and start the calculations
                QgsApplication.taskManager().addTask(workerThread)

                # Show progress bar
                self.progressDialog.run()

                self.adjustmentWindow.initData(self.progressDialog.result)
                self.adjustmentWindow.show()
                self.adjustmentWindow.exec_()

                # # After calculations have finished and progress gui has been
                # # closed: Check if user wants a rerun
                # if self.progressDialog.reRun:
                #     reRun = True
                #     reRunProj = workerThread.projInfo['projFile']

                
                del self.progressDialog
            del self.adjustmentWindow
            del workerThread
            del self.dlg

        return

    def reject(self):
        self.dlg.Reject()

    def cleanUp(self):
        pass
