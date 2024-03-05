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
    
class CreateRouteDialog(QWidget):
    def __init__(self, parent=None):
        super(CreateRouteDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        modeLabel = CustomLabel(self.tr("Calculate for the following modes"))
        self.modeChoice = QgsCheckableComboBox()
        modes = Transition.get_transition_routing_modes()
        self.modeChoice.addItems(modes)

        departureLabel = CustomLabel(self.tr("Departure time"))
        self.departureTime = QTimeEdit()
        self.departureTime.setDisplayFormat("hh:mm")
        self.departureTime.setTime(QTime(8, 00))

        arrivalLabel = CustomLabel(self.tr("Arrival time"))
        self.arrivalTime = QTimeEdit()
        self.arrivalTime.setDisplayFormat("hh:mm")
        self.arrivalTime.setTime(QTime(10, 00))

        maxParcoursTimeLabel = CustomLabel(self.tr("Maximum total travel time including access and egress (minutes)"))
        self.maxParcoursTimeChoice = QSpinBox()
        self.maxParcoursTimeChoice.setMaximum(1000)
        self.maxParcoursTimeChoice.setValue(180)


        minWaitTimeLabel = CustomLabel(self.tr("Minimum waiting time (minutes)"))
        self.minWaitTimeChoice = QSpinBox()
        self.minWaitTimeChoice.setMinimum(1)
        self.minWaitTimeChoice.setValue(3)
        self.minWaitTimeChoice.setToolTip(self.tr("To account for timetable uncertainty, this value should be greater or equal to 1 minute. Suggested value: 3 minutes"))

        maxAccessTimeOrigDestLabel = CustomLabel(self.tr("Maximum access and egress travel time (minutes)"))
        self.maxAccessTimeOrigDestChoice = QSpinBox()
        self.maxAccessTimeOrigDestChoice.setValue(15)
        self.maxAccessTimeOrigDestChoice.setMaximum(20)
        self.maxAccessTimeOrigDestChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxTransferWaitTimeLabel = CustomLabel(self.tr("Maximum access travel time when transferring (minutes)"))
        self.maxTransferWaitTimeChoice = QSpinBox()
        self.maxTransferWaitTimeChoice.setValue(10)
        self.maxTransferWaitTimeChoice.setMaximum(20)
        self.maxTransferWaitTimeChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxWaitTimeFisrstStopLabel = CustomLabel(self.tr("Maximum first waiting time (minutes)"))
        self.maxWaitTimeFisrstStopChoice = QSpinBox()
        self.maxWaitTimeFisrstStopChoice.setValue(5)
        self.maxWaitTimeFisrstStopChoice.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop"))

        scenarioLabel = CustomLabel(self.tr("Scenario"))
        self.scenarioChoice = QComboBox()
        self.scenarios = Transition.get_transition_scenarios()
        self.scenariosNames = [entry['name'] for entry in self.scenarios.json()['collection']]
        self.scenarioChoice.addItems(self.scenariosNames)

        # Add fields to form display
        for label, field in zip([modeLabel, departureLabel, arrivalLabel, maxParcoursTimeLabel, minWaitTimeLabel, maxAccessTimeOrigDestLabel, maxTransferWaitTimeLabel, maxWaitTimeFisrstStopLabel, scenarioLabel], 
                                [self.modeChoice, self.departureTime, self.arrivalTime, self.maxParcoursTimeChoice, self.minWaitTimeChoice, self.maxAccessTimeOrigDestChoice, self.maxTransferWaitTimeChoice, self.maxWaitTimeFisrstStopChoice, self.scenarioChoice]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

