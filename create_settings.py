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
from qgis.PyQt.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QVBoxLayout

from pyTransition import Transition

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

