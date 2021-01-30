from abc import ABC, abstractmethod
import requests
import json
import decimal

class ResourceData(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def getResponseFromResource(self):
        pass

    @abstractmethod
    def resourceResponseToJson(self):
        pass

class DataList(ABC):
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
        while self.lower < self.upper:
            yield float(self.lower)
            self.lower += decimal.Decimal(self.step)

class ApiResponse(ResourceData):
    def __init__(self):
        super().__init__()
        self.baseUrl = "https://ssd-api.jpl.nasa.gov/fireball.api?date-min=2017-01-01&date-max=2020-01-01"
        self.headers={}
        self.payload={}
        self.response=None
        self.apiData=[]

    def getResponseFromResource(self):
        self.response=requests.get(self.baseUrl, headers=self.headers)

    def resourceResponseToJson(self):
        self.apiData = json.loads(self.response.text)
        return self.apiData

class LocationCoordinate(ApiResponse, DataList):

    def __init__(self):
        super().__init__()
        self.idataList = None
        self.listData = []
        self.a = None

    def fetchDataToProcess(self):
        self.idataList=iter(ApiResponse.resourceResponseToJson(self)["data"])

    def processDataList(self):
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
        return self.listData

class FireBall(DataList, FloatRange):
    def __init__(self, latitude, longitude):

        self.latitude = latitude
        self.longitude = longitude
        self.rlatitude = None
        self.rlongitude = None

    def fetchDataToProcess(self):
        self.latitude = self.latitude.replace(" ","")
        self.longitude = self.longitude.replace(" ","")
        #c = ["N", "n", "s", "S", "e", "E", "w", "W"]
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
    def __init__(self, latitude, longitude):
        super().__init__(latitude, longitude)
        self.rlatitudeRange = []
        self.rlongitudeRange = []
        self.data=[]

    def latitudeRange(self):
        l=FloatRange(round(decimal.Decimal(self.latitudeLimits()[0]),1), round(decimal.Decimal(self.latitudeLimits()[1]),1), 0.1)
        for i in list(l.floatRange()):
            self.rlatitudeRange.append(round(i,1))


    def longitudeRange(self):
        l = FloatRange(round(decimal.Decimal(self.longitudeLimits()[0]), 1),
                       round(decimal.Decimal(self.longitudeLimits()[1]), 1), 0.1)
        for i in list(l.floatRange()):
            self.rlongitudeRange.append(round(i, 1))

    def fetchdatalist(self):
        d = LocationCoordinate()
        d.getResponseFromResource()
        d.resourceResponseToJson()
        d.fetchDataToProcess()
        self.data = d.processDataList()

    def highestEnergyList(self):
        for values in self.data:
            if not (values[0] == 200.0 and values[1] == 200.0):
                if values[0] in self.rlatitudeRange and values[1] in self.rlongitudeRange:
                        print(values[2])







s1=FireBall("37.7937007 N", "122.4039064 W")
#s1.getResponseFromResource()
#s1.resourceResponseToJson()
s2=Energy("37.7937007 N", "122.4039064 W")
s2.fetchDataToProcess()
s2.processDataList()
s2.latitudeLimits()
s2.longitudeLimits()

s2.latitudeRange()
s2.longitudeRange()
s2.fetchdatalist()
s2.highestEnergyList()
