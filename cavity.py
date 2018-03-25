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
"""This module contains functions for calculating properties of a bow-tie SHG cavity. The cavity
is described by a dict containing the following entries:

* f: Focal length of the focusing mirrors (assumed to be equal)
* l: Length of the nonlinear crystal
* v: Distance between the focusing mirrors and the crystal surface
* s: Distance between the focusing mirrors and the secondary focus
* eta: Refractive index of the nonlinear crystal
* alpha: Angle of incidence on the cavity mirrors
* wavelength: Wavelength of the fundamental radiation
* Brewster: Whether the crystal is Brewster-cut or plane
"""
# pylint: disable=invalid-name
import copy
import numpy as np
import gaussian_beam

def s_bounds_tangential(cavity_parameters):
    """Return the minimum and maximum distance between the focusing mirrors and the crystal
    surface s for which the resonator is stable in the tangential plane.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    if cavity_parameters["Brewster"]:
        s1 = -(l/(2*eta**3)) + f*np.cos(alpha)
        s2 = -(l/(2*eta**3)) + (f*v)/(-f + v*np.cos(alpha)**-1)
    else:
        s1 = -l/(2.*eta) + f*np.cos(alpha)
        s2 = -l/(2.*eta) + (f*v)/(-f + v*np.cos(alpha)**-1)

    return min(s1, s2), max(s1, s2)

def s_bounds_sagittal(cavity_parameters):
    """Return the minimum and maximum distance between the focusing mirrors and the crystal
    surface s for which the resonator is stable in the sagittal plane.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    s1 = -l/(2*eta) + f*np.cos(alpha)**-1
    s2 = -l/(2*eta) + f*v/(-f+v*np.cos(alpha))
    return min(s1, s2), max(s1, s2)

def s_bounds(cavity_parameters):
    """Return the minimum and maximum distance between the focusing mirrors and the crystal
    surface s for which the resonator is stable in both planes.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    s_t_min, s_t_max = s_bounds_tangential(cavity_parameters)
    s_s_min, s_s_max = s_bounds_sagittal(cavity_parameters)

    return max(s_t_min, s_s_min), min(s_t_max, s_s_max)

def construct_tangential_matrix(cavity_parameters):
    """Construct a transfer matrix for the tangential plane of a bow-tie resonator.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    s = cavity_parameters["s"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    if cavity_parameters["Brewster"]:
        A = (f**2*eta**3 - f*(l + 2*(s + v)*eta**3)*np.cos(alpha)**-1
             + v*(l + 2*s*eta**3)*np.cos(alpha)**-2)/(f**2*eta**3)
        B = ((2*f*eta**3 - (l + 2*s*eta**3)*np.cos(alpha)**-1)*(f*(l + 2*(s + v)*eta**3)
             - v*(l + 2*s*eta**3)*np.cos(alpha)**-1))/(2*f**2*eta**4)
        C = - (2*np.cos(alpha)**-1 * (f-v*np.cos(alpha)**-1))/(f**2*eta**2)
        D = (f**2*eta**3 - f*(l + 2*(s + v)*eta**3)*np.cos(alpha)**-1
             + v*(l + 2*s*eta**3)*np.cos(alpha)**-2)/(f**2*eta**3)
    else:
        A = (f**2*eta - f*(l + 2*(s + v)*eta)*np.cos(alpha)**-1
             + v*(l + 2*s*eta)*np.cos(alpha)**-2)/(f**2*eta)
        B = ((2*f*eta - (l + 2*s*eta)*np.cos(alpha)**-1)*(f*(l + 2*(s + v)*eta)
             - v*(l + 2*s*eta)*np.cos(alpha)**-1))/(2.*f**2*eta**2)
        C = (-2*np.cos(alpha)**-1*(f - v*np.cos(alpha)**-1))/f**2
        D = (f**2*eta - f*(l + 2*(s + v)*eta)*np.cos(alpha)**-1
             + v*(l + 2*s*eta)*np.cos(alpha)**-2)/(f**2*eta)
    return [[A, B], [C, D]]

def construct_sagittal_matrix(cavity_parameters):
    """Construct a transfer matrix for the sagittal plane of a bow-tie resonator.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    s = cavity_parameters["s"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    A = (f**2*eta - f*(l + 2*(s + v)*eta)*np.cos(alpha)
         + v*(l + 2*s*eta)*np.cos(alpha)**2)/(f**2*eta)
    B = ((2*f*eta - (l + 2*s*eta)*np.cos(alpha))*(f*(l + 2*(s + v)*eta)
        - v*(l + 2*s*eta)*np.cos(alpha)))/(2*f**2*eta**2)
    C = (2*np.cos(alpha)*(-f + v*np.cos(alpha)))/f**2
    D = (f**2*eta - f*(l + 2*(s + v)*eta)*np.cos(alpha)
         + v*(l + 2*s*eta)*np.cos(alpha)**2)/(f**2*eta)
    return [[A, B], [C, D]]

def construct_secondary_focus_matrix_tangential(cavity_parameters):
    """Return the transfer matrix between the center of the nonlinear crystal and the location
    of the secondary focus in the tangential plane.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    s = cavity_parameters["s"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    if cavity_parameters["Brewster"]:
        A = (f - v*np.cos(alpha)**-1)/(f*eta)
        B = (f*(l + 2*(s + v)*eta**3) - v*(l + 2*s*eta**3)*np.cos(alpha)**-1)/(2.*f*eta**2)
        C = -(np.cos(alpha)**-1/(f*eta))
        D = eta - ((l + 2*s*eta**3)*np.cos(alpha)**-1)/(2.*f*eta**2)
    else:
        A = 1 - (v*np.cos(alpha)**-1)/f
        B = (f*(l + 2*(s + v)*eta) - v*(l + 2*s*eta)*np.cos(alpha)**-1)/(2.*f*eta)
        C = -(np.cos(alpha)**-1/f)
        D = 1 - ((l + 2*s*eta)*np.cos(alpha)**-1)/(2.*f*eta)
    return [[A, B], [C, D]]

def construct_secondary_focus_matrix_sagittal(cavity_parameters):
    """Return the transfer matrix between the center of the nonlinear crystal and the location
    of the secondary focus in the sagittal plane.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    """
    f = cavity_parameters["f"]
    l = cavity_parameters["l"]
    v = cavity_parameters["v"]
    s = cavity_parameters["s"]
    eta = cavity_parameters["eta"]
    alpha = cavity_parameters["alpha"]
    A = 1 - (v*np.cos(alpha))/f
    B = (f*(l + 2*(s + v)*eta) - v*(l + 2*s*eta)*np.cos(alpha))/(2.*f*eta)
    C = -(np.cos(alpha)/f)
    D = 1 - ((l + 2*s*eta)*np.cos(alpha))/(2.*f*eta)
    return [[A, B], [C, D]]

def solve_cavity(cavity_parameters):
    """Calculate the cavity eigenmode.

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    :returns: A dict with the following entries:
              * tangential waist crystal
              * tangential confocal parameter crystal
              * tangential focusing parameter
              * sagittal waist crystal
              * sagittal confocal parameter crystal
              * sagittal focusing parameter
              * ellipticity crystal
              * tangential waist collimated
              * tangential confocal parameter collimated
              * sagittal waist collimated
              * sagittal confocal parameter collimated
              * ellipticity collimated
    """
    M_t = construct_tangential_matrix(cavity_parameters)
    q_t = gaussian_beam.calculate_eigenmode(M_t, cavity_parameters["eta"])

    M_s = construct_sagittal_matrix(cavity_parameters)
    q_s = gaussian_beam.calculate_eigenmode(M_s, cavity_parameters["eta"])

    s_min, s_max = s_bounds(cavity_parameters)

    if cavity_parameters["s"] < s_min or cavity_parameters["s"] > s_max:
        raise ValueError("Cavity unstable for the supplied s value.")

    w_t_crystal = gaussian_beam.get_w(q_t, cavity_parameters["eta"],
                                      cavity_parameters["wavelength"])
    b_t_crystal = gaussian_beam.get_b(q_t)

    w_s_crystal = gaussian_beam.get_w(q_s, cavity_parameters["eta"],
                                      cavity_parameters["wavelength"])
    b_s_crystal = gaussian_beam.get_b(q_s)

    q_t_collimated = gaussian_beam.propagate(
        q_t, construct_secondary_focus_matrix_tangential(cavity_parameters), 1,
        cavity_parameters["eta"])
    q_s_collimated = gaussian_beam.propagate(
        q_s, construct_secondary_focus_matrix_sagittal(cavity_parameters), 1,
        cavity_parameters["eta"])

    w_t_collimated = gaussian_beam.get_w(q_t_collimated, 1, cavity_parameters["wavelength"])
    b_t_collimated = gaussian_beam.get_b(q_t_collimated)

    w_s_collimated = gaussian_beam.get_w(q_s_collimated, 1, cavity_parameters["wavelength"])
    b_s_collimated = gaussian_beam.get_b(q_s_collimated)

    e_collimated = w_s_collimated/w_t_collimated

    return {"tangential waist crystal":w_t_crystal,
            "tangential confocal parameter crystal":b_t_crystal,
            "tangential focusing parameter":cavity_parameters["l"]/b_t_crystal,
            "sagittal waist crystal":w_s_crystal,
            "sagittal confocal parameter crystal":b_s_crystal,
            "sagittal focusing parameter":cavity_parameters["l"]/b_s_crystal,
            "ellipticity crystal":w_s_crystal/w_t_crystal,
            "tangential waist collimated":w_t_collimated,
            "tangential confocal parameter collimated":b_t_collimated,
            "sagittal waist collimated":w_s_collimated,
            "sagittal confocal parameter collimated":b_s_collimated,
            "ellipticity collimated":e_collimated}

def solve_cavity_s_range(cavity_parameters, s_values=None):
    """Calculate the cavity eigenmode for a range of distances between the focusing mirrors and
    the crystal surfaces (s).

    :param cavity_parameters: Dict containing the cavity parameters (see module docstring for
                              details)
    :param s_values: The s values for which the eigenmode should be calculated. Defaults to
                     np.linspace(s_min+100E-6, s_max-100E-6), where s_min and s_max are the limits
                     of the stability range.
    :returns: A dict with the following entries:
              * tangential waists crystal
              * tangential confocal parameters crystal
              * tangential focusing parameters
              * sagittal waists crystal
              * sagittal confocal parameters crystal
              * sagittal focusing parameters
              * ellipticities crystal
              * tangential waists collimated
              * tangential confocal parameters collimated
              * sagittal waists collimated
              * sagittal confocal parameters collimated
              * ellipticities collimated
              * s values
    """

    parameters = copy.deepcopy(cavity_parameters)  # Don't modify the original dict

    w_t_crystal_values = []
    b_t_crystal_values = []
    xi_t_crystal_values = []

    w_s_crystal_values = []
    b_s_crystal_values = []
    xi_s_crystal_values = []

    ellipticity_crystal_values = []

    w_t_collimated_values = []
    b_t_collimated_values = []

    w_s_collimated_values = []
    b_s_collimated_values = []

    ellipticity_collimated_values = []

    s_values_valid = []

    s_min, s_max = s_bounds(parameters)

    if  (s_max-s_min) < 1E-3 or s_min < 0 or s_max < 0:
        raise ValueError("Cavity unstable for all s values.")

    if s_values is None:
        s_values = np.linspace(s_min+100E-6, s_max-100E-6)
    for s in s_values:
        parameters["s"] = s
        try:
            cavity_results = solve_cavity(parameters)
        except ValueError:
            print("Cavity unstable for s value: {}.".format(s))
            continue

        s_values_valid.append(s)

        w_t_crystal_values.append(cavity_results["tangential waist crystal"])
        b_t_crystal_values.append(cavity_results["tangential confocal parameter crystal"])
        xi_t_crystal_values.append(cavity_results["tangential focusing parameter"])

        w_s_crystal_values.append(cavity_results["sagittal waist crystal"])
        b_s_crystal_values.append(cavity_results["sagittal confocal parameter crystal"])
        xi_s_crystal_values.append(cavity_results["sagittal focusing parameter"])

        ellipticity_crystal_values.append(cavity_results["ellipticity crystal"])

        w_t_collimated_values.append(cavity_results["tangential waist collimated"])
        b_t_collimated_values.append(cavity_results["tangential confocal parameter collimated"])

        w_s_collimated_values.append(cavity_results["sagittal waist collimated"])
        b_s_collimated_values.append(cavity_results["sagittal confocal parameter collimated"])

        ellipticity_collimated_values.append(cavity_results["ellipticity collimated"])

    return {"tangential waists crystal":w_t_crystal_values,
            "tangential confocal parameters crystal":b_t_crystal_values,
            "tangential focusing parameters":xi_t_crystal_values,
            "sagittal waists crystal":w_s_crystal_values,
            "sagittal confocal parameters crystal":b_s_crystal_values,
            "sagittal focusing parameters":xi_s_crystal_values,
            "ellipticities crystal":ellipticity_crystal_values,
            "tangential waists collimated":w_t_collimated_values,
            "tangential confocal parameters collimated":b_t_collimated_values,
            "sagittal waists collimated":w_s_collimated_values,
            "sagittal confocal parameters collimated":b_s_collimated_values,
            "ellipticities collimated":ellipticity_collimated_values,
            "s values":s_values_valid}
