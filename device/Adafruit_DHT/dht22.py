from uuid import getnode as get_mac
import Adafruit_DHT as DHT
import smbus,time,datetime,pymysql,random,math
from device import connect_database as db
pymysql.install_as_MySQLdb()
connection = db.connect_air_database()
cursor = connection.cursor()

SENSOR_TYPE = DHT.DHT22
DHT_GPIO = 4

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address, if any error, change this address to 0x3f
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def main():
    
    lcd_init()
    random.seed(get_mac())
    
    
    while True:
        h,t = DHT.read_retry(SENSOR_TYPE,DHT_GPIO)
        time = datetime.datetime.now()
        now = time.strftime('%H:%M:%S')
        t1 = "{0:0.1f}" . format(t)
        h1 = "{0:0.1f}" . format(h)
        mac = math.floor(random.random()*1000000)
        

        lcd_string(now,LCD_LINE_1)
        lcd_string("tem" + "{0:0.1f}" . format(t) + " humi" + "{0:0.1f}" . format(h),LCD_LINE_2)
        
        try:
            cursor.execute("INSERT INTO device_data VALUES('" + str(mac) + "','" + "Temp" + "','" + str(t1) + "','" + str(time) + "')")
            cursor.execute("INSERT INTO device_data VALUES('" + str(mac) + "','" + "Humid" + "','" + str(h1) + "','" + str(time) + "')")
                
        except pymysql.Error as e:
            print(e)
            
        break

    connection.commit()
    connection.close()
    
        
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)