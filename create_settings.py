import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox, QRadioButton
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.gui import QgsCheckableComboBox, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QFontMetrics

import sys
from .import_path import return_lib_path
sys.path.append(return_lib_path())
from transition_lib import Transition

class CustomLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
    
class CreateSettings(QWidget):
    def __init__(self, parent=None):
        super(CreateSettings, self).__init__(parent)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.usernameOrEmailLabel = CustomLabel(self.tr("Username or email"))
        self.usernameOrEmailLabel.setMinimumSize(50,40)

        self.username = Transition.get_username()
        self.usernameField = QLineEdit()
        self.usernameField.setText(self.username)
        self.usernameField.setReadOnly(True)
        self.usernameField.setMinimumSize(50,40)

        self.urlLabel = CustomLabel(self.tr("URL"))
        self.urlLabel.setMinimumSize(50,40)

        self.url = Transition.get_url()
        # display the url in a field that cannot be edited
        self.urlField = QLineEdit()
        self.urlField.setText(self.url)
        self.urlField.setReadOnly(True)
        self.urlField.setMinimumSize(50,40)

        # Add fields to form display
        for label, field in zip([self.usernameOrEmailLabel, self.urlLabel], 
                                [self.usernameField, self.urlField]):
            label.setWordWrap(True)
            row_layout = QVBoxLayout()
            row_layout.addWidget(label)
            row_layout.addWidget(field)
            form_layout.addRow(row_layout)

        layout.addLayout(form_layout)

