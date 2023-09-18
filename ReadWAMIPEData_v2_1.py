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
import os
import datetime

# Create a dictionary of netCDF files to use:-------------------------------------------------
WAMfileDir = r"C:\Users\sasrivas\OneDrive - ANSYS, Inc\Work\12_R&D\ACE SME Mentoring Program\SpaceWeather x Astro\scenarios\CaseStudy\GeomagneticQuiet\WAMdata"

##--------------------------------------------------------------------------------------------------
# Function definitions
##--------------------------------------------------------------------------------------------------

def InterpolateDensity(WAMfileDir,ncfile,CurrentHeightKm,CurrentLat,CurrentLon):
    """"WAMfileDir -> directory where all 10-min nc files are stored
        ncfile -> single element array of the result of nc file search (hence it needs to be indexed by [0])
        CurrentHeightKm, CurrentLat, CurrentLon -> values from STK at current timestep """
    ds = nc.Dataset(os.path.join(WAMfileDir,ncfile[0]))
    den = ds['den'][:]
    lat = ds['lat'][:]
    lon = ds['lon'][:]
    hlevs = ds['hlevs'][:]
    from scipy.interpolate import RegularGridInterpolator
    fn = RegularGridInterpolator((hlevs,lat,lon),np.squeeze(den)) # create Interpolant
    CurrentDensity = fn([CurrentHeightKm,CurrentLat,CurrentLon])
    return CurrentDensity[0]

def main(argv):
    CurrentEpMin = float(argv[0])
    CurrentHeightKm = float(argv[1])
    CurrentLat = float(argv[2])
    CurrentLon = float(argv[3])
    StartTime = argv[4] # all times will be coming back in ISO-YMD format because spaces break inputs to python.  So format is like this: 2023-05-12T16:00:00.000
    StopTime = argv[5]

    #----------------------------------------------------------------------
    # Perform computations:

    # First, use scenario start time and EpMin to select the nc files: 
    StartTime_obj = datetime.datetime.fromisoformat(StartTime) # read StartTime as datetime object
    CurrentTime = StartTime_obj + datetime.timedelta(minutes = CurrentEpMin) # Get current time by adding CurrentEpMin to StartTime datetime object

    CurrentTimePattern = datetime.datetime.strftime(CurrentTime,"%Y%m%d_%H%M00") # current scenario time in format of WAM file nomenclature
    SameTimeFIle = [x for x in os.listdir(WAMfileDir) if CurrentTimePattern in x] # if the current scenario time exactly corrsponds to a WAM 10 min file
    if SameTimeFIle:
        CurrentDensity = InterpolateDensity(WAMfileDir,SameTimeFIle,CurrentHeightKm,CurrentLat,CurrentLon)
    else:
        # Find upper and lower bound files
        hmsPattern = CurrentTimePattern[-6:] 
        # initial guesses by rounding CurrentTimePattern to the nearest 1000 (i.e. 10 minutes)
        round_down = CurrentTimePattern[:9] + str(round(int(hmsPattern),-3))
        round_up = CurrentTimePattern[:9] + str(round(int(hmsPattern),-3) + 1000)

        # Check if file exists for the rounded down time, then check if file exists for rounded up time, by traversing in steps of 1000 (i.e.10 min)
        file_down = [] # init
        file_down = [x for x in os.listdir(WAMfileDir) if round_down in x]
        while not(file_down): # run only if file_down is not found
            try_time = int(round_down[-6:])-1000    # decrease time by 1000 (i.e. 10 min)
            round_down = CurrentTimePattern[:9] + str(try_time)
            # try finding again
            file_down = [x for x in os.listdir(WAMfileDir) if round_down in x]

        file_up = [] # init
        file_up = [x for x in os.listdir(WAMfileDir) if round_up in x]
        while not(file_up): # run only if file_up is not found
            try_time = int(round_down[-6:])+1000    # increase time by 1000 (i.e. 10 min)
            round_up = CurrentTimePattern[:9] + str(try_time)
            # try finding again
            file_up = [x for x in os.listdir(WAMfileDir) if round_up in x]
        
        density_down = InterpolateDensity(WAMfileDir,file_down,CurrentHeightKm,CurrentLat,CurrentLon)
        density_up = InterpolateDensity(WAMfileDir,file_up,CurrentHeightKm,CurrentLat,CurrentLon)
        CurrentDensity = (density_down + density_up)/2.0

    sys.stdout.write(str(CurrentDensity))
    sys.stdout.flush()
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])

