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
"""This module contains the QtWidgets that make up the application GUI."""
from PyQt5 import QtWidgets, QtSvg, QtGui
import numpy as np

BREWSTER_CAVITY_IMAGE = "Cavity_brewster.svg"
PLANE_CAVITY_IMAGE = "Cavity_plane.svg"

class ImageWidget(QtSvg.QSvgWidget):
    """Subclass of QSvgWidget which allows setting a custom width with fixed aspect ratio."""

    def __init__(self, filename):
        """Construct a new ImageWidget.

        :param filename: filename of the svg file to be displayed
        """
        super().__init__(filename)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

class SetupWidget(QtWidgets.QGroupBox):
    """Widget for displaying and modifying the cavity setup."""

    def update_parameters(self, cavity_parameters):
        """Display the chosen setup in the widget.

        :param cavity_parameters: A dict containing the cavity parameters. See cavity.py for
                                  details.
        """
        if cavity_parameters["Brewster"]:
            self.update_image(BREWSTER_CAVITY_IMAGE)
            self.radio_button_brewster.setChecked(True)
            self.radio_button_plane.setChecked(False)
        else:
            self.update_image(PLANE_CAVITY_IMAGE)
            self.radio_button_brewster.setChecked(False)
            self.radio_button_plane.setChecked(True)

    def update_image(self, filename):
        """Load and display a svg file in the ImageWidget.

        :param filename: Filename of the svg file.
        """
        self.svg_widget.load(filename)

    def switch_cavity_setup(self):
        """Switch between Brewster-cut and plane crystal depending on the selected UI element."""
        if self.radio_button_brewster.isChecked():
            self.update_image(BREWSTER_CAVITY_IMAGE)
            self.app.switch_cavity_setup(True)
        elif self.radio_button_plane.isChecked():
            self.update_image(PLANE_CAVITY_IMAGE)
            self.app.switch_cavity_setup(False)

    def _setup_ui(self):
        """Add the required widgets and set up layouts."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.svg_widget)
        layout.addWidget(self.radio_button_brewster)
        layout.addWidget(self.radio_button_plane)


    def __init__(self, application, brewster):
        """Initialize a SetupWidget.

        :param application: reference to the main application
        :param brewster: True for a Brewster-cut crystal, False for a plane crystal
        """
        self.app = application
        super().__init__("Setup")
        self.radio_button_brewster = QtWidgets.QRadioButton("Brewster-Cut Crystal")
        self.radio_button_plane = QtWidgets.QRadioButton("Plane Crystal")
        if brewster:
            filename = BREWSTER_CAVITY_IMAGE
            self.radio_button_brewster.setChecked(True)
            self.radio_button_plane.setChecked(False)
        else:
            filename = PLANE_CAVITY_IMAGE
            self.radio_button_brewster.setChecked(False)
            self.radio_button_plane.setChecked(True)
        self.svg_widget = ImageWidget(filename)
        self._setup_ui()

        # Connect UI widget signals
        self.radio_button_brewster.clicked.connect(self.switch_cavity_setup)
        self.radio_button_plane.clicked.connect(self.switch_cavity_setup)


class InputWidget(QtWidgets.QGroupBox):
    """Widget for user input."""

    def update_s_parameter_range(self, s_min, s_max):
        """Update the minimum and maximum allowed values for the s parameter widget.

        :param s_min: the minimum value of s in m
        :param s_max: the maximum value of s in m
        """
        blocked = self.spin_box_s_parameter.blockSignals(True)
        self.spin_box_s_parameter.setMinimum(s_min*1E3)
        self.spin_box_s_parameter.setMaximum(s_max*1E3)
        self.spin_box_s_parameter.blockSignals(blocked)

    def update_parameters(self, cavity_parameters):
        """Set the input widgets to the specified values.

        :param cavity_parameters: A dict containing the cavity parameters. See cavity.py for
                                  details.
        """
        blocked = self.spin_box_angle.blockSignals(True)
        self.spin_box_angle.setValue(360*cavity_parameters["alpha"]/2/np.pi)
        self.spin_box_angle.blockSignals(blocked)
        blocked = self.spin_box_mirror_radius.blockSignals(True)
        self.spin_box_mirror_radius.setValue(2E3*cavity_parameters["f"])
        self.spin_box_mirror_radius.blockSignals(blocked)
        blocked = self.spin_box_crystal_length.blockSignals(True)
        self.spin_box_crystal_length.setValue(1E3*cavity_parameters["l"])
        self.spin_box_crystal_length.blockSignals(blocked)
        blocked = self.spin_box_secondary_focus.blockSignals(True)
        self.spin_box_secondary_focus.setValue(1E3*cavity_parameters["v"])
        self.spin_box_secondary_focus.blockSignals(blocked)
        blocked = self.spin_box_wavelength.blockSignals(True)
        self.spin_box_wavelength.setValue(1E9*cavity_parameters["wavelength"])
        self.spin_box_wavelength.blockSignals(blocked)
        blocked = self.spin_box_refractive_index.blockSignals(True)
        self.spin_box_refractive_index.setValue(cavity_parameters["eta"])
        self.spin_box_refractive_index.blockSignals(blocked)
        blocked = self.spin_box_b_parameter.blockSignals(True)
        self.spin_box_b_parameter.setValue(cavity_parameters["B"])
        self.spin_box_b_parameter.blockSignals(blocked)
        blocked = self.spin_box_s_parameter.blockSignals(True)
        self.spin_box_s_parameter.setValue(1E3*cavity_parameters["s"])
        self.spin_box_s_parameter.blockSignals(blocked)

    def _setup_ui(self):
        """Add the required widgets and set up layouts."""
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Mirror incidence angle (°)"), 0, 0)
        layout.addWidget(self.spin_box_angle, 0, 1)
        self.spin_box_angle.setKeyboardTracking(False)
        self.spin_box_angle.setMaximum(90)

        layout.addWidget(QtWidgets.QLabel("Mirror radius of curvature (mm)"), 1, 0)
        layout.addWidget(self.spin_box_mirror_radius, 1, 1)
        self.spin_box_mirror_radius.setKeyboardTracking(False)
        self.spin_box_mirror_radius.setMaximum(200)

        layout.addWidget(QtWidgets.QLabel("Beam length inside crystal (mm)"), 3, 0)
        layout.addWidget(self.spin_box_crystal_length, 3, 1)
        self.spin_box_crystal_length.setKeyboardTracking(False)

        layout.addWidget(
            QtWidgets.QLabel("Distance focusing mirror to secondary focus (mm)"), 4, 0)
        layout.addWidget(self.spin_box_secondary_focus, 4, 1)
        self.spin_box_secondary_focus.setKeyboardTracking(False)
        self.spin_box_secondary_focus.setMaximum(500)

        layout.addWidget(QtWidgets.QLabel("Fundamental wavelength (nm)"), 5, 0)
        layout.addWidget(self.spin_box_wavelength, 5, 1)
        self.spin_box_wavelength.setKeyboardTracking(False)
        self.spin_box_wavelength.setMinimum(400)
        self.spin_box_wavelength.setMaximum(10000)

        layout.addWidget(QtWidgets.QLabel("Fundamental refractive index"), 6, 0)
        layout.addWidget(self.spin_box_refractive_index, 6, 1)
        self.spin_box_refractive_index.setKeyboardTracking(False)
        self.spin_box_refractive_index.setMaximum(5)
        self.spin_box_refractive_index.setMinimum(1)
        self.spin_box_refractive_index.setDecimals(3)
        self.spin_box_refractive_index.setSingleStep(0.01)

        layout.addWidget(QtWidgets.QLabel("Crystal B parameter"), 7, 0)
        layout.addWidget(self.spin_box_b_parameter, 7, 1)
        self.spin_box_b_parameter.setKeyboardTracking(False)
        self.spin_box_b_parameter.setDecimals(1)

        layout.addWidget(
            QtWidgets.QLabel("Distance focusing mirror to crystal surface (mm)"), 8, 0)
        layout.addWidget(self.spin_box_s_parameter, 8, 1)
        self.spin_box_s_parameter.setKeyboardTracking(False)
        self.spin_box_s_parameter.setSingleStep(0.1)

    def __init__(self, application):
        """Initialize an InputWidget.

        :param application: reference to the main application
        """
        self.app = application
        super().__init__("Input")
        self.spin_box_angle = QtWidgets.QDoubleSpinBox()
        self.spin_box_mirror_radius = QtWidgets.QDoubleSpinBox()
        self.spin_box_crystal_length = QtWidgets.QDoubleSpinBox()
        self.spin_box_secondary_focus = QtWidgets.QDoubleSpinBox()
        self.spin_box_wavelength = QtWidgets.QDoubleSpinBox()
        self.spin_box_refractive_index = QtWidgets.QDoubleSpinBox()
        self.spin_box_b_parameter = QtWidgets.QDoubleSpinBox()
        self.spin_box_s_parameter = QtWidgets.QDoubleSpinBox()
        self._setup_ui()

        # Connect UI widget signals
        self.spin_box_angle.valueChanged.connect(self.app.update_angle)
        self.spin_box_mirror_radius.valueChanged.connect(self.app.update_mirror_radius)
        self.spin_box_crystal_length.valueChanged.connect(self.app.update_crystal_length)
        self.spin_box_secondary_focus.valueChanged.connect(self.app.update_distance_secondary_focus)
        self.spin_box_wavelength.valueChanged.connect(self.app.update_wavelength)
        self.spin_box_refractive_index.valueChanged.connect(self.app.update_refractive_index)
        self.spin_box_b_parameter.valueChanged.connect(self.app.update_b_parameter)
        self.spin_box_s_parameter.valueChanged.connect(self.app.update_s)

class OutputWidget(QtWidgets.QGroupBox):
    """Widget for calculated output."""

    def display_result(self, result):
        """Display the calculated parameters.

        :param result: Dict containing the calculated values or None if the cavity is unstable.
                       See documentation of cavity.solve_cavity for details.
        """
        if result is None:
            self.label_crystal_focus.setText("Cavity unstable\n\n")
            self.label_collimated_focus.setText("Cavity unstable\n\n")
            self.label_fsr.setText("Cavity unstable")
            return

        crystal_string = "wt = {:.2f} µm\tbt = {:.2f} mm\tξt={:.3f}\n"\
                         "ws = {:.2f} µm\tbs = {:.2f} mm\tξs={:.3f}\nellipticity = {:.2f}"
        self.label_crystal_focus.setText(crystal_string.format(
            result["tangential waist crystal"]*1E6,
            result["tangential confocal parameter crystal"]*1E3,
            result["tangential focusing parameter"],
            result["sagittal waist crystal"]*1E6,
            result["sagittal confocal parameter crystal"]*1E3,
            result["sagittal focusing parameter"],
            result["ellipticity crystal"]))

        collimated_string = "wt = {:.2f} µm\tbt = {:.2f} mm\nws = {:.2f} µm\tbs = {:.2f} mm\n"\
                            "ellipticity = {:.2f}"

        self.label_collimated_focus.setText(collimated_string.format(
            result["tangential waist collimated"]*1E6,
            result["tangential confocal parameter collimated"]*1E3,
            result["sagittal waist collimated"]*1E6,
            result["sagittal confocal parameter collimated"]*1E3,
            result["ellipticity collimated"]))

        self.label_fsr.setText("FSR = {:.1f} MHz".format(result["free spectral range"]/1E6))

    def _setup_ui(self):
        """Add the required widgets and set up layouts."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        headline_font = QtGui.QFont()
        headline_font.setBold(True)
        label_crystal = QtWidgets.QLabel("Crystal:")

        label_crystal.setFont(headline_font)
        layout.addWidget(label_crystal)
        layout.addWidget(self.label_crystal_focus)

        label_collimated = QtWidgets.QLabel("Collimated arm:")
        label_collimated.setFont(headline_font)
        layout.addWidget(label_collimated)
        layout.addWidget(self.label_collimated_focus)

        label_fsr_headline = QtWidgets.QLabel("Free spectral range:")
        label_fsr_headline.setFont(headline_font)
        layout.addWidget(label_fsr_headline)
        layout.addWidget(self.label_fsr)

    def __init__(self, application):
        """Initialize an OutputWidget.

        :param application: reference to the main application
        """
        self.app = application
        super().__init__("Output")
        self.label_crystal_focus = QtWidgets.QLabel()
        self.label_collimated_focus = QtWidgets.QLabel()
        self.label_fsr = QtWidgets.QLabel()
        self._setup_ui()
