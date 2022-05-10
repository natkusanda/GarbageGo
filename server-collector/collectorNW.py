import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print(str(message.payload.decode("utf-8")))
    print("=====================================================================")

    # after receiving a message, hold for some time so that we do not spam the waste collectors
    time.sleep(5)


mqttBroker ="test.mosquitto.org"

client = mqtt.Client("Smartphone")
client.connect(mqttBroker)

client.loop_start()

client.subscribe("NW")
client.on_message=on_message

time.sleep(30)
client.loop_stop()
