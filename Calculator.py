import numpy as np
import pandas
import openpyxl
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Get data from excel sheet for inputs.
try:
    getdata = pandas.read_excel('/Users/joeybanowetz/Desktop/Joule Calculations.xlsx', usecols='A')
except FileNotFoundError:
    Path = input ('File not found, Please enter path name here:')
    getdata = pandas.read_excel(Path, usecols='A') 

# Drag coefficient, projectile radius (m), area (m2) and mass (kg).
c = getdata.iloc[0]
r = getdata.iloc[1]
A = np.pi * r**2
m = getdata.iloc[2]

# Air density (kg.m-3), acceleration due to gravity (m.s-2).
rho_air = getdata.iloc[3]
g = 9.81

# For convenience, define  this constant.
k = 0.5 * c * rho_air * A

# Initial speed and launch angle (from the horizontal).
v0 = getdata.iloc[4]
phi0 = np.radians(getdata.iloc[5])

def deriv(t, u):
    x, xdot, z, zdot = u
    speed = np.hypot(xdot, zdot)
    xdotdot = -k/m * speed * xdot
    zdotdot = -k/m * speed * zdot - g
    return xdot, xdotdot, zdot, zdotdot

# Initial conditions: x0, v0_x, z0, v0_z.
u0 = 0, v0 * np.cos(phi0), getdata.iloc[6], v0 * np.sin(phi0)

# Integrate up to tf unless we hit the target sooner.
t0, tf = 0, 50

def hit_target(t, u):
    # We've hit the target if the z-coordinate is 0.
    return u[2]

# Stop the integration when we hit the target.
hit_target.terminal = True

# We must be moving downwards (don't stop before we begin moving upwards!)
hit_target.direction = -1

# Solve!
soln = solve_ivp(deriv, (t0, tf), u0, dense_output=True,
                 events=(hit_target))

print('Time to target: {:.2f}s'.format(soln.t_events[0][0]))

# Create an array of final velocities to find the angle of incidence.
Vf = (soln.y_events[0][0])
Vfy = (Vf [3])
Vfx = (Vf [1])
phif = -1*np.rad2deg(np.arctan(Vfy / Vfx))
print('Angle of Incidence: {:.2f} degrees'.format (phif))

# A fine grid of time points from 0 until impact time.
t = np.linspace(0, soln.t_events[0][0], 100)

# Retrieve the solution for the time grid and plot the trajectory.
sol = soln.sol(t)
x, z = sol[0], sol[2]
print('Distance: {:.2f}m'.format(x[-1]))

# Original code taken from https://scipython.com/book2/chapter-8-scipy/examples/a-projectile-with-air-resistance/