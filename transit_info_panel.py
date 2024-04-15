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
from qgis.PyQt.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from qgis.gui import QgsCheckableComboBox
from PyQt5.QtCore import QTime

from pyTransition.transition import Transition

class TransitInformationPanel(QWidget):
    def __init__(self, transitPaths, tabWidget, index, parent=None):
        super(TransitInformationPanel, self).__init__(parent)
        stepWidget = QWidget(self)
        scrollArea = QScrollArea(self)

        scrollArea.setWidgetResizable(True)

        stepLayout = QVBoxLayout(self)
        for step in transitPaths["steps"]:
            action = step['action']
            if action == "boarding" :
                # Add information about the line and the stop in self.dockwidget.scrollArea
                lineNumber = step["lineShortname"]
                stopName = step["nodeName"]
                # Departure time is in seconds since midnight. Convert it to a hh:mm format
                departureTimeSeconds = step["departureTime"]
                departureTime = f"{(departureTimeSeconds // 3600):02d}:{((departureTimeSeconds % 3600) // 60):02d}"

                # Add a new label with the information
                label = QLabel(self.tr("{} : Board line {} at stop {}.").format(departureTime, lineNumber, stopName))
                stepLayout.addWidget(label)
            elif action == "unboarding":
                lineNumber = step["lineShortname"]
                stopName = step["nodeName"]
                # Arrival time is in seconds since midnight. Convert it to a hh:mm format.
                arrivalTimeSeconds = step["arrivalTime"]
                arrivalTime = f"{(arrivalTimeSeconds // 3600):02d}:{((arrivalTimeSeconds % 3600) // 60):02d}"

                # Add a new label with the information
                label = QLabel(self.tr("{} : Unboard line {} at stop {}.").format(arrivalTime, lineNumber, stopName))
                stepLayout.addWidget(label)
            else:
                # Add information about the walk
                # distance is in meters
                distance = step["distance"]
                duration = step["travelTime"] // 60
                departureTimeSeconds = step["departureTime"]
                departureTime = f"{(departureTimeSeconds // 3600):02d}:{((departureTimeSeconds % 3600) // 60):02d}"

                # Add a new label with the information
                label = QLabel(self.tr("{} : Walk for {} minutes over {} meters.").format(departureTime, duration, distance))
                stepLayout.addWidget(label)

        stepWidget.setLayout(stepLayout)
        scrollArea.setWidget(stepWidget)
        title = "Transit" if index == 0 else self.tr(f"Alternative {index}")
        tabWidget.addTab(scrollArea, title)


        