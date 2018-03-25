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
"""This module contains functions for Gaussian beam calculations.
"""
import numpy as np

def propagate(q_parameter, matrix, eta2, eta1):
    """Propagate a beam with given beam parameter through an optical system described by a transfer
    matrix.

    :param q_parameter: The complex beam parameter q.
    :param matrix: The transfer matrix of the optical system.
    :param eta1: The refractive index of the medium at the initial position.
    :param eta2: The refractive index of the medium at the final position.
    :returns: The complex beam parameter q after propagation.
    """
    return eta2*(matrix[0][0]*q_parameter/eta1 + matrix[0][1])/(matrix[1][0]*q_parameter/eta1 +
                                                                matrix[1][1])
def get_r(q_parameter):
    """Calculate the wavefront curvature for a given beam parameter.

    :param q_parameter: The complex beam parameter q.
    """
    return np.real(q_parameter**-1)**-1

def get_w(q_parameter, eta, wavelength):
    """Calculate the beam waist for a given beam parameter, refractive index, and wavelength.

    :param eta: The refractive index of the medium at the location of the waist.
    :param q_parameter: The complex beam parameter q.
    :param wavelength: The wavelength of the radiation.
    """
    inner = -wavelength/(np.pi*eta*np.imag(q_parameter**-1))
    if inner < 0:
        return 0
    return np.sqrt(inner)

def get_b(q_parameter):
    """Calculate the confocal parameter for a given beam parameter.

    :param q_parameter: The complex beam parameter q.
    """
    return -2/np.imag(q_parameter**-1)

def get_m(matrix):
    """ Calculate the m value of a given transfer matrix. The resonator is stable for abs(m) < 1.

    :param matrix: The matrix for which the m value should be calculated.
    """
    return (matrix[0][0] + matrix[1][1])/2

def calculate_eigenmode(matrix, eta):
    """Calculate the complex beam parameter corresponding to the eigenmode of an optical system
    described by a transfer matrix.

    :param matrix: The transfer matrix.
    :param eta: the refractive index at the start/end position of the beam path
    """
    return (2*matrix[0][1]*eta)/(-matrix[0][0] + matrix[1][1] + np.sqrt(
        (np.complex(-2 + matrix[0][0] + matrix[1][1])*(2 + matrix[0][0] + matrix[1][1]))))
