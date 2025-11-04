import adafruit_dht

dhtSensor = adafruit_dht.DHT22
dhtPin = 4

def getTempAndHumidity():
    return dhtSensor.temperature, dhtSensor.humidity

def getTemperature():
    return dhtSensor.temperature

def getHumidity():
    return dhtSensor.humidity