# GarbageGo
ESC204 Praxis III Final Design Project

Afrin Prio, Fengyuan Liu, Mary Cheng, Nathanael Kusanda, Patrick Samaha, Vivek Dhande

GarbageGo is a garbage bin train system complemented by a text messaging system, aiming to build upon Gazipur's current system of informal waste colleciton to more effectively and efficiently capture waste. By involving separate, regionalised trains for recycling, organic, and garbage, the system allows for the separate movement of different types of waste, better enabling sorting and processing.  

![garbagego](https://user-images.githubusercontent.com/84566002/167674923-165a64ca-0439-4399-a62b-d3706d4609db.jpg)

In this prototype, the text messaging system is represented with MQTT topics. Each train contains an Arduino Nano RP2040 with code written in RaspberryPi to collect data on weight and volume, which can be found in '/bin-arduino/code.py'. On a computer, the file /server-collector/server.py can be run, establishing a central processing server for the data. Note that the SSID and password entries in 'secrets.py' should be updated for your own Wi-Fi. Each collector would then be able to subscribe to their region's MQTT topic, and receive notifications when a bin is full and ready for collection.

![mqtt](https://user-images.githubusercontent.com/84566002/167674939-69feffda-05f7-40fe-9271-80ffbec78ec0.jpg)

Below is a brochure detailing this design in further detail:
![Praxis Brochure](https://user-images.githubusercontent.com/84566002/167677890-26dc3802-646d-4488-8252-e382e8b68aa0.png)

