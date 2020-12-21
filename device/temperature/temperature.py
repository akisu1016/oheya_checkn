import time
import board
import adafruit_dht
import subprocess


def get_temperature():

    dhtDevice = adafruit_dht.DHT22(board.D4)

    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        """
        print(
            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity
            )
        )
        """

        tempval = {"temp": temperature_c, "humidity": humidity}

        return tempval

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
    except Exception as error:
        dhtDevice.exit()
        raise error

try :
    while 1 :
        tem = getTemperature()
        print(tem)
        time.sleep(3)

except KeyboardInterrupt:
    pass
