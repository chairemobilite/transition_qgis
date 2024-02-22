import os
import sys
import configparser
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
        self.loadConfig()
        self.show()

        self.usernameEdit.disconnect()
        self.passwordEdit.disconnect()

        self.usernameEdit.editingFinished.connect(self.onUsernameEditTextChanged)
        self.passwordEdit.editingFinished.connect(self.onPasswordEditTextChanged)

        self.buttonBox.accepted.connect(self.onConnectButtonClicked)
        self.buttonBox.rejected.connect(self.reject)

        
    def loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if not os.path.isfile(self.config_path):
            self.config['credentials'] = {
                'username': '',
                'token': ''
            }
            self.config['URL'] = {
                'dev': 'http://localhost:8080/',
                'prod': ''
            }
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read('config.ini')

    def saveConfig(self):
        print("Saving config")
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def onUsernameEditTextChanged(self):
        os.environ['TRANSITION_USERNAME'] = self.usernameEdit.text()
        self.config['credentials']['username'] = os.environ['TRANSITION_USERNAME']


    def onPasswordEditTextChanged(self):
        os.environ['TRANSITION_PASSWORD'] = self.passwordEdit.text()

    def onConnectButtonClicked(self):
        try:
            print("Connecting...")
            result = Transition.get_token()
            if result.status_code == 200:
                self.config['credentials']['token'] = result.text
                self.saveConfig()
                print("Successfully connected to API")
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid login credentials", "Bad username or password.")
                
        except ValueError:
            QMessageBox.warning(self, "Missing credentials", "Please enter your username and password.")

