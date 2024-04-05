
from qgis.PyQt import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFormLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QComboBox, QTimeEdit, QPushButton, QDialogButtonBox

import os
import requests
from transition_lib.transition import Transition

missing_credentials = "Please enter your username and password."
popup_title = "Invalid loggin credentials"

class LoginDialog(QDialog):
    closeWidget = pyqtSignal()
    
    def __init__(self, iface, settings, parent = None) -> None:
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'login_dialog.ui'), self)
        self.settings = settings
        self.iface = iface
        self.show()

        self.urlEdit.setText("http://localhost:8080")

        self.buttonBox.accepted.connect(self.onConnectButtonClicked)
        self.buttonBox.rejected.connect(self.reject)


    def onConnectButtonClicked(self):
        try:
            if self.usernameEdit.text() == "" or self.passwordEdit.text() == "":
                QMessageBox.warning(self, popup_title, missing_credentials)
                return
            self.settings.setValue("username", self.usernameEdit.text())
            self.settings.setValue("url", self.urlEdit.text())
            Transition.set_url(self.urlEdit.text())
            token = Transition.request_token(self.usernameEdit.text(), self.passwordEdit.text())
            self.settings.setValue("token", token)
            Transition.set_token(token)
            self.accept()
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(None, "Unable to connect to server", "Unable to connect to your Transition server.\nMake sure you provided the right server URL and that the server is up.")
            self.close()
            self.closeWidget.emit()
        except requests.exceptions.HTTPError as error:
            self.iface.messageBar().pushCritical('Error', str(error.response.text))
        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

