import os
import sys
from tkinter import messagebox
from qgis.PyQt import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox

from .import_path import return_lib_path
sys.path.append(return_lib_path())
from transition_api_lib import Transition

missing_credentials = "Please enter your username and password."
invalid_credentials = "Bad username or password."
popup_title = "Invalid loggin credentials"

class Login(QDialog):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'login_dialog.ui'), self)
        self.config = Transition.get_configurations()
        self.show()

        self.buttonBox.accepted.connect(self.onConnectButtonClicked)
        self.buttonBox.rejected.connect(self.reject)
        self.comboBox.addItems(self.config['URL'].keys())


    def onConnectButtonClicked(self):
        try:
            print("Connecting...")
            Transition.set_url(self.comboBox.currentText())
            Transition.set_username(self.usernameEdit.text())

            result = Transition.get_token(self.usernameEdit.text(), self.passwordEdit.text())
            if result.status_code == 200:
                print("Successfully connected to API")
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid login credentials", "Bad username or password.")
                
        except ValueError:
            QMessageBox.warning(self, "Missing credentials", "Please enter your username and password.")

