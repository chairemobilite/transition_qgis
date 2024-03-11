import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.gui import QgsCheckableComboBox, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QFontMetrics

import sys
from .import_path import return_lib_path
sys.path.append(return_lib_path())
from transition_api_lib import Transition

class CustomLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def minimumSizeHint(self):
        metrics = self.fontMetrics()
        minSize = metrics.boundingRect(self.text()).size()
        minSize.setWidth(1)
        minSize.setHeight(minSize.height() + 30)
        return minSize
    
class CreateAccessibilityDialog(QWidget):
    def __init__(self, parent=None):
        super(CreateAccessibilityDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        departureOrArrivalLabel = CustomLabel(self.tr("Time to use"))
        departureOrArrivalChoice = QComboBox()
        departureOrArrivalChoice.addItems(['Departure', 'Arrival'])

        departureLabel = CustomLabel(self.tr("Departure or arrival time"))
        departureTime = QTimeEdit()
        departureTime.setDisplayFormat("hh:mm")
        departureTime.setTime(QTime(8, 00))

        nPolygonsLabel = CustomLabel(self.tr("Number of polygons to calculate"))
        nPolygons = QSpinBox()
        nPolygons.setMinimum(1)
        nPolygons.setValue(3)
        nPolygons.setToolTip(self.tr("A total duration of 60 minutes with a number of polygons of 3 implies that we will obtain three polygons: accessibility at 20 minutes, 40 minutes and 60 minutes."))

        deltaLabel = CustomLabel(self.tr("Delta (minutes)"))
        delta = QSpinBox()
        delta.setValue(15)
        delta.setMinimum(1)

        deltaIntervalLabel = CustomLabel(self.tr("Delta interval (minutes)"))
        deltaInterval = QSpinBox()
        deltaInterval.setValue(5)
        deltaInterval.setMinimum(1)
        deltaInterval.setToolTip(self.tr("A delta of 15 minutes with an interval of 5 minutes implies that the polygon area will be averaged over polygons obtained 15 minutes before, 10 minutes before, 5 minutes before, at specified time, 5 minutes after, 10 minutes after and 15 minutes after the specified departure or arrival time."))

        scenarioLabel = CustomLabel(self.tr("Scenario"))
        scenarioChoice = QComboBox()
        scenarios = Transition.get_transition_scenarios()
        scenarioChoice.addItems(scenarios)

        placeNameLabel = CustomLabel(self.tr("Place name"))
        placeName = QLineEdit()

        maxTotalTravelTimeLabel = CustomLabel(self.tr("Maximum total travel time including access and egress (minutes)"))
        maxTotalTravelTime = QSpinBox()
        maxTotalTravelTime.setValue(30)

        minWaitTimeLabel = CustomLabel(self.tr("Minimum waiting time (minutes)"))
        minWaitTime = QSpinBox()
        minWaitTime.setMinimum(1)
        minWaitTime.setValue(3)
        minWaitTime.setToolTip(self.tr("To account for timetable uncertainty, this value should be greater or equal to 1 minute. Suggested value: 3 minutes"))

        maxAccessTimeOrigDestLabel = CustomLabel(self.tr("Maximum access and egress travel time (minutes)"))
        maxAccessTimeOrigDest = QSpinBox()
        maxAccessTimeOrigDest.setValue(15)
        maxAccessTimeOrigDest.setMaximum(20)
        maxAccessTimeOrigDest.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxTransferWaitTimeLabel = CustomLabel(self.tr("Maximum access travel time when transferring (minutes)"))
        maxTransferWaitTime = QSpinBox()
        maxTransferWaitTime.setValue(10)
        maxTransferWaitTime.setMaximum(20)
        maxTransferWaitTime.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxFirstWaitTimeLabel = CustomLabel(self.tr("Maximum first waiting time (minutes)"))
        maxFirstWaitTime = QSpinBox()
        maxFirstWaitTime.setValue(0)
        maxFirstWaitTime.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop"))

        walkingSpeedLabel = CustomLabel(self.tr("Walking speed (km/h)"))
        walkingSpeed = QSpinBox()
        walkingSpeed.setMinimum(1)
        walkingSpeed.setValue(5)

        # Add fields to form display
        for label, field in zip([departureOrArrivalLabel, departureLabel, nPolygonsLabel, deltaLabel, deltaIntervalLabel, scenarioLabel, placeNameLabel, maxTotalTravelTimeLabel, minWaitTimeLabel, maxAccessTimeOrigDestLabel, maxTransferWaitTimeLabel, maxFirstWaitTimeLabel, walkingSpeedLabel], 
                                [departureOrArrivalChoice, departureTime, nPolygons, delta, deltaInterval, scenarioChoice, placeName, maxTotalTravelTime, minWaitTime, maxAccessTimeOrigDest, maxTransferWaitTime, maxFirstWaitTime, walkingSpeed]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

