# shg-cavity-calculator
shg-cavity-calculator is a program for designing bow-tie ring resonators for second-harmonic
generation of laser light.

## System Requirements
Running shg-cavity-calculator requires [Python 3](https://www.python.org/). Python package
dependencies are managed using [pipenv](https://docs.pipenv.org/).

## Installation
Use pipenv to generate a new virtualenv and install the required packages
```
cd shg-cavity-calculator
pipenv install
```

## Usage
Use pipenv to activate the virtualenv and launch the program
```
pipenv run python main.py
```

The diagram in the top left of the program window shows the layout of the ring resonator. The radio
buttons in this box allow switching between a Brewster-cut and a plane crystal.

The box below shows the parameters of the calculated cavity eigenmode. The first section refers to
the focus inside the crystal, the second section to the secondary focus in the collimated arm of the
cavity. Variables ending with t refer to the tangential direction, variables ending with s to the
sagittal direction. The calculated variables are:
* w: Gaussian beam waist
* b: Confocal parameter
* ξ: Boyd-Kleinman parameter (l/b)
* ellipticity: ws/wt

The third section shows the free spectral range of the cavity.

The input box allows setting the parameters of the cavity. The mirror incidence angle is the angle
between the incident beam and the surface normal of the mirror (or half of the angle between the
incident and the reflected beam). For a symmetrical cavity the secondary focus is located half-way
between the two focusing mirrors. The distance from either mirror to the focus is one of the 
configurable parameters. The crystal B parameter is defined as B = ρ (l k_1)^(1/2)/2, where ρ is
the birefringent walk-off angle, l is the crystal length, and k_1 is the fundamental wavenumber. It
doesn't effect the cavity mode and is used for shg efficiency calculations (to be implemented).

The plots in the right half of the program window show the dependence of various cavity mode
parameters on the distance between the focusing mirrors and the crystal surface. The vertical line
shows the currently selected value for this distance. The plots can be used for estimating the
sensitivity of the cavity mode to variations of the mirror positions.
