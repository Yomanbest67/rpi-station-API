import board
import adafruit_dht
import time

dhtSensor = None

def init_sensor():
    global dhtSensor
    dhtSensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)

def getTempAndHumidity():
    return dhtSensor.temperature, dhtSensor.humidity

def getTemperature():
    return dhtSensor.temperature

def getHumidity():
    return dhtSensor.humidity

def humidex(temperature, humidity):
    euler = 2.71828

    waterVaporPressure = (humidity / 100.0) * 6.105 * pow(euler, (17.27 * temperature) / (237.7 + temperature))

    humidex = temperature + 0.5555 * (waterVaporPressure - 10.0)

    return humidex

def feelsLikeTemp(temperature, humidity, wind=0):
    euler = 2.71828
    waterVaporPressure = (humidity / 100.0) * 6.105 * pow(euler, (17.27 * temperature) / (237.7 + temperature))
    feelsLike = temperature + 0.33 * waterVaporPressure - 0.70 * wind - 4.00

    return feelsLike

def dewPoint(temperature, humidity):
    dewPoint = temperature - ((100 - humidity) / 5)
    return dewPoint

def getAll(retries = 10, delay = 2):

    for i in range(retries):
        humidity = dhtSensor.humidity
        temperature = dhtSensor.temperature

        if humidity is not None and temperature is not None:
        
            return {
                'temperature': temperature,
                'humidity': humidity,
                'humidex': humidex(temperature, humidity),
                'temperature_feels_like': feelsLikeTemp(temperature, humidity),
                'dew_point': dewPoint(temperature, humidity)
            }
        else:
            time.sleep(delay)

        return None, None