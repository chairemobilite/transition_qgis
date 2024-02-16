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
        self.show()
        self.transition_lib = Transition()
        self.usernameEdit.disconnect()
        self.passwordEdit.disconnect()
        self.usernameEdit.editingFinished.connect(self.on_usernameEdit_textChanged)

        self.passwordEdit.editingFinished.connect(self.on_passwordEdit_textChanged)

        self.connectButton.clicked.connect(self.onConnectButtonClicked)


    def on_usernameEdit_textChanged(self):
        os.environ['TRANSITION_USERNAME'] = self.usernameEdit.text()

    def on_passwordEdit_textChanged(self):
        os.environ['TRANSITION_PASSWORD'] = self.passwordEdit.text()


    def onConnectButtonClicked(self):
        try:
            print("Connecting...")
            result = self.transition_lib.call_api()
            print(result)
            if result.status_code == 200:
                print("Successfully connected to API")
                # QMessageBox.information(self, "Login Success", "Successfully connected to API")
                self.accept()

            else:
                QMessageBox.warning(self, "Invalid loggin credentials", "Bad username or password.")
                
        except ValueError:
            QMessageBox.warning(self, "Missing credentials", "Please enter your username and password.")

    # on exit, close the dialog
    def closeEvent(self, event):
        event.accept()


        