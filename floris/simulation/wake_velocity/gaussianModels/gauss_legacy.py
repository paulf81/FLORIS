# Copyright 2020 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import numpy as np
from ....utilities import cosd, sind, tand
from ..base_velocity_deficit import VelocityDeficit
from .gaussian_model_ish import GaussianModel


class LegacyGauss(VelocityDeficit):
    def __init__(self, parameter_dictionary):
        super().__init__(parameter_dictionary)

        self.model_string = "gauss_legacy"
        model_dictionary = self._get_model_dict()

        # near wake / far wake boundary parameters
        self.alpha = float(model_dictionary["alpha"])
        self.beta = float(model_dictionary["beta"])

        # wake expansion parameters
        self.ka = float(model_dictionary["ka"])
        self.kb = float(model_dictionary["kb"])

    def function(self, x_locations, y_locations, z_locations, turbine, turbine_coord, deflection_field, flow_field):
        # veer (degrees)
        veer = flow_field.wind_veer

        # added turbulence model
        TI = turbine.current_turbulence_intensity

        # turbine parameters
        D = turbine.rotor_diameter
        HH = turbine.hub_height
        yaw = -1 * turbine.yaw_angle  # opposite sign convention in this model
        Ct = turbine.Ct
        U_local = flow_field.u_initial

        # wake deflection
        delta = deflection_field

        xR, _ = GaussianModel.mask_upstream_wake(y_locations, turbine_coord, yaw)
        uR, u0 = GaussianModel.initial_velocity_deficits(U_local, Ct)
        sigma_y0, sigma_z0 = GaussianModel.initial_wake_expansion(turbine, U_local, veer, uR, u0)

        # quantity that determines when the far wake starts
        x0 = D * ( cosd(yaw) * (1 + np.sqrt(1 - Ct)) ) / ( np.sqrt(2) * ( 4 * self.alpha * TI + 2 * self.beta * ( 1 - np.sqrt(1 - Ct) ) ) ) + turbine_coord.x1

        # velocity deficit in the near wake
        sigma_y = (((x0 - xR) - (x_locations - xR)) / (x0 - xR)) * 0.501 * D * np.sqrt(Ct / 2.0) + ((x_locations - xR) / (x0 - xR)) * sigma_y0
        sigma_z = (((x0 - xR) - (x_locations - xR)) / (x0 - xR)) * 0.501 * D * np.sqrt(Ct / 2.0) + ((x_locations - xR) / (x0 - xR)) * sigma_z0
        sigma_y[x_locations < xR] = 0.5 * D
        sigma_z[x_locations < xR] = 0.5 * D

        a = cosd(veer)**2 / (2 * sigma_y**2) + sind(veer)**2 / (2 * sigma_z**2)
        b = -sind(2 * veer) / (4 * sigma_y**2) + sind(2 * veer) / (4 * sigma_z**2)
        c = sind(veer)**2 / (2 * sigma_y**2) + cosd(veer)**2 / (2 * sigma_z**2)
        r = -(a * ((y_locations - turbine_coord.x2) - delta)**2 - 2 * b * ((y_locations - turbine_coord.x2) - delta) * ((z_locations - HH)) + c * ((z_locations - HH))**2)
        C = 1 - np.sqrt(1 - ( Ct * cosd(yaw) / (8.0 * sigma_y * sigma_z / D**2) ) )

        velDef = GaussianModel.gaussian_function(U_local, C, r, 1, np.sqrt(0.5) )
        velDef[x_locations < xR] = 0
        velDef[x_locations > x0] = 0

        # wake expansion in the lateral (y) and the vertical (z)
        ky = self.ka * TI + self.kb  # wake expansion parameters
        kz = self.ka * TI + self.kb  # wake expansion parameters
        sigma_y = ky * (x_locations - x0) + sigma_y0
        sigma_z = kz * (x_locations - x0) + sigma_z0
        sigma_y[x_locations < x0] = sigma_y0[x_locations < x0]
        sigma_z[x_locations < x0] = sigma_z0[x_locations < x0]

        # velocity deficit outside the near wake
        a = cosd(veer)**2 / (2 * sigma_y**2) + sind(veer)**2 / (2 * sigma_z**2)
        b = -sind(2 * veer) / (4 * sigma_y**2) + sind(2 * veer) / (4 * sigma_z**2)
        c = sind(veer)**2 / (2 * sigma_y**2) + cosd(veer)**2 / (2 * sigma_z**2)
        r = a * (y_locations - turbine_coord.x2 - delta)**2 - 2 * b * (y_locations - turbine_coord.x2 - delta) * (z_locations - HH) + c * (z_locations - HH)**2
        C = 1 - np.sqrt(1 - ( Ct * cosd(yaw) / (8.0 * sigma_y * sigma_z / D**2) ) )

        # compute velocities in the far wake
        velDef1 = GaussianModel.gaussian_function(U_local, C, r, 1, np.sqrt(0.5) )
        velDef1[x_locations < x0] = 0

        U = np.sqrt(velDef**2 + velDef1**2)

        return U, np.zeros(np.shape(velDef1)), np.zeros(np.shape(velDef1))

    @property
    def ka(self):
        """
        Parameter used to determine the linear relationship between the 
            turbulence intensity and the width of the Gaussian wake shape.
        Args:
            ka (float, int): Gaussian wake model coefficient.
        Returns:
            float: Gaussian wake model coefficient.
        """
        return self._ka

    @ka.setter
    def ka(self, value):
        if type(value) is float:
            self._ka = value
        elif type(value) is int:
            self._ka = float(value)
        else:
            raise ValueError("Invalid value given for ka: {}".format(value))

    @property
    def kb(self):
        """
        Parameter used to determine the linear relationship between the 
            turbulence intensity and the width of the Gaussian wake shape.
        Args:
            kb (float, int): Gaussian wake model coefficient.
        Returns:
            float: Gaussian wake model coefficient.
        """
        return self._kb

    @kb.setter
    def kb(self, value):
        if type(value) is float:
            self._kb = value
        elif type(value) is int:
            self._kb = float(value)
        else:
            raise ValueError("Invalid value given for kb: {}".format(value))

    @property
    def alpha(self):
        """
        Parameter that determines the dependence of the downstream boundary
            between the near wake and far wake region on the turbulence
            intensity.
        Args:
            alpha (float, int): Gaussian wake model coefficient.
        Returns:
            float: Gaussian wake model coefficient.
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if type(value) is float:
            self._alpha = value
        elif type(value) is int:
            self._alpha = float(value)
        else:
            raise ValueError("Invalid value given for alpha: {}".format(value))

    @property
    def beta(self):
        """
        Parameter that determines the dependence of the downstream boundary
            between the near wake and far wake region on the turbine's
            induction factor.
        Args:
            beta (float, int): Gaussian wake model coefficient.
        Returns:
            float: Gaussian wake model coefficient.
        """
        return self._beta

    @beta.setter
    def beta(self, value):
        if type(value) is float:
            self._beta = value
        elif type(value) is int:
            self._beta = float(value)
        else:
            raise ValueError("Invalid value given for beta: {}".format(value))