
from qgis.PyQt import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QDialog

import os
import requests
from pyTransition.transition import Transition

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
                QMessageBox.warning(self, self.tr("Invalid loggin credentials"), self.tr("Please enter your username and password."))
                return
            
            Transition.set_url(self.urlEdit.text())
            token = Transition.request_token(self.usernameEdit.text(), self.passwordEdit.text())
            Transition.set_token(token)
            
            self.settings.setValue("username", self.usernameEdit.text())
            self.settings.setValue("url", self.urlEdit.text())
            self.settings.setValue("token", token)
            self.settings.setValue("keepConnection", self.loginCheckbox.isChecked())
            
            self.accept()
            
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(None, self.tr("Unable to connect to server"), self.tr("Unable to connect to your Transition server.\nMake sure you provided the right server URL and that the server is up."))
            self.close()
            self.closeWidget.emit()
        except requests.exceptions.HTTPError as error:
            self.iface.messageBar().pushCritical('Error', str(error.response.text))
        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

