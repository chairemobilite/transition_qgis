import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox, QRadioButton, QCheckBox
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.gui import QgsCheckableComboBox, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QFontMetrics

from transition_lib.transition import Transition

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

        self.modeLabel = CustomLabel(self.tr("Calculate for the following modes"))
        self.modeChoice = QgsCheckableComboBox()
        self.modes = Transition.get_routing_modes()
        self.modeChoice.addItems(self.modes)

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

        self.maxParcoursTimeLabel = CustomLabel(self.tr("Maximum total travel time including access and egress (minutes)"))
        self.maxParcoursTimeChoice = QSpinBox()
        self.maxParcoursTimeChoice.setMaximum(1000)
        self.maxParcoursTimeChoice.setValue(180)

        self.minWaitTimeLabel = CustomLabel(self.tr("Minimum waiting time (minutes)"))
        self.minWaitTimeChoice = QSpinBox()
        self.minWaitTimeChoice.setMinimum(1)
        self.minWaitTimeChoice.setValue(3)
        self.minWaitTimeChoice.setToolTip(self.tr("To account for timetable uncertainty, this value should be greater or equal to 1 minute. Suggested value: 3 minutes"))

        self.maxAccessTimeOrigDestLabel = CustomLabel(self.tr("Maximum access and egress travel time (minutes)"))
        self.maxAccessTimeOrigDestChoice = QSpinBox()
        self.maxAccessTimeOrigDestChoice.setValue(15)
        self.maxAccessTimeOrigDestChoice.setMaximum(20)
        self.maxAccessTimeOrigDestChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        self.maxTransferWaitTimeLabel = CustomLabel(self.tr("Maximum access travel time when transferring (minutes)"))
        self.maxTransferWaitTimeChoice = QSpinBox()
        self.maxTransferWaitTimeChoice.setValue(10)
        self.maxTransferWaitTimeChoice.setMaximum(20)
        self.maxTransferWaitTimeChoice.setToolTip(self.tr("To avoid long calculation time, this value has a maximum of 20 minutes."))

        self.maxWaitTimeFisrstStopLabel = CustomLabel(self.tr("Maximum first waiting time (minutes)"))
        self.maxWaitTimeFisrstStopChoice = QSpinBox()
        self.maxWaitTimeFisrstStopChoice.setValue(5)
        self.maxWaitTimeFisrstStopChoice.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop"))

        self.scenarioLabel = CustomLabel(self.tr("Scenario"))
        self.scenarioChoice = QComboBox()
        self.scenarios = Transition.get_scenarios()
        self.scenariosNames = [entry['name'] for entry in self.scenarios['collection']]
        self.scenarioChoice.addItems(self.scenariosNames)

        self.withAlternativeLabel = CustomLabel(self.tr("Calculate with alternatives"))
        self.withAlternativeChoice = QCheckBox()
        self.withAlternativeChoice.setChecked(False)

        self.routeNameLabel = CustomLabel(self.tr("Route name"))
        self.routeName = QLineEdit()

        # Add fields to form display
        for label, field in zip([self.modeLabel, self.departureOrArrivalLabel,self.departureOrArrivalTimeLabel, self.routeNameLabel, self.maxParcoursTimeLabel, self.minWaitTimeLabel, self.maxAccessTimeOrigDestLabel, self.maxTransferWaitTimeLabel, self.maxWaitTimeFisrstStopLabel, self.scenarioLabel, self.withAlternativeLabel], 
                                [self.modeChoice, self.radioButtonsWidget, self.departureOrArrivalTime, self.routeName, self.maxParcoursTimeChoice, self.minWaitTimeChoice, self.maxAccessTimeOrigDestChoice, self.maxTransferWaitTimeChoice, self.maxWaitTimeFisrstStopChoice, self.scenarioChoice, self.withAlternativeChoice]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

