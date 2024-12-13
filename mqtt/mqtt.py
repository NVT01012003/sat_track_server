import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import threading
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BROKER = os.getenv("MQTT_BROCKER")                                # Brocker URL
PORT = int(os.getenv("MQTT_PORT"))                                # PORT
TOPIC = "/topic/check_server"                                     # Check server topic
SET_SAT_TOPIC = "/topic/set_sat"                                  # Set satellite topic
UPDATE_ANGLE_TOPIC = "/topic/update_angles"                       # Update satellite angles topic
USERNAME = os.getenv("MQTT_USERNAME")                             # Username 
PASSWORD = os.getenv("MQTT_PASS")                                 # Password 
CHECK_TRACK = "/topic/check_track"
GPS_TOPIC = "/topic/location"
STOP_TOPIC ="/topic/stop"
SET_SAT_TOPIC = "/topic/set_sat"

Longitude = None
Latitude = None
Altitude = None

mqtt_event = asyncio.Event() 

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected!")
        client.subscribe(SET_SAT_TOPIC)
        client.subscribe(UPDATE_ANGLE_TOPIC)
        client.subscribe(CHECK_TRACK)
        client.subscribe(GPS_TOPIC)
    else:
        print(f"Error: {rc}")

def on_message(client, userdata, msg):
    print(f"Topic {msg.topic}: {msg.payload.decode()}")
    global Latitude, Longitude, Altitude
    if msg.topic == CHECK_TRACK and msg.payload.decode() == "OK": 
        print(f"Success!")
    if msg.topic == GPS_TOPIC:
        location = [float(num) for num in msg.payload.decode().split()]
        if location[0] != 0: 
            Longitude = location[0]
            Latitude = location[1]
            Altitude = location[2]
        print(f"Success!")


def get_message(time, start, end, step, set):
    text = ""
    start_ = start
    if set: 
        for i in range(2): 
            text += f"{time + i - 1} 0 0,"
    else: 
        for i in range(2): 
            text += f"{time + i - 1} {(start - step * (2 - i)):.2f} {(start - step * (2 - i)):.2f},"
    count = 2; 
    while (round(start, 2) <= end):
        text += f"{int(time + 1 + (start - start_)/0.6)} {start:.2f} {start:.2f},"
        start += step
        count = count + 1 
    print(count)
    return text

def connect_mqtt():
    client = mqtt_client.Client()
    client.username_pw_set(USERNAME, PASSWORD)

    # Thiết lập TLS
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    return client