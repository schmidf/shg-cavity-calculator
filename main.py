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
import sys
import json
import logging
from PyQt5 import QtWidgets, QtCore
import pyqtgraph

import numpy as np

import cavity
import widgets
import dialogs

#import shg_efficiency

DEFAULT_CAVITY_CONFIG = "default_cavity_config.json"
LICENSEPATH = "COPYING"

class MainWindow(QtWidgets.QMainWindow):
    """Main application class."""

    def switch_cavity_setup(self, brewster):
        """Switch between Brewster-cut and plane crystal.

        :param brewster: True for a Brewster-cut crystal, False for a plane crystal
        """
        self.cavity_parameters["Brewster"] = brewster
        self.update_cavity_mode()

    def update_cavity_mode(self):
        """Calculate the cavity mode and update the first three plots."""
        try:
            result = cavity.solve_cavity_s_range(self.cavity_parameters)
        except ValueError:
            self.output_widget.display_result(None)
            logging.info("Cavity unstable for current parameters.")
            return

        self.update_plots(result)

        s_min, s_max = cavity.s_bounds(self.cavity_parameters)
        self.input_widget.update_s_parameter_range(s_min+100E-6,
                                                   s_max-100E-6)

        if self.cavity_parameters["s"] < s_min or self.cavity_parameters["s"] > s_max:
            # Set the vertical lines roughly in the middle of the plots
            self.update_s(1E3*(s_min+s_max)/2)
            self.input_widget.update_parameters(self.cavity_parameters)
        else:
            self.update_s(1E3*self.cavity_parameters["s"])

    def update_s(self, value):
        """Change the distance s between the focussing mirrors and the crystal surface and move the
        vertical lines in the first three plots.

        :param value: The value to set s to in mm.
        """
        self.cavity_parameters["s"] = value/1E3
        try:
            result = cavity.solve_cavity(self.cavity_parameters)
        except ValueError:
            self.output_widget.display_result(None)
            logging.info("Cavity unstable for current s value.")
            return

        self.output_widget.display_result(result)

        self.update_s_lines(self.cavity_parameters["s"])

    def update_angle(self, value):
        """Change the mirror incidence angle and update the first three plots.

        :param value: The value in degree to set the angle to.
        """
        self.cavity_parameters["alpha"] = 2*np.pi*value/360.
        self.update_cavity_mode()

    def update_mirror_radius(self, value):
        """Change the mirror radius of curvature and update the first three plots.

        :param value: The value in mm to set the radius of curvature to.
        """
        self.cavity_parameters["f"] = value*1E-3/2.
        self.update_cavity_mode()

    def update_crystal_length(self, value):
        """Change the length l of the nonlinear crystal and update the first three plots.

        :param value: The value in mm to set the length to.
        """
        self.cavity_parameters["l"] = value*1E-3
        self.update_cavity_mode()

    def update_distance_secondary_focus(self, value):
        """Change the distance v between the focussing mirror and the secondary focus and update
        the first three plots.

        :param value: The value in mm to set the distance to.
        """
        self.cavity_parameters["v"] = value*1E-3
        self.update_cavity_mode()

    def update_wavelength(self, value):
        """Change the wavelength to the value obtained from the input field and update the first
        three plots.

        :param value: The value in nm to set the wavelength to.
        """
        self.cavity_parameters["wavelength"] = value*1E-9
        self.update_cavity_mode()

    def update_refractive_index(self, value):
        """Change the crystal refractive index to the value obtained from the input field and update
        the first three plots.

        :param value: The value to set the refractive index to.
        """
        self.cavity_parameters["eta"] = value
        self.update_cavity_mode()

    def update_b_parameter(self, value):
        """Change the crystal B parameter (Boyd-Kleinman) to the value obtained from the input field
        and update the first three plots.

        :param value: The value to set the B parameter to.
        """
        self.cavity_parameters["B"] = value
        self.update_cavity_mode()

    def load_cavity_parameters(self, filename):
        """Load cavity parameters from a json file and update the UI widgets.

        :param filename: Path to the json configuration file.
        """
        try:
            with open(filename) as config_file:
                self.cavity_parameters = json.load(config_file)
        except FileNotFoundError:
            logging.error("Cavity configuration file not found: %s", filename)

        self.input_widget.update_parameters(self.cavity_parameters)
        self.setup_widget.update_parameters(self.cavity_parameters)

    def load_default_cavity_parameters(self):
        """Load the default cavity parameters, and update the UI widgets.
        """
        self.load_cavity_parameters(DEFAULT_CAVITY_CONFIG)
        self.update_cavity_mode()

    def save_cavity_parameters(self, filename):
        """Save cavity parameters to a json file.

        :param filename: Path to the json configuration file.
        """
        try:
            with open(filename, "w") as config_file:
                json.dump(self.cavity_parameters, config_file)
        except PermissionError as error:
            logging.error("Could not write configuration file: %s", error)

    def open_parameter_file_dialog(self):
        """Open a QFileDialog and load a saved cavity configuration from the chosen file."""
        cavity_config_path = QtWidgets.QFileDialog.getOpenFileName(
            filter="Configuration files (*.json)")[0]
        if cavity_config_path == "":
            logging.info("No file chosen for loading cavity config.")
            return
        self.load_cavity_parameters(cavity_config_path)
        self.update_cavity_mode()

    def save_parameter_file_dialog(self):
        """Open a QFileDialog and save the current cavity configuration to the chosen file."""
        cavity_config_path = QtWidgets.QFileDialog.getSaveFileName(
            filter="Configuration files (*.json)")[0]
        if cavity_config_path == "":
            logging.info("No file chosen for saving cavity config.")
            return
        self.save_cavity_parameters(cavity_config_path)

    def init_plots(self):
        """Initialize the plots in the graphics_layout_widget."""
        crystal_focus_plot = self.graphics_layout_widget.addPlot(row=0, col=0)
        crystal_focus_plot.addLegend()
        self.crystal_waist_curve_tangential = crystal_focus_plot.plot(
            name="tangential", pen=pyqtgraph.mkPen(color="r"))
        self.crystal_waist_curve_sagittal = crystal_focus_plot.plot(
            name="sagittal", pen=pyqtgraph.mkPen(color="g"))
        self.crystal_focus_s_line = pyqtgraph.InfiniteLine()
        crystal_focus_plot.addItem(self.crystal_focus_s_line)
        crystal_focus_plot.setTitle("Crystal focus beam waists")
        crystal_focus_plot.setLabels(
            left="Beam waist (µm)", bottom="Distance focusing mirror to crystal surface (mm)")

        crystal_ellipticity_plot = self.graphics_layout_widget.addPlot(row=0, col=1)
        self.crystal_ellipticity_curve = crystal_ellipticity_plot.plot(
            pen=pyqtgraph.mkPen(color="r"))
        self.crystal_ellipticity_s_line = pyqtgraph.InfiniteLine()
        crystal_ellipticity_plot.addItem(self.crystal_ellipticity_s_line)
        crystal_ellipticity_plot.setTitle("Crystal focus ellipticity")
        crystal_ellipticity_plot.setLabels(
            left="Ellipticity", bottom="Distance focusing mirror to crystal surface (mm)")

        collimated_ellipticity_plot = self.graphics_layout_widget.addPlot(row=1, col=0)
        self.collimated_ellipticity_curve = collimated_ellipticity_plot.plot(
            pen=pyqtgraph.mkPen(color="r"))
        self.collimated_ellipticity_s_line = pyqtgraph.InfiniteLine()
        collimated_ellipticity_plot.addItem(self.collimated_ellipticity_s_line)
        collimated_ellipticity_plot.setTitle("Collimated arm ellipticity")
        collimated_ellipticity_plot.setLabels(
            left="Ellipticity", bottom="Distance focusing mirror to crystal surface (mm)")

    def update_plots(self, result_dict):
        """Update the first three plots showing beam waists and ellipticities vs. the distance s
        between focussing mirror and crystal.

        :param result_dict: A dict containing the parameters of the cavity eigenmodes (see
                            cavity.solve_cavity_s_range() docstring for details)
        """
        self.crystal_waist_curve_tangential.setData(
            1E3*np.array(result_dict["s values"]),
            1E6*np.array(result_dict["tangential waists crystal"]))
        self.crystal_waist_curve_sagittal.setData(
            1E3*np.array(result_dict["s values"]),
            1E6*np.array(result_dict["sagittal waists crystal"]))
        self.crystal_ellipticity_curve.setData(
            1E3*np.array(result_dict["s values"]),
            np.array(result_dict["ellipticities crystal"]))
        self.collimated_ellipticity_curve.setData(
            1E3*np.array(result_dict["s values"]),
            np.array(result_dict["ellipticities collimated"]))

    def update_s_lines(self, s_value):
        """Update the position of the vertical lines in the first three plots.

        :param s_value: The position of the vertical lines in m.
        """
        self.crystal_focus_s_line.setValue(1E3*s_value)
        self.crystal_ellipticity_s_line.setValue(1E3*s_value)
        self.collimated_ellipticity_s_line.setValue(1E3*s_value)

    def closeEvent(self, e):
        """QCloseEvent handler to handle application shutdown.

        :param e: QCloseEvent sent to the widget.
        """
        # Save window size and position
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        e.accept()

    def _setup_logging(self):
        """Configure the application logging setup."""
        logging.basicConfig(level=logging.INFO)

    def _setup_ui(self):
        """Set up the application's ui elements."""
        self.setWindowTitle("SHG Cavity Calculator")

        central_widget = QtWidgets.QWidget()
        horizontal_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(horizontal_layout)
        self.setCentralWidget(central_widget)

        vertical_layout = QtWidgets.QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        horizontal_layout.addWidget(self.graphics_layout_widget)
        vertical_layout.addWidget(self.setup_widget)
        vertical_layout.addWidget(self.output_widget)
        vertical_layout.addWidget(self.input_widget)

        vertical_layout.addStretch()


    def _create_menus(self):
        """Create the application menu bar and its entries."""
        self.menu_file.addAction(self.action_load_cavity_config)
        self.menu_file.addAction(self.action_save_cavity_config)
        self.menu_file.addAction(self.action_load_default_config)
        self.menu_help.addAction(self.action_about)
        self.menuBar().addMenu(self.menu_file)
        self.menuBar().addMenu(self.menu_help)

    def __init__(self):
        self._setup_logging()
        super().__init__()

        self.graphics_layout_widget = pyqtgraph.GraphicsLayoutWidget()
        self.init_plots()
        self.setup_widget = widgets.SetupWidget(self, True)
        self.output_widget = widgets.OutputWidget(self)
        self.input_widget = widgets.InputWidget(self)

        self._setup_ui()

        self.menu_file = QtWidgets.QMenu("File")
        self.menu_help = QtWidgets.QMenu("Help")

        self.action_load_cavity_config = QtWidgets.QAction("Load Cavity Config")
        self.action_save_cavity_config = QtWidgets.QAction("Save Cavity Config")
        self.action_load_default_config = QtWidgets.QAction("Load Default Cavity Config")
        self.action_about = QtWidgets.QAction("About")
        self.about_dialog = dialogs.AboutDialog(LICENSEPATH)
        self._create_menus()

        # Load default parameters
        self.cavity_parameters = {}
        self.load_cavity_parameters(DEFAULT_CAVITY_CONFIG)

        # Load previous window size and position
        self.settings = QtCore.QSettings("MPQ", "shg-cavity-calculator")
        geometry = self.settings.value("geometry")
        windowState = self.settings.value("windowState")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if windowState is not None:
            self.restoreState(windowState)

        # Connect UI elements
        self.action_load_default_config.triggered.connect(self.load_default_cavity_parameters)
        self.action_load_cavity_config.triggered.connect(self.open_parameter_file_dialog)
        self.action_save_cavity_config.triggered.connect(self.save_parameter_file_dialog)
        self.action_about.triggered.connect(self.about_dialog.exec)

        self.update_cavity_mode()

        self.show()

if __name__ == "__main__":
    qt_app = QtWidgets.QApplication(sys.argv)

    MAIN_WINDOW = MainWindow()

    sys.exit(qt_app.exec_())
