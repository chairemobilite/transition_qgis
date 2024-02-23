# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Transition
                                 A QGIS plugin
 truc
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Transition
        email                : Transition
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDialog

from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsProjectionSelectionDialog
from qgis.core import QgsUnitTypes, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPointXY, QgsVectorLayer, QgsProject
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .transition_qgis_dockwidget import TransitionDockWidget
from .create_login import Login
from .coordinate_capture_map_tool import CoordinateCaptureMapTool
import os.path

import sys
import geojson
import configparser

from .import_path import return_lib_path
sys.path.append(return_lib_path())
from transition_api_lib import Transition

from .create_route import CreateRouteDialog


class TransitionWidget:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Transition_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Transition')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Transition')
        self.toolbar.setObjectName(u'Transition')

        #print "** INITIALIZING Transition"
        self.pluginIsActive = False
        self.dockwidget = None
        self.loginPopup = None
        self.validLogin = False
        
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.transform = QgsCoordinateTransform()
        self.transform.setDestinationCrs(self.crs)
        if self.crs.mapUnits() == QgsUnitTypes.DistanceDegrees:
            self.userCrsDisplayPrecision = 5
        else:
            self.userCrsDisplayPrecision = 3
        self.canvasCrsDisplayPrecision = None
        self.iface.mapCanvas().destinationCrsChanged.connect(self.setSourceCrs)
        self.setSourceCrs()

        self.mapToolFrom = CoordinateCaptureMapTool(self.iface, self.iface.mapCanvas(), Qt.darkGreen, "Starting point")
        self.mapToolFrom.mouseClicked.connect(self.mouseClickedFrom)
        self.mapToolFrom.endSelection.connect(self.endCapture)

        self.mapToolTo = CoordinateCaptureMapTool(self.iface, self.iface.mapCanvas(), Qt.blue, "Destination point")
        self.mapToolTo.mouseClicked.connect(self.mouseClickedTo)
        self.mapToolTo.endSelection.connect(self.endCapture)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Transition', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/transition_qgis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Transition'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING Transition"

        # disconnects
        if self.dockwidget is not None:
            self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        print("closing")

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

        self.mapToolFrom.deactivate()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD Transition"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Transition'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            print("Transition plugin is active")

            self.checkValidLogin()
            print(f"Valid login: {self.validLogin}")
                
            if self.validLogin:
                self.show_dockwidget()

            else:
                self.loginPopup = Login()
                self.loginPopup.finished.connect(self.onLoginFinished)

    def checkValidLogin(self):
        config = Transition.get_configurations()
        if config['credentials']['token']:
            self.validLogin = True
    

    def onLoginFinished(self, result):
        if result == QDialog.Accepted:
            print("Login successful")
            self.validLogin = True
            self.show_dockwidget()
            
            #print "** STARTING Transition"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)

        else:
            print("Login canceled")
            
            # Close the plugin's dock widget if it was created
            if self.dockwidget:
                self.iface.removeDockWidget(self.dockwidget)
                self.dockwidget.close()
            self.onClosePlugin()   

    def show_dockwidget(self):
        if self.dockwidget == None and self.validLogin:
            print("Creating new dockwidget")
            # Create the dockwidget (after translation) and keep reference
            self.dockwidget = TransitionDockWidget()
            createRouteForm = CreateRouteDialog()
            self.dockwidget.verticalLayout.addWidget(createRouteForm)

            self.dockwidget.pathButton.clicked.connect(self.onPathButtonClicked)
            self.dockwidget.nodeButton.clicked.connect(self.onNodeButtonClicked)

            self.dockwidget.captureButtonFrom.clicked.connect(self.startCapturingFrom)
            self.dockwidget.captureButtonTo.clicked.connect(self.startCapturingTo)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

        # show the dockwidget
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()         

    def onPathButtonClicked(self):
        self.dockwidget.plainTextEdit.setPlainText("Getting the paths...")
        geojson_data = Transition.get_transition_paths()
        if geojson_data:
            layer = QgsVectorLayer(geojson.dumps(geojson_data), "transition_paths", "ogr")
            if not layer.isValid():
                print("Layer failed to load!")
                return
            QgsProject.instance().addMapLayer(layer)
        else:
            print("Failed to get GeoJSON data")
        self.iface.actionPan().trigger()
    
    def onNodeButtonClicked(self):
        self.dockwidget.plainTextEdit.setPlainText("Getting the nodes...")
        geojson_data = Transition.get_transition_nodes()
        if geojson_data:
            layer = QgsVectorLayer(geojson.dumps(geojson_data), "transition_nodes", "ogr")
            if not layer.isValid():
                print("Layer failed to load!")
                return
            QgsProject.instance().addMapLayer(layer)
        else:
            print("Failed to get GeoJSON data")

        print("API called")
        self.iface.actionPan().trigger()

    def setCrs(self):
        selector = QgsProjectionSelectionDialog(self.iface.mainWindow())
        selector.setCrs(self.crs)
        if selector.exec():
            self.crs = selector.crs()
            self.transform.setDestinationCrs(self.crs)
            if self.crs.mapUnits() == QgsUnitTypes.DistanceDegrees:
                self.userCrsDisplayPrecision = 5
            else:
                self.userCrsDisplayPrecision = 3

    def setSourceCrs(self):
        self.transform.setSourceCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        if self.iface.mapCanvas().mapSettings().destinationCrs().mapUnits() == QgsUnitTypes.DistanceDegrees:
            self.canvasCrsDisplayPrecision = 5
        else:
            self.canvasCrsDisplayPrecision = 3

    def mouseClickedFrom(self, point: QgsPointXY):
        userCrsPoint = self.transform.transform(point)
        self.dockwidget.userCrsEditFrom.setText('{0:.{2}f},{1:.{2}f}'.format(userCrsPoint.x(),
                                                                         userCrsPoint.y(),
                                                                         self.userCrsDisplayPrecision))


    def mouseClickedTo(self, point: QgsPointXY):
        userCrsPoint = self.transform.transform(point)
        self.dockwidget.userCrsEditTo.setText('{0:.{2}f},{1:.{2}f}'.format(userCrsPoint.x(),
                                                                         userCrsPoint.y(),
                                                                         self.userCrsDisplayPrecision))

    def startCapturingFrom(self):
        self.iface.mapCanvas().setMapTool(self.mapToolFrom)

    def startCapturingTo(self):
        self.iface.mapCanvas().setMapTool(self.mapToolTo)

    def endCapture(self):
        self.iface.actionPan().trigger()
        self.mapToolFrom.deactivate()
