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
        modeChoice = QgsCheckableComboBox()
        modes = Transition.get_transition_routing_modes()
        modeChoice.addItems(modes)

        departureLabel = CustomLabel(self.tr("Departure time"))
        departureTime = QTimeEdit()
        departureTime.setDisplayFormat("hh:mm")
        departureTime.setTime(QTime(8, 00))

        arrivalLabel = CustomLabel(self.tr("Arrival time"))
        arrivalTime = QTimeEdit()
        arrivalTime.setDisplayFormat("hh:mm")
        arrivalTime.setTime(QTime(10, 00))

        maxParcoursTimeLabel = CustomLabel(self.tr("Maximum total travel time including access and egress (minutes)"))
        maxParcoursTimeChoice = QSpinBox()
        maxParcoursTimeChoice.setMaximum(999999999)

        minWaitTimeLabel = CustomLabel(self.tr("Minimum waiting time (minutes)"))
        minWaitTimeChoice = QSpinBox()
        minWaitTimeChoice.setMinimum(1)
        minWaitTimeChoice.setValue(3)
        minWaitTimeChoice.setToolTip(self.tr("To account for timetable uncertainty, this value should be greater or equal to 1 minute. Suggested value: 3 minutes"))

        maxAccessTimeOrigDestLabel = CustomLabel(self.tr("Maximum access and egress travel time (minutes)"))
        maxAccessTimeOrigDestChoice = QSpinBox()
        maxAccessTimeOrigDestChoice.setValue(15)
        maxAccessTimeOrigDestChoice.setMaximum(20)
        maxAccessTimeOrigDestChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxTransferWaitTimeLabel = CustomLabel(self.tr("Maximum access travel time when transferring (minutes)"))
        maxTransferWaitTimeChoice = QSpinBox()
        maxTransferWaitTimeChoice.setValue(10)
        maxTransferWaitTimeChoice.setMaximum(20)
        maxTransferWaitTimeChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        maxWaitTimeFisrstStopLabel = CustomLabel(self.tr("Maximum first waiting time (minutes)"))
        maxWaitTimeFisrstStopChoice = QSpinBox()
        maxWaitTimeFisrstStopChoice.setValue(0)
        maxWaitTimeFisrstStopChoice.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop"))

        scenarioLabel = CustomLabel(self.tr("Scenario"))
        scenarioChoice = QComboBox()
        scenarios = Transition.get_transition_scenarios()
        scenarioChoice.addItems(scenarios)

        # Add fields to form display
        for label, field in zip([modeLabel, departureLabel, arrivalLabel, maxParcoursTimeLabel, minWaitTimeLabel, maxAccessTimeOrigDestLabel, maxTransferWaitTimeLabel, maxWaitTimeFisrstStopLabel, scenarioLabel], 
                                [modeChoice, departureTime, arrivalTime, maxParcoursTimeChoice, minWaitTimeChoice, maxAccessTimeOrigDestChoice, maxTransferWaitTimeChoice, maxWaitTimeFisrstStopChoice, scenarioChoice]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

