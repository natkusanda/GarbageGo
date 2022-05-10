import paho.mqtt.client as mqtt

mqttBroker = "test.mosquitto.org"
client_collector = mqtt.Client("CPU")
client_collector.connect(mqttBroker)

info = {1: {'weight': -1, 'volume': -1, 'density': -1},
        2: {'weight': -1, 'volume': -1, 'density': -1}}

regions = {1: ["Kazi Azimuddin (Central – C)", "C"],
           2: ["Mariyali (NW)", "NW"],
           3: ["Luxmipura (W)", "W"],
           4: ["Agriculture (SW)", "SW"],
           5: ["Hajibag (SE)", "SE"],
           6: ["Orchid House (NE)", "NE"]}
'''
Format for dictionary regions:
           <id>: [<full title of region>, <short-form (MQTT connection ID)>
'''

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    teamid = "1012H" #TODO: fill in your team ID
    client.subscribe(f"uoft/p3/{teamid}/msg")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("\n")
    alert = None
    global info
    global regions
    data = msg.payload
    data = data.decode()
    bin_id = int(data[0])
    if data[1] == '1':
        sensor = "weight"
        if float(data[2:])>= 100:
            alert = "Dear Waste Collector of " + regions[bin_id][0] + ",\n The C0113CT3R system has notified that bin " + str(bin_id) + " needs to be replaced due to surpassing the threshold weight. Recommended maximum weight 5kg. Bin " + str(bin_id) + " weight is " + str(info[bin_id]['weight']) + " kg."
    elif data[1] == '2':
        sensor = "volume"
        if float(data[2:]) >= 80:
            alert = "Dear Waste Collector of " + regions[bin_id][0] + ",\n The C0113CT3R system has notified that bin " + str(bin_id) + " needs to be replaced due to surpassing the threshold volume. Recommended maximum volume 7200 cubic cm. Bin " + str(bin_id) + " volume is " + str(8000*info[bin_id]['volume']/100) + " cubic cm."
    info[bin_id][sensor] = float(data[2:])
    info[bin_id]['density'] = info[bin_id]['weight']/(8000*info[bin_id]['volume'])
    # print("1:\t" + info[1][0], "2:\t" + info[2][0], "3:\t" + info[3][0], "4:\t" + info[4][0], "5:\t" + info[5][0], "6:\t" + info[6][0], sep="\n")
    print(info)
    if alert != None:
        print("!!!\t" + sensor + " error; sending alert to " + regions[bin_id][0] + " waste collectors.")
        print(regions[bin_id][1])
        client_collector.publish(regions[bin_id][1], alert)



if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("test.mosquitto.org", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
