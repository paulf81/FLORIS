# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

# See read the https://floris.readthedocs.io for documentation


import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import floris.tools as wfct
import numpy as np


print('Running FLORIS with no yaw...')
# Instantiate the FLORIS object

initial = np.linspace(0.1,0.9,4)
constant = np.linspace(0.1,0.9,4)
ai = np.linspace(0.1,0.9,4)
downstream = np.linspace(0.1,0.9,4)

fi = wfct.floris_interface.FlorisInterface("../../example_input.json")

# Set turbine locations to 3 turbines in a row
D = fi.floris.farm.turbines[0].rotor_diameter

l_x = [0,6*D,12*D,18*D,24*D]
# l_x = [0,7*D,14*D]
l_y = [0,0,0,0,0]

# fi.reinitialize_flow_field(layout_array=(layout_x, layout_y),wind_direction=wind_direction)
fi.reinitialize_flow_field(layout_array=(l_x, l_y),wind_direction=270,turbulence_intensity=0.065)
fi.calculate_wake(yaw_angles=np.zeros(len(l_x)))

for i in range(len(l_x)):
    print('Turbine ', i, ' velocity = ', fi.floris.farm.turbines[i].average_velocity, fi.floris.farm.turbines[i].power/(10**3))





