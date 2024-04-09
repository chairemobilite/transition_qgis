from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY, QgsApplication, QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject

class CaptureCoordTool(QgsMapToolEmitPoint):
    mouseClicked = pyqtSignal(QgsPointXY)
    endSelection = pyqtSignal()

    def __init__(self, iface, canvas, name):
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
        self.endSelection.emit()

    def deactivate(self):
        # Deactivate only if there is an active layer
        if self.layer:
            super(CaptureCoordTool, self).deactivate()
