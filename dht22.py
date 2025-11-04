import board
import adafruit_dht

dhtSensor = None

def init_sensor():
    global dhtSensor
    dhtSensor = adafruit_dht.DHT22(board.D4)

def getTempAndHumidity():
    return dhtSensor.temperature, dhtSensor.humidity

def getTemperature():
    return dhtSensor.temperature

def getHumidity():
    return dhtSensor.humidity