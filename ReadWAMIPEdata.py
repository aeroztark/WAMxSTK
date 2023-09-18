"""This file reads a 4-D netcdf file and interpolates density at a given location & time.

--> Dependencies: the following packages need to be installed: Numpy, Scipy, netCDF4

--> Inputs:
    CurrentEpMin (float scalar): Current Epoch in Minutes
    current_height_km (float scalar): Current Satellite altitude in km
    current_lat (float scalar): Current Satellite Geodetic latitude (between -90 to 90 deg)
    current_lon (float scalar): Current Satellite longitude (between 0 to 360 deg)

--> Outputs: The output of this Python file is CurrentDensity variable on the last line (float scalar)
    CurrentDensity (float scalar): Density (kg/m^3) for the current Satellite position and epoch.
"""



import numpy as np
import netCDF4 as nc
import scipy
import sys
import time


#----------Begin Inputs ---------------#
#---------------------------------------#
#CurrentEpMin = 85.3 # Current Epoch in Minutes
#CurrentHeightKm = 150
#CurrentLat = 45
#CurrentLon =  195

# Specify netCDF file
ds = nc.Dataset(r"C:\Users\sasrivas\OneDrive - ANSYS, Inc\Work\12_R&D\ACE SME Mentoring Program\SpaceWeather x Astro\code\WAM_den_20211102.nc")
#----------End of Inputs ---------------#
#---------------------------------------#

# grab variable data from the netCDF file
den = ds['den'][:]
lat = ds['lat'][:]      # goes from -90 to +90
lon = ds['lon'][:]      # goes from 0 to 360
hlevs = ds['hlevs'][:]  # in km


# Function definitions
def ExtractDataForCurrentTime(current_t_min,den):
    """This function takes the current scenario time in minutes and rounds it to the nearest 10 min window, and returns 3-D density data for that 10 min window.
    Inputs:
        current_t_min: Current Epoch time in minutes from STK
        den: 4-D density from a daily .nc file

    Outputs:
        ThisBlockDen: 4-D density for the 10-min block of the day in which the current Epoch lies"""

    MinuteArray = np.arange(0,1440,10) # Array of 10 minute blocks for 24 hrs (to find data corresponding to current time)
    MinBlock = round(current_t_min,-1) # Round current time in mins to the nearest 10-min block
    WhichBlock = np.where(MinuteArray == MinBlock) # find
    TimeFloorInd = WhichBlock[0][0]
    ThisBlockDen = den[TimeFloorInd:TimeFloorInd+1,:,:,:]
    return ThisBlockDen


def CreateDensityInterpolant(hlevs,lat,lon,ThisBlockDen):
    """This function creates a SciPy interpolant on the time-filtered 4-D density. The output interpolant can then be used to interpolate density
    Inputs:
        hlevs: height array of the nc file
        lat: latitude array of the nc file
        lon: longitude array of the nc file
        ThisBlockDen: 10-min 4-D density block

    Outputs:
        fn: SciPy Interpolant"""

    from scipy.interpolate import RegularGridInterpolator
    fn = RegularGridInterpolator((hlevs,lat,lon),np.squeeze(ThisBlockDen)) # create Interpolant
    return fn

def main(argv):
    CurrentEpMin = float(argv[0])
    CurrentHeightKm = float(argv[1])
    CurrentLat = float(argv[2])
    CurrentLon = float(argv[3])
    StartTime = argv[4] # all times will be coming back in ISO-YMD format because spaces break inputs to python.  So format is like this: 2023-05-12T16:00:00.000
    StopTime = argv[5]

    # Perform Interpolation
    CurrentBlockDensity = ExtractDataForCurrentTime(CurrentEpMin, den)
    CurrentInterpolant = CreateDensityInterpolant(hlevs,lat,lon,CurrentBlockDensity)
    CurrentDensity = CurrentInterpolant([CurrentHeightKm,CurrentLat,CurrentLon]) # finally, get density
    
    sys.stdout.write(str(CurrentDensity[0]))
    sys.stdout.flush()
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
