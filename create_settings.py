import os

from qgis.core import *
from qgis.PyQt.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QVBoxLayout

from pyTransition.transition import Transition

class CreateSettingsForm(QWidget):
    def __init__(self, settings, parent=None):
        super(CreateSettingsForm, self).__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.usernameOrEmailLabel = QLabel(self.tr("Username or email"))
        self.usernameOrEmailLabel.setMinimumSize(50,40)

        self.username = self.settings.value("username")
        self.usernameField = QLineEdit()
        self.usernameField.setText(self.username)
        self.usernameField.setReadOnly(True)
        self.usernameField.setMinimumSize(50,40)

        self.urlLabel = QLabel(self.tr("Transition server URL"))
        self.urlLabel.setMinimumSize(50,40)

        self.url = self.settings.value("url")
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

