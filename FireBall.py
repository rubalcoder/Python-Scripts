# Python Module to compute and return the City/location and brightness of brightest shooting star for a given time period
# The time period is considered from 1st of January 2017 to 1st of January 2020
#
#
#
# \brief
# Fetch the latitude, Longitude, and Energy values from the fireBall API for the given time period and the datalist
# Take input the latitude, longitude and Energy values for a given city, create a latitude and longitude datarange with buffer of +-15
# From the datalist iterate and check the values in the datarange and fetch the energy values
# The higest value in the enegy value list of energy will be the value for given city
# Compare the highest values of energy for all the city and return the data
#
#
# Code Written in Python 3.7
#
# Start with importing the external modules and libraries into the main module
from abc import ABC, abstractmethod
import requests
import json
import decimal


## Using Abstract Base Classes to set class constraints

class ResourceData(ABC):
    # Inheriting from ABC indicates that this is an abstract base class
    """Abstract Base class, to get data from resource and set it to a valid format"""
    def __init__(self):
        super().__init__()

    # declaring a method as abstract requires a subclass to implement it
    @abstractmethod
    def getResponseFromResource(self):
        pass

    @abstractmethod
    def resourceResponseToJson(self):
        pass

class DataList(ABC):
    """Abstract class, to fetch data and process """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def fetchDataToProcess(self):
        pass

    @abstractmethod
    def processDataList(self):
        pass

class FloatRange():

    def __init__(self, lower, upper, step):
        self.lower = lower
        self.upper = upper
        self.step = step

    def floatRange(self):
        '''Method which takes a lower and upper float value and creates a range according to the step value'''
        while self.lower < self.upper:
            yield float(self.lower)
            self.lower += decimal.Decimal(self.step)

class ApiResponse(ResourceData):
    # Set URl, params, headers and payload for http get method to fetch API data from fireball API
    def __init__(self):
        super().__init__()
        self.baseUrl = "https://ssd-api.jpl.nasa.gov/fireball.api?date-min=2017-01-01&date-max=2020-01-01" # BaseURL, API method and filters for given data range
        self.headers={}
        self.payload={}
        self.response=None # Initiate variable and set it to http response
        self.apiData=[]

    def getResponseFromResource(self):
        try:
            # Get http response from http request and save it to self.response
            self.response=requests.get(self.baseUrl, headers=self.headers)
        except:
            print("Network Connection Error")

    def resourceResponseToJson(self):
        # set the http response to a valid JSON format and return the value
        try:
            self.apiData = json.loads(self.response.text)
            return self.apiData
        except:
            print("No response due to Network Error")

class LocationCoordinate(ApiResponse, DataList):
    # Process API data to get the list of latitude, longitude and energy values respectively

    def __init__(self):
        super().__init__()
        self.idataList = None
        self.listData = []

    def fetchDataToProcess(self):
        # create an iterator object of datalist with latitude, longitude and energy value extracted from API JSON data
        self.idataList=iter(ApiResponse.resourceResponseToJson(self)["data"])

    def processDataList(self):
        # Method to convert all string values to float value, and None value to an invalid value of 200
        for j in self.idataList:
            try:
                j[3] = round(float(j[3],1))
            except:
                if j[3] == None:
                    j[3] = 200.0

            try:
                j[5] = round(float(j[5],1))
            except:
                if j[5] == None:
                    j[5] = 200.0

            self.listData.append((float(j[3]), float(j[5]), float(j[1])))
        return self.listData # Return a list of tuple with float latitude, longitude and Energy values

class FireBall(DataList, FloatRange):
    # Get latitude, longitude float values and create a floating range for latitude and longitude
    def __init__(self, latitude, longitude):

        self.latitude = latitude
        self.longitude = longitude
        self.rlatitude = None # Initiate latitude value with lower/upper limit latitude variable
        self.rlongitude = None # Initiate longitude value with lower/upper longitude variable

    def fetchDataToProcess(self):
        # Modify the latitude and longitude values by removing spaces and trailing strings
        self.latitude = self.latitude.replace(" ","")
        self.longitude = self.longitude.replace(" ","")

        # List of strings to denote the direction ["N", "n", "s", "S", "e", "E", "w", "W"]
        for c in ["N", "n", "s", "S", "e", "E", "w", "W"]:
            if c in self.latitude:
                self.latitude = self.latitude.rstrip(c)
            else:
                pass

            if c in self.longitude:
                self.longitude = self.longitude.rstrip(c)
            else:
                pass

    def processDataList(self):
        # Create and return a latitude and longitude lower/upper limits  with a buffer size of 15
        try:
            self.rlatitude = [round(float(self.latitude)-15.0,1), round(float(self.latitude)+15.0,1)]
        except:
            pass

        try:
            self.rlongitude = [round(float(self.longitude)-15.0, 1), round(float(self.longitude)+15.0, 1)]
        except:
            pass

    def latitudeLimits(self):
        return self.rlatitude

    def longitudeLimits(self):
        return self.rlongitude

class Energy(FireBall):
    # Main class to get the API values from http response
    # Get the location, latitude and longitude values and create an upper/lower limit and range
    # Compare the API values with range values

    def __init__(self, latitude, longitude):
        super().__init__(latitude, longitude)
        self.rlatitudeRange = [] # Initiate a variable to range of latitudes
        self.rlongitudeRange = [] # Initiate a variable to range of longitudes
        self.data=[] # Initiate a data variable to set it to energy values
        self.energyList = {} # Initiate an empty dictionary

    def latitudeRange(self):
        # Create a latitude range with lower and upper limit of latitude with an increment of decimal 0.1
        # Round off the range values to one decimal digit
        #
        #
        # create a local object of a class FloatRange
        #
        #
        l=FloatRange(round(decimal.Decimal(self.latitudeLimits()[0]),1), round(decimal.Decimal(self.latitudeLimits()[1]),1), 0.1)
        for i in list(l.floatRange()):
            self.rlatitudeRange.append(round(i,1))

    def longitudeRange(self):
        # Create a longitude range with lower and uppper limits of longitude with an increment of decimal 0.1
        # Round off the range values to one decimal digit
        #
        # create a local object of a class FloatRange
        #
        #
        l = FloatRange(round(decimal.Decimal(self.longitudeLimits()[0]), 1),
                       round(decimal.Decimal(self.longitudeLimits()[1]), 1), 0.1)
        for i in list(l.floatRange()):
            self.rlongitudeRange.append(round(i, 1))

    def fetchdatalist(self):
        # create a local object of Location Coordinate class and get the data from API

        d = LocationCoordinate()
        d.getResponseFromResource()
        d.resourceResponseToJson()
        d.fetchDataToProcess()
        self.data = d.processDataList()

    def EnergyList(self):
        # Compare the lat, long, values in the latitude/longitude range and if exist save the location and energy value into ernergy list dictionary

        for values in self.data:
            if not (values[0] == 200.0 and values[1] == 200.0):
                if values[0] in self.rlatitudeRange and values[1] in self.rlongitudeRange:
                        self.energyList[values[2]]=(values[0], values[1])

    def highestEnergy(self):
        # returns the highest value of energy as key and the coordinates of the location with the highest energy value
        return [max(self.energyList.keys()), self.energyList[max(self.energyList.keys())]]

# if the current module is the main module perform the code
if __name__ == '__main__':
    city_Energy = {}

    # Setting the while loop to true to iterate over the city name and lat, long coordinates to return the comparison result
    while True:
        city = input("Enter the cityName: ") # Input the city name
        Latitude = input("Enter the latitude: ") # Input the latitude coordinates
        Longitude = input("Enter the longitude: ") # Input the longitude coordinates

        def getEnergy(Latitude, Longitude):
            # Function to get the location and highest energy value for the location
            s2 = Energy(Latitude, Longitude)
            s2.fetchDataToProcess()
            s2.processDataList()
            s2.latitudeLimits()
            s2.longitudeLimits()
            s2.latitudeRange()
            s2.longitudeRange()
            s2.fetchdatalist()
            s2.EnergyList()
            return s2.highestEnergy()

        city_Energy[getEnergy(Latitude, Longitude)[0]]=city
        def compareEnergy():
            # Compare and return the location and highest energy value
            print(city_Energy[max(city_Energy.keys())], max(city_Energy.keys()))

        compareResults=input("print the ComparisonResult: ") # User input to view the comparison results after n city iteration
        # press enter to iterate over and enter the details of next city
        if compareResults.casefold() == 'yes'.casefold():
            compareEnergy()
        elif compareResults.casefold() == 'exit'.casefold():
            break
        else:
            pass


