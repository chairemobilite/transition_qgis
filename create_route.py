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

        # Create each field and corresponding label
        modeLabel = CustomLabel("Effectuer le calcul de chemin pour les modes suivants")
        modeChoice = QgsCheckableComboBox()
        modes = Transition.get_transition_routing_modes()
        modeChoice.addItems(modes)

        departureLabel = CustomLabel("Heure de départ [HH:MM]")
        departureTime = QTimeEdit()
        departureTime.setDisplayFormat("hh:mm")
        departureTime.setTime(QTime(8, 00))

        arrivalLabel = CustomLabel("Heure de départ [HH:MM]")
        arrivalTime = QTimeEdit()
        arrivalTime.setDisplayFormat("hh:mm")
        arrivalTime.setTime(QTime(10, 00))

        maxParcoursTimeLabel = CustomLabel("Temps de parcours maximal incluant les accès (minutes)")
        maxParcoursTimeChoice = QSpinBox()
        maxParcoursTimeChoice.setMaximum(999999999)

        minWaitTimeLabel = CustomLabel("Temps minimum d'attente (minutes)")
        minWaitTimeChoice = QSpinBox()
        minWaitTimeChoice.setMinimum(1)
        minWaitTimeChoice.setValue(3)
        minWaitTimeChoice.setToolTip("Pour tenir compte des incertitudes des horaires, cette valeur doit être de 1 minute ou plus. Valeur suggérée: 3 minutes")

        maxAccessTimeOrigDestLabel = CustomLabel("Temps maximum d'accès à l'origine et à destination (minutes)")
        maxAccessTimeOrigDestChoice = QSpinBox()
        maxAccessTimeOrigDestChoice.setValue(15)
        maxAccessTimeOrigDestChoice.setMaximum(20)
        maxAccessTimeOrigDestChoice.setToolTip("Pour éviter de longs temps de calcul, la valeur maximale est de 20 minutes.")

        maxTransferWaitTimeLabel = CustomLabel("Temps maximum d'accès lors des transferts (minutes)")
        maxTransferWaitTimeChoice = QSpinBox()
        maxTransferWaitTimeChoice.setValue(10)
        maxTransferWaitTimeChoice.setMaximum(20)
        maxTransferWaitTimeChoice.setToolTip("Pour éviter de longs temps de calcul, la valeur maximale est de 20 minutes.")

        maxWaitTimeFisrstStopLabel = CustomLabel("Temps d'attente maximal au premier arrêt (minutes)")
        maxWaitTimeFisrstStopChoice = QSpinBox()
        maxWaitTimeFisrstStopChoice.setValue(0)
        maxWaitTimeFisrstStopChoice.setToolTip("Si l'attente au premier arrêt est plus grande que cette valeur pour une ligne, ignorer le départ de cette ligne à cet arrêt")

        scenarioLabel = CustomLabel("Scénario")
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

