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

from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY, QgsApplication, QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject

class CaptureCoordTool(QgsMapToolEmitPoint):
    """
        A custom map tool to capture a point on the map.
    """
    mouseClicked = pyqtSignal(QgsPointXY)
    endSelection = pyqtSignal()

    def __init__(self, iface, canvas, name):
        """
            Constructor.
            
            :param iface: The QGIS interface.
            :param canvas: The map canvas.
            :param name: The name of the layer to create.
        """
        super(CaptureCoordTool, self).__init__(canvas)
        self.iface = iface
        self.mapCanvas = canvas
        self.layerName = name
        self.layer = None
        self.setCursor(QgsApplication.getThemeCursor(QgsApplication.Cursor.CrossHair))

        # Remove layers with the same layer name if some exist
        existing_layers = QgsProject.instance().mapLayersByName(self.layerName)
        for existing_layer in existing_layers:
            QgsProject.instance().removeMapLayer(existing_layer.id())

    def canvasPressEvent(self, e):
        """
            Capture the point on the map.
        """
        if e.button() == Qt.LeftButton:
            if not self.layer:
                # create a memory layer with one point
                self.layer = QgsVectorLayer('Point', self.layerName , "memory")
                self.layer.setCrs(self.mapCanvas.mapSettings().destinationCrs())
                pr = self.layer.dataProvider()
                pt = QgsFeature()
                point = QgsPointXY(self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y()))
                pt.setGeometry(QgsGeometry.fromPointXY(point))
                pr.addFeatures([pt])
                self.layer.updateFields()
                self.layer.updateExtents()
                QgsProject.instance().addMapLayer(self.layer)
            else:
                # Set the geometry of the existing feature to the new point
                feat = next(self.layer.getFeatures())
                point = QgsPointXY(self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y()))
                feat.setGeometry(QgsGeometry.fromPointXY(point))

                # update the layer's data provider with the updated feature
                self.layer.dataProvider().changeGeometryValues({feat.id(): QgsGeometry.fromPointXY(point)})
                self.layer.triggerRepaint()

            originalPoint = QgsPointXY(self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y()))
            self.mouseClicked.emit(originalPoint)

    def canvasReleaseEvent(self, e):
        """
            End the selection.
        """
        self.endSelection.emit()

    def deactivate(self):
        """
            Deactivate the tool.
        """
        # Deactivate only if there is an active layer
        if self.layer:
            super(CaptureCoordTool, self).deactivate()
