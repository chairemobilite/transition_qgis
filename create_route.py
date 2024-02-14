import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.gui import QgsCheckableComboBox, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import QTime

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'create_route_ui.ui'))

class MapClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, dialog):
        super(MapClickTool, self).__init__(canvas)
        self.dialog = dialog

    def canvasReleaseEvent(self, event):
        point = self.toLayerCoordinates(self.dialog.current_layer, event.pos())
        self.dialog.clicked_point = point
        self.dialog.show_coordinate(point)

class CreateRouteDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateRouteDialog, self).__init__(parent)
        #self.setupUi(self)

        self.setGeometry(0, 0, 650, 300)
        self.setWindowTitle("Create new route")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        modeLabel = QLabel("Effectuer le calcul de chemin pour les modes suivants")
        #modeLabel.setWordWrap(True)
        modeChoice = QgsCheckableComboBox()
        modeChoice.addItems(["marche", "bus urbain", "metro"])

        departureLabel = QLabel("Heure de départ [HH:MM]")
        departureTime = QTimeEdit()
        departureTime.setDisplayFormat("hh:mm")
        departureTime.setTime(QTime(8, 00))

        arrivalLabel = QLabel("Heure de départ [HH:MM]")
        arrivalTime = QTimeEdit()
        arrivalTime.setDisplayFormat("hh:mm")
        arrivalTime.setTime(QTime(10, 00))

        maxParcoursTimeLabel = QLabel("Temps de parcours maximal incluant les accès (minutes)")
        #maxParcoursTimeLabel.setWordWrap(True)
        maxParcoursTimeChoice = QSpinBox()
        maxParcoursTimeChoice.setMaximum(999999999)

        minWaitTimeLabel = QLabel("Temps minimum d'attente (minutes)")
        minWaitTimeChoice = QSpinBox()
        minWaitTimeChoice.setMinimum(1)
        minWaitTimeChoice.setValue(3)
        minWaitTimeChoice.setToolTip("Pour tenir compte des incertitudes des horaires, cette valeur doit être de 1 minute ou plus. Valeur suggérée: 3 minutes")

        maxAccessTimeOrigDestLabel = QLabel("Temps maximum d'accès à l'origine et à destination (minutes)")
        maxAccessTimeOrigDestChoice = QSpinBox()
        maxAccessTimeOrigDestChoice.setValue(15)
        maxAccessTimeOrigDestChoice.setMaximum(20)
        maxAccessTimeOrigDestChoice.setToolTip("Pour éviter de longs temps de calcul, la valeur maximale est de 20 minutes.")

        maxTransferWaitTimeLabel = QLabel("Temps maximum d'accès lors des transferts (minutes)")
        maxTransferWaitTimeChoice = QSpinBox()
        maxTransferWaitTimeChoice.setValue(10)
        maxTransferWaitTimeChoice.setMaximum(20)
        maxTransferWaitTimeChoice.setToolTip("Pour éviter de longs temps de calcul, la valeur maximale est de 20 minutes.")

        maxWaitTimeFisrstStopLabel = QLabel("Temps d'attente maximal au premier arrêt (minutes)")
        maxWaitTimeFisrstStopChoice = QSpinBox()
        maxWaitTimeFisrstStopChoice.setValue(0)
        maxWaitTimeFisrstStopChoice.setToolTip("Si l'attente au premier arrêt est plus grande que cette valeur pour une ligne, ignorer le départ de cette ligne à cet arrêt")

        scenarioLabel = QLabel("Scénario")
        scenarioChoice = QComboBox()
        scenarioChoice.addItems(["scenario1", "scenario2"])

        for label, field in zip([modeLabel, departureLabel, arrivalLabel, maxParcoursTimeLabel, minWaitTimeLabel, maxAccessTimeOrigDestLabel, maxTransferWaitTimeLabel], 
                                [modeChoice, departureTime, arrivalTime, maxParcoursTimeChoice, minWaitTimeChoice, maxAccessTimeOrigDestChoice, maxTransferWaitTimeChoice]):
            row_layout = QHBoxLayout()
            row_layout.addWidget(label, stretch=3)  # 75% of the space
            row_layout.addWidget(field, stretch=1)  # 25% of the space
            form_layout.addRow(row_layout)

        
        layout.addLayout(form_layout)

        self.buttonCoord = QPushButton("Select coord", self)
        layout.addWidget(self.buttonCoord)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
