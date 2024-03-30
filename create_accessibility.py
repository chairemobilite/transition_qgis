import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox, QRadioButton
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.gui import QgsCheckableComboBox, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QFontMetrics

from transition_lib import Transition

class CustomLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def minimumSizeHint(self):
        metrics = self.fontMetrics()
        minSize = metrics.boundingRect(self.text()).size()
        minSize.setWidth(1)
        minSize.setHeight(minSize.height() + 30)
        return minSize
    
class CreateAccessibilityForm(QWidget):
    def __init__(self, parent=None):
        super(CreateAccessibilityForm, self).__init__(parent)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.departureOrArrivalLabel = CustomLabel(self.tr("Time to use"))
        self.departureRadioButton = QRadioButton(self.tr("Departure"))
        self.departureRadioButton.setChecked(True)
        self.arrivalRadioButton = QRadioButton(self.tr("Arrival"))

        self.radioButtonsLayout = QHBoxLayout()
        self.radioButtonsLayout.addWidget(self.departureRadioButton)
        self.radioButtonsLayout.addWidget(self.arrivalRadioButton)

        self.radioButtonsWidget = QWidget()
        self.radioButtonsWidget.setLayout(self.radioButtonsLayout) 

        self.departureOrArrivalTimeLabel = CustomLabel(self.tr("Departure or arrival time"))
        self.departureOrArrivalTime = QTimeEdit()
        self.departureOrArrivalTime.setDisplayFormat("hh:mm")
        self.departureOrArrivalTime.setTime(QTime(8, 00))

        self.nPolygonsLabel = CustomLabel(self.tr("Number of polygons to calculate"))
        self.nPolygons = QSpinBox()
        self.nPolygons.setMinimum(1)
        self.nPolygons.setValue(3)
        self.nPolygons.setToolTip(self.tr("A total duration of 60 minutes with a number of polygons of 3 implies that we will obtain three polygons: accessibility at 20 minutes, 40 minutes and 60 minutes."))

        self.deltaLabel = CustomLabel(self.tr("Delta (minutes)"))
        self.delta = QSpinBox()
        self.delta.setValue(15)
        self.delta.setMinimum(1)

        self.deltaIntervalLabel = CustomLabel(self.tr("Delta interval (minutes)"))
        self.deltaInterval = QSpinBox()
        self.deltaInterval.setValue(5)
        self.deltaInterval.setMinimum(1)
        self.deltaInterval.setToolTip(self.tr("A delta of 15 minutes with an interval of 5 minutes implies that the polygon area will be averaged over polygons obtained 15 minutes before, 10 minutes before, 5 minutes before, at specified time, 5 minutes after, 10 minutes after and 15 minutes after the specified departure or arrival time."))

        self.scenarioLabel = CustomLabel(self.tr("Scenario"))
        self.scenarioChoice = QComboBox()
        self.scenarios = Transition.get_scenarios()
        self.scenariosNames = [entry['name'] for entry in self.scenarios.json()['collection']]
        self.scenarioChoice.addItems(self.scenariosNames)

        self.placeNameLabel = CustomLabel(self.tr("Place name"))
        self.placeName = QLineEdit()

        self.maxTotalTravelTimeLabel = CustomLabel(self.tr("Maximum total travel time including access and egress (minutes)"))
        self.maxTotalTravelTime = QSpinBox()
        self.maxTotalTravelTime.setValue(30)

        self.minWaitTimeLabel = CustomLabel(self.tr("Minimum waiting time (minutes)"))
        self.minWaitTime = QSpinBox()
        self.minWaitTime.setMinimum(1)
        self.minWaitTime.setValue(3)
        self.minWaitTime.setToolTip(self.tr("To account for timetable uncertainty, this value should be greater or equal to 1 minute. Suggested value: 3 minutes"))

        self.maxAccessTimeOrigDestLabel = CustomLabel(self.tr("Maximum access and egress travel time (minutes)"))
        self.maxAccessTimeOrigDest = QSpinBox()
        self.maxAccessTimeOrigDest.setValue(15)
        self.maxAccessTimeOrigDest.setMaximum(20)
        self.maxAccessTimeOrigDest.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        self.maxTransferWaitTimeLabel = CustomLabel(self.tr("Maximum access travel time when transferring (minutes)"))
        self.maxTransferWaitTime = QSpinBox()
        self.maxTransferWaitTime.setValue(10)
        self.maxTransferWaitTime.setMaximum(20)
        self.maxTransferWaitTime.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        self.maxFirstWaitTimeLabel = CustomLabel(self.tr("Maximum first waiting time (minutes)"))
        self.maxFirstWaitTime = QSpinBox()
        self.maxFirstWaitTime.setValue(0)
        self.maxFirstWaitTime.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop"))

        self.walkingSpeedLabel = CustomLabel(self.tr("Walking speed (km/h)"))
        self.walkingSpeed = QSpinBox()
        self.walkingSpeed.setMinimum(1)
        self.walkingSpeed.setValue(5)

        # Add fields to form display
        for label, field in zip([self.departureOrArrivalLabel, self.departureOrArrivalTimeLabel, self.nPolygonsLabel, self.deltaLabel, self.deltaIntervalLabel, self.scenarioLabel, self.placeNameLabel, self.maxTotalTravelTimeLabel, self.minWaitTimeLabel, self.maxAccessTimeOrigDestLabel, self.maxTransferWaitTimeLabel, self.maxFirstWaitTimeLabel, self.walkingSpeedLabel], 
                                [self.radioButtonsWidget, self.departureOrArrivalTime, self.nPolygons, self.delta, self.deltaInterval, self.scenarioChoice, self.placeName, self.maxTotalTravelTime, self.minWaitTime, self.maxAccessTimeOrigDest, self.maxTransferWaitTime, self.maxFirstWaitTime, self.walkingSpeed]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

