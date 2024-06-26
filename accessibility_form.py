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

from qgis.core import *
from qgis.PyQt.QtWidgets import QCheckBox, QWidget, QFormLayout, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QRadioButton
from PyQt5.QtCore import QTime

from pyTransition import Transition

from .custom_label import CustomLabel
    
class AccessibilityForm(QWidget):
    """
        Form to set parameters for accessibility map calculation.
    """
    def __init__(self, scenarios, parent=None):
        """
            Constructor for AccessibilityForm class.

            The constructor initializes the form with the following fields:
            - Time to use (departure or arrival)
            - Departure or arrival time
            - Number of polygons to calculate
            - Display polygons in distinct layers
            - Delta (minutes)
            - Delta interval (minutes)
            - Scenario
            - Maximum total travel time including access and egress (minutes)
            - Minimum waiting time (minutes)
            - Maximum access and egress travel time (minutes)
            - Maximum access travel time when transferring (minutes)
            - Maximum first waiting time (minutes)
            - Walking speed (km/h)
            - Output layer name
        """
        super(AccessibilityForm, self).__init__(parent)

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

        self.distinctPolygonLayersLabel = CustomLabel(self.tr("Display polygons in distinct layers"))
        self.distinctPolygonLayers = QCheckBox()
        self.distinctPolygonLayers.setChecked(False)

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
        self.scenariosNames = scenarios
        self.scenarioChoice.addItems(self.scenariosNames)

        self.outputLayerNameLabel = CustomLabel(self.tr("Output layer name"))
        self.outputLayerName = QLineEdit()

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
        self.maxFirstWaitTime.setMinimum(-1)
        self.maxFirstWaitTime.setValue(-1)
        self.maxFirstWaitTime.setToolTip(self.tr("If waiting time at first stop is greater than this value for a line, ignore the departure of this line at this stop. Use -1 to ignore this field and allow for indefinite waiting."))

        self.walkingSpeedLabel = CustomLabel(self.tr("Walking speed (km/h)"))
        self.walkingSpeed = QSpinBox()
        self.walkingSpeed.setMinimum(1)
        self.walkingSpeed.setValue(5)

        # Add fields to form display
        for label, field in zip([self.departureOrArrivalLabel, self.departureOrArrivalTimeLabel, self.nPolygonsLabel, self.distinctPolygonLayersLabel, self.deltaLabel, self.deltaIntervalLabel, self.scenarioLabel, self.maxTotalTravelTimeLabel, self.minWaitTimeLabel, self.maxAccessTimeOrigDestLabel, self.maxTransferWaitTimeLabel, self.maxFirstWaitTimeLabel, self.walkingSpeedLabel, self.outputLayerNameLabel],
                                [self.radioButtonsWidget, self.departureOrArrivalTime, self.nPolygons, self.distinctPolygonLayers, self.delta, self.deltaInterval, self.scenarioChoice, self.maxTotalTravelTime, self.minWaitTime, self.maxAccessTimeOrigDest, self.maxTransferWaitTime, self.maxFirstWaitTime, self.walkingSpeed, self.outputLayerName]):
            label.setWordWrap(True)
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=4)  # 66% of the space
            row_layout.addWidget(field, stretch=2)  # 33% of the space
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

