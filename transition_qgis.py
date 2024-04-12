# MIT License

# Copyright (c) 2024 Polytechnique Montréal

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QTabWidget, QScrollArea
from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt5 import QtTest
from qgis.core import QgsUnitTypes, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPointXY, QgsVectorLayer, QgsProject, QgsLayerTreeGroup, Qgis
from qgis.gui import QgsProjectionSelectionDialog

import os.path
import geojson
import requests
from pyTransition.transition import Transition

from .resources import *
from .transition_qgis_dockwidget import TransitionDockWidget
from .create_login import LoginDialog
from .capture_coord_tool import CaptureCoordTool
from .create_route import CreateRouteDialog
from .create_accessibility import CreateAccessibilityForm
from .create_settings import CreateSettingsForm

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
        self.settings = QSettings()
        # initialize locale
        locale = self.settings.value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'transition_qgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Transition')
        
        self.toolbar = self.iface.addToolBar(u'Transition')
        self.toolbar.setObjectName(u'Transition')

        #print "** INITIALIZING Transition"
        self.pluginIsActive = False
        self.dockwidget = None
        self.loginPopup = None
        self.transition_paths = None

        self.tab_widget = QTabWidget()
        self.tab_widget.setWindowTitle("Transit information")


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

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
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
        
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        # Remove user settings
        if not self.settings.value('keepConnection'):
            self.removeSettings()

        # Disconnect
        if self.dockwidget is not None:
            self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
            self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Transition'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.checkValidLogin():
                self.show_dockwidget()

            else:
                self.loginPopup = LoginDialog(self.iface, self.settings)
                self.loginPopup.finished.connect(self.onLoginFinished)
                self.loginPopup.closeWidget.connect(self.onClosePlugin)

    def checkValidLogin(self):
        token = self.settings.value("token")
        if token:
            Transition.set_token(self.settings.value("token"))
            Transition.set_url(self.settings.value("url"))
            return True
        
        return False

    def onLoginFinished(self, result):
        if result == QDialog.Accepted:
            print("Login successful")
            self.show_dockwidget()

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
        else:
            # Close the plugin's dock widget if it was created
            if self.dockwidget:
                self.iface.removeDockWidget(self.dockwidget)
                self.dockwidget.close()
            self.onClosePlugin()

    def show_dockwidget(self):
        try:
            if self.dockwidget == None:
                print("Creating new dockwidget")
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = TransitionDockWidget()

                self.selectedCoords = { 'routeOriginPoint': None, 'routeDestinationPoint': None, 'accessibilityMapPoint': None }

                self.createRouteForm = CreateRouteDialog()
                self.dockwidget.routeVerticalLayout.addWidget(self.createRouteForm)
                self.createAccessibilityForm = CreateAccessibilityForm()
                self.dockwidget.accessibilityVerticalLayout.addWidget(self.createAccessibilityForm)
                self.dockwidget.createSettingsForm = CreateSettingsForm(self.settings)
                self.dockwidget.settingsVerticalLayout.addWidget(self.dockwidget.createSettingsForm)

                self.dockwidget.pathButton.clicked.connect(self.onPathButtonClicked)
                self.dockwidget.nodeButton.clicked.connect(self.onNodeButtonClicked)
                self.dockwidget.accessibilityButton.clicked.connect(self.onAccessibilityButtonClicked)
                self.dockwidget.routeButton.clicked.connect(self.onNewRouteButtonClicked)
                self.dockwidget.disconnectButton.clicked.connect(self.onDisconnectUser)
                self.mapToolFrom = CaptureCoordTool(self.iface, self.iface.mapCanvas(), "Starting point")
                self.mapToolFrom.mouseClicked.connect(lambda event: self.mouseClickedCapture(event, self.dockwidget.userCrsEditFrom, 'routeOriginPoint'))
                self.mapToolFrom.endSelection.connect(self.stopCapturing)

                self.mapToolTo = CaptureCoordTool(self.iface, self.iface.mapCanvas(), "Destination point")
                self.mapToolTo.mouseClicked.connect(lambda event: self.mouseClickedCapture(event, self.dockwidget.userCrsEditTo, 'routeDestinationPoint'))
                self.mapToolTo.endSelection.connect(self.stopCapturing)

                self.mapToolAccessibility = CaptureCoordTool(self.iface, self.iface.mapCanvas(),"Accessibility map center")
                self.mapToolAccessibility.mouseClicked.connect(lambda event: self.mouseClickedCapture(event, self.dockwidget.userCrsEditAccessibility, 'accessibilityMapPoint'))
                self.mapToolAccessibility.endSelection.connect(self.stopCapturing)

                self.dockwidget.routeCaptureButtonFrom.clicked.connect(lambda: self.startCapturing(self.mapToolFrom))
                self.dockwidget.routeCaptureButtonTo.clicked.connect(lambda: self.startCapturing(self.mapToolTo))
                self.dockwidget.accessibilityCaptureButton.clicked.connect(lambda: self.startCapturing(self.mapToolAccessibility))

                # Connect to provide cleanup on closing of dockwidget
                self.dockwidget.closingPlugin.connect(self.onClosePlugin)

                # Determine the order in which the layers are shown on the map (point, line, polygon)
                QgsProject.instance().layerTreeRegistryBridge().setLayerInsertionMethod(Qgis.LayerTreeInsertionMethod.OptimalInInsertionGroup)

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(None, "Unable to connect to server", "Unable to connect to your Transition server.\nMake sure you provided the right server URL and that the server is up.")
            self.dockwidget = None
            self.onClosePlugin()

    def onPathButtonClicked(self):
        try:
            geojson_data = Transition.get_paths()
            if geojson_data:
                # Remove the existing "transition_paths" layer if it exists
                existing_layers = QgsProject.instance().mapLayersByName("transition_paths")
                if existing_layers:
                    QgsProject.instance().removeMapLayer(existing_layers[0].id())

                # Add the new "transition_paths" layer
                layer = QgsVectorLayer(geojson.dumps(geojson_data), "transition paths", "ogr")
                if not layer.isValid():
                    raise Exception("Layer failed to load!")
                QgsProject.instance().addMapLayer(layer)

        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

    def onNodeButtonClicked(self):
        try:
            geojson_data = Transition.get_nodes()
            if geojson_data:
                # Remove the existing "transition_nodes" layer if it exists
                existing_layers = QgsProject.instance().mapLayersByName("transition_nodes")
                if existing_layers:
                    QgsProject.instance().removeMapLayer(existing_layers[0].id())

                # Add the new "transition_nodes" layer
                layer = QgsVectorLayer(geojson.dumps(geojson_data), "transition_nodes", "ogr")
                if not layer.isValid():
                    raise Exception("Layer failed to load!")
                QgsProject.instance().addMapLayer(layer)

        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

    def onNewRouteButtonClicked(self):
        # try:
            modes = self.createRouteForm.modeChoice.checkedItems()
            if not modes:
                QMessageBox.warning(self.dockwidget, "No modes selected", "Please select at least one mode.")
                return
 
            result = Transition.request_routing_result(
                modes=modes, 
                origin=[self.selectedCoords['routeOriginPoint'].x(), self.selectedCoords['routeOriginPoint'].y()], 
                destination=[self.selectedCoords['routeDestinationPoint'].x(), self.selectedCoords['routeDestinationPoint'].y()], 
                scenario_id=self.createRouteForm.scenarios['collection'][self.createRouteForm.scenarioChoice.currentIndex()]['id'], 
                max_travel_time_minutes=self.createRouteForm.maxParcoursTimeChoice.value(), 
                min_waiting_time_minutes=self.createRouteForm.minWaitTimeChoice.value(),
                max_transfer_time_minutes=self.createRouteForm.maxTransferWaitTimeChoice.value(), 
                max_access_time_minutes=self.createRouteForm.maxAccessTimeOrigDestChoice.value(), 
                departure_or_arrival_time=self.createRouteForm.departureOrArrivalTime.time().toPyTime(), 
                departure_or_arrival_choice="Departure" if self.createRouteForm.departureRadioButton.isChecked() else "Arrival", 
                max_first_waiting_time_minutes=self.createRouteForm.maxWaitTimeFisrstStopChoice.value(),
                with_geojson=True,
                with_alternatives=self.createRouteForm.withAlternativeChoice.isChecked()
            )
            
            # Remove the existing "Routing results" group if it exists
            existing_group = QgsProject.instance().layerTreeRoot().findGroup("Routing results")
            if existing_group:
                QgsProject.instance().layerTreeRoot().removeChildNode(existing_group)
            
            # Create a new layer group for the routing results
            root = QgsProject.instance().layerTreeRoot()
            routing_result_group = root.addGroup("Routing results")
            
            for mode, mode_data in result.items():  
                geojson_paths = mode_data["pathsGeojson"]

                if mode == "transit":
                    # Clear the tab widget and add the information about the transit steps to it
                    self.tab_widget.clear()
                    self.dockwidget.transitInfoLayout.addWidget(self.tab_widget)
                    transit_paths = mode_data["paths"][0]
                    self.displayTransitInformation(transit_paths)

                # Add the first route for each mode in its own layer
                geojson_data = geojson_paths[0]
                layer = QgsVectorLayer(geojson.dumps(geojson_data), mode, "ogr")
                if not layer.isValid():
                    raise Exception("Layer failed to load!")
                QgsProject.instance().addMapLayer(layer, False)
                routing_result_group.addLayer(layer)

                # If there are other alternative routes for this mode, add them as layers in a subgroup
                if len(geojson_paths) > 1:
                    mode_group = QgsLayerTreeGroup(f"{mode} alternatives")
                    routing_result_group.addChildNode(mode_group)

                    for i, index in enumerate(range(1, len(geojson_paths))):
                        geojson_data = geojson_paths[i]
                        transit_paths = mode_data["paths"][i]
                        self.displayTransitInformation(transit_paths, index)
                        layer = QgsVectorLayer(geojson.dumps(geojson_data), f"{mode} alternative {index}", "ogr")
                        if not layer.isValid():
                            raise Exception("Layer failed to load!")
                        QgsProject.instance().addMapLayer(layer, False)
                        mode_group.addLayer(layer)

        # except Exception as error:
        #     self.iface.messageBar().pushCritical('Error', str(error))

    def onAccessibilityButtonClicked(self):
        try:
            geojson_data = Transition.request_accessibility_map(
                with_geojson=True,
                departure_or_arrival_choice="Departure" if self.createAccessibilityForm.departureRadioButton.isChecked() else "Arrival",
                departure_or_arrival_time=self.createAccessibilityForm.departureOrArrivalTime.time().toPyTime(),
                n_polygons=self.createAccessibilityForm.nPolygons.value(),
                delta_minutes=self.createAccessibilityForm.delta.value(),
                delta_interval_minutes=self.createAccessibilityForm.deltaInterval.value(),
                scenario_id=self.createAccessibilityForm.scenarios['collection'][self.createAccessibilityForm.scenarioChoice.currentIndex()]['id'],
                place_name=self.createAccessibilityForm.placeName.text(),
                max_total_travel_time_minutes=self.createAccessibilityForm.maxTotalTravelTime.value(),
                min_waiting_time_minutes=self.createAccessibilityForm.minWaitTime.value(),
                max_access_egress_travel_time_minutes=self.createAccessibilityForm.maxAccessTimeOrigDest.value(),
                max_transfer_travel_time_minutes=self.createAccessibilityForm.maxTransferWaitTime.value(),
                max_first_waiting_time_minutes=self.createAccessibilityForm.maxFirstWaitTime.value() if self.createAccessibilityForm.maxFirstWaitTime.value() > -1 else None,
                walking_speed_kmh=self.createAccessibilityForm.walkingSpeed.value(),
                coordinates = [self.selectedCoords['accessibilityMapPoint'].x(), self.selectedCoords['accessibilityMapPoint'].y()]
            )
            geojson_data = geojson.dumps(geojson_data['polygons'])

            if geojson_data:
                # Remove the existing "Accessibility map" layer if it exists
                existing_layers = QgsProject.instance().mapLayersByName("Accessibility map")
                if existing_layers:
                    QgsProject.instance().removeMapLayer(existing_layers[0].id())

                # Add the new "Accessibility map" layer
                layer = QgsVectorLayer(geojson_data, "Accessibility map", "ogr")
                if not layer.isValid():
                    raise Exception("Layer failed to load!")
                QgsProject.instance().addMapLayer(layer)

                # Set layer opacity to 60%
                single_symbol_renderer = layer.renderer()
                symbol = single_symbol_renderer.symbol()
                symbol.setOpacity(0.6)
                layer.triggerRepaint()
        
        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

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

    def mouseClickedCapture(self, point: QgsPointXY, displayField, selectedCoordKey):
        userCrsPoint = self.transform.transform(point)
        displayField.setText('{0:.{2}f},{1:.{2}f}'.format(userCrsPoint.x(),
                                                          userCrsPoint.y(),
                                                          self.userCrsDisplayPrecision))
        self.selectedCoords[selectedCoordKey] = userCrsPoint

    def startCapturing(self, mapTool):
        self.iface.mapCanvas().setMapTool(mapTool)

    def stopCapturing(self):
        # Set mouse cursor back to pan mode
        self.iface.actionPan().trigger()
        self.mapToolFrom.deactivate()

    def onDisconnectUser(self):
        # Remove all layers
        for layer in QgsProject.instance().mapLayers().values():
            QgsProject.instance().removeMapLayer(layer)

        # Remove all groups
        root = QgsProject.instance().layerTreeRoot()
        for group in root.children():
            root.removeChildNode(group)

        # Remove user settings
        if self.settings.value("keepConnection") !=  Qt.CheckState.Checked:
            self.removeSettings()
        
        self.dockwidget.close()

        # add a delay to allow the layers to be removed before the login popup is shown
        QtTest.QTest.qWait(1000)
        self.loginPopup = LoginDialog(self.iface, self.settings)
        self.loginPopup.finished.connect(self.onLoginFinished)
        self.loginPopup.show()

    def removeSettings(self):
        self.settings.remove("token")
        self.settings.remove("url")
        self.settings.remove("username")
        self.settings.remove("keepConnection")

    def setLayerOpacity(self, layer, opacity):
        single_symbol_renderer = layer.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setOpacity(opacity)
        layer.triggerRepaint()

    def displayTransitInformation(self, transitPaths, index=0):
        # Add a scroll area to the tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        stepLayout = QVBoxLayout()
        stepWidget = QWidget()
        for step in transitPaths["steps"]:
            action = step['action']
            if action == "boarding" or action == "unboarding":
                # Add information about the line and the stop in self.dockwidget.scrollArea
                lineNumber = step["lineShortname"]
                stopName = step["nodeName"]

                # Add a new label with the information
                label = QLabel(f"{action.capitalize()} line {lineNumber} at stop {stopName}")
                stepLayout.addWidget(label)
            else:
                # Add information about the walk
                # distance is in meters, duration in seconds
                distance = step["distance"]
                duration = step["travelTime"] // 60
                label = QLabel(f"Walk for {duration} minutes over {distance} meters")
                stepLayout.addWidget(label)

        stepWidget.setLayout(stepLayout)
        scroll_area.setWidget(stepWidget)
        title = "Transit" if index == 0 else f"Alternative {index}"
        self.tab_widget.addTab(scroll_area, title)



        

