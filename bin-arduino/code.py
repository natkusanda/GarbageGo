import time
from microcontroller import cpu
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
import analogio
import adafruit_hcsr04


#### mqqtt setup
import board
import time
import digitalio
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT

def on_connect(mqtt_client, userdata, flags, rc):
    '''
    This function will be called when the mqtt_client is connected successfully to the broker.
    '''
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))

def on_publish(mqtt_client, userdata, topic, pid):
    '''
    This method is called when the mqtt_client publishes data to a feed.
    '''
    print("Published to {0} with PID {1}".format(topic, pid))

# Set up LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Set MQTT definitions
teamid = "1012H" #TODO: fill in your teamid
mqtt_topic = f"uoft/p3/{teamid}/msg"

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set up SPI pins
esp32_cs = DigitalInOut(board.CS1)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# Connect the RP2040 to the Nina W102 uBlox module's onboard ESP32 chip via SPI connections
spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# Check if ESP32 chip found and ready to connect and print chip details
if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

# Print SSIDs for all discovered networks and their signal strengths
for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

# Try to connect to your WiFI network (using the SSID and password from secrets.py)
print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
    print(".", end="")

# If successfully connected, print IP
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

# Set up socket
socket.set_interface(esp)

# Set up a MiniMQTT Client
MQTT.set_socket(socket, esp)
mqtt_client = MQTT.MQTT(broker=secrets["broker"],port=secrets["port"])

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

# Try to connect to MQTT client
print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()

#set up sensor
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.A5, echo_pin=board.A4)
# moisture_pin = board.A0
# moisture = analogio.AnalogIn(moisture_pin)
force_pin = board.A1
force = analogio.AnalogIn(force_pin)

prv_refresh_time = 0.0

vol = 0
weight = 0
prev_voltage = 3
prev_vol = 1000
count = 0
error = 0

while True:
    if (time.monotonic() - prv_refresh_time) > 30:
        # Take readings and output calibrated values
        while True:
            #try:
            # ultrasonic sensor
            X = sonar.distance
            real_dist = 1.084*(X-9.044)+10
            # print("Distance measure ok!")
            # moisture sensor
            # io.publish("moisture",moisture.value)
            # print("Moisture publish ok!")
            # force sensor to accumulate weight
            analog_force = force.value + 1
            voltage = (5 * 10000) / (10000 + analog_force)
            if (voltage - prev_voltage > 2.5):
                weight = weight + 200
            prev_voltage = voltage
            if (count == 10):
                #io.publish("weight",weight)
                # Volume
                vol = ((20-real_dist)*20*20)
                if (vol < 0):
                    vol = prev_vol
                else:
                    prev_vol = vol
                percent_vol = 100* vol/8000
                #io.publish("volume", percent_vol)
                # density
                density = weight/vol
               # io.publish("density",density)
                count = 0
               # print("Publishing now!")
                #print(density, percent_vol)
                # send stuff to server
                bin = 1
                garbage_weight = str(bin)+"1"+str(weight)
                garbage_volume = str(bin)+"2"+str(percent_vol)
                # Format of data sends
                ''' 0: bin_id
                    1: 1 for weight, 2 for percent volume
                    2-: data
                '''

                #msg = "ID: 1\t" + "Weight: " + str(weight) + "\tVolume: " + str(vol)
                print("Arduino --> Server | Weight: %s" % garbage_weight)
                print("Arduino --> Server | Volume: %s" % garbage_volume)
                if(len(garbage_weight) > 0 and len(garbage_volume) > 0):
                    print("Publishing to %s" % mqtt_topic)
                    mqtt_client.publish(mqtt_topic, garbage_weight)
                    mqtt_client.publish(mqtt_topic, garbage_volume)
                    #publish_list = [garbage_ID,garbage_weight,garbage_volume]
                    #mqtt_client.publish(mqtt_topic, publish_list)




                time.sleep(1.0)
            count = count + 1
            time.sleep(0.5)

            '''except:
                if (error != 1):
                    error = 1
                    print("error")'''
