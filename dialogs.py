# Copyright (C) 2018  Fabian Schmid (fabian.schmid@mpq.mpg.de)
# This file is part of shg-cavity-calculator
#
# shg-cavity-calculator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# shg-cavity-calculator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# shg-cavity-calculator.  If not, see <https://www.gnu.org/licenses/>.
"""This modules contains dialog windows used in the cavity-calculator program."""
import logging
from PyQt5 import QtWidgets, QtGui

class LicenseDialog(QtWidgets.QDialog):
    """Subclass of QDialog for displaying the application's license."""

    def __init__(self, licensepath):
        """Create a license dialog window.

        :param licensepath: path to the license file to be shown
        """
        super().__init__()
        self.setWindowTitle("License")

        try:
            with open(licensepath) as text:
                self.license_text = text.read()
        except FileNotFoundError as error:
            logging.error("Could not find license file. FileNotFoundError: %s", error)
            self.license_text = "License text file not found"

        self.layout = QtWidgets.QVBoxLayout()

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(self.license_text)

        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)

class AboutDialog(QtWidgets.QDialog):
    """Subclass of QDialog for displaying an about window."""

    def __init__(self, licensepath):
        """Create an about window.

        :param licensepath: path to the license file to be shown in the license information window
        """
        super().__init__()
        self.setWindowTitle("About shg-cavity-calculator")

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.version_label = QtWidgets.QLabel("shg-cavity-calculator 0.1")
        version_font = QtGui.QFont()
        version_font.setBold(True)
        version_font.setPointSize(14)
        self.version_label.setFont(version_font)
        self.layout.addWidget(self.version_label)
        self.author_label = QtWidgets.QLabel("Copyright (C)  2018 Fabian Schmid")
        self.layout.addWidget(self.author_label)

        self.button_license = QtWidgets.QPushButton("License")
        self.layout.addWidget(self.button_license)

        self.license_dialog = LicenseDialog(licensepath)

        self.button_license.clicked.connect(self.license_dialog.exec)
