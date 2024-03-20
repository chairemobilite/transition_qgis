# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordinateCaptureMapTool
                                 A QGIS plugin
 Python port of the deprecated Coordinate Capture core plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Stefanos Natsis
        email                : uclaros@gmail.com
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
from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsApplication, QgsPoint, QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject


class CoordinateCaptureMapTool(QgsMapToolEmitPoint):
    mouseClicked = pyqtSignal(QgsPointXY)
    endSelection = pyqtSignal()

    def __init__(self, iface, canvas, color, name):
        super(CoordinateCaptureMapTool, self).__init__(canvas)
        self.iface = iface
        self.mapCanvas = canvas
        self.layerName = name
        self.layer = None
        self.rubberBand = QgsRubberBand(self.mapCanvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setFillColor(color)
        self.rubberBand.setWidth(1)
        self.setCursor(QgsApplication.getThemeCursor(QgsApplication.Cursor.CrossHair))

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
                # get the existing feature
                feat = next(self.layer.getFeatures())
                # set the geometry of the existing feature to the new point
                point = QgsPointXY(self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y()))
                feat.setGeometry(QgsGeometry.fromPointXY(point))
                # update the layer's data provider with the updated feature
                self.layer.dataProvider().changeGeometryValues({feat.id(): QgsGeometry.fromPointXY(point)})
                self.layer.triggerRepaint()


            originalPoint = QgsPointXY(self.mapCanvas.getCoordinateTransform().toMapCoordinates(e.x(), e.y()))
            self.mouseClicked.emit(originalPoint)

    def canvasReleaseEvent(self, e):
        #if e.button() == Qt.RightButton:
        self.endSelection.emit()

    def deactivate(self):
        # Deactivate only if there is an active layer
        if self.layer:
            super(CoordinateCaptureMapTool, self).deactivate()
