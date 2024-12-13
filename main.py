from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from skyfield.api import load, Topos, EarthSatellite
import asyncio 
import httpx
from bs4 import BeautifulSoup
from connection import engine
from routes.index import router as index_router  
from routes.user import router as user_router  
# from .routes.satellite import router as satellite_router
# from .routes.tle import router as tle_router
from mqtt.mqtt import connect_mqtt, STOP_TOPIC, Longitude, Latitude, Altitude, SET_SAT_TOPIC, UPDATE_ANGLE_TOPIC
from mqtt.calc import get_message, get_tles, get_vnredsat, get_iss, get_visible_time, sat_location
from datetime import datetime 
from starlette.middleware.cors import CORSMiddleware
import time
Set = True
Update = False
Out_Of_Visible = False
Satellite_TLEs_List = {}
Update_TLEs_time = int(time.time())

app = FastAPI()

latitude_degrees = Latitude or 21.0378
longitude_degrees = Longitude or 105.7764
elevation_m = Altitude or 10

observer_location = Topos(latitude_degrees=latitude_degrees, longitude_degrees=longitude_degrees, elevation_m=elevation_m)
ts = load.timescale()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

mqtt_client_instance = None

# Routes
app.include_router(index_router)
app.include_router(user_router, prefix="/users", tags=["users"])

async def publish_message(mqtt_client_instance, time_set, satellite, observer_location):
    time_ = time_set
    print("this................")
    while True:
        global Set, Update, Out_Of_Visible
        message = get_message(time_, satellite, observer_location)
        print(message)
        current_time = int(time.time())
        print(current_time)
        if current_time < (time_ - 10):
            mqtt_client_instance.publish(SET_SAT_TOPIC, str(message))
            time_ = time_ + 25
            await asyncio.sleep(time_ + 25 - current_time)
        if Out_Of_Visible: 
            print("Disconnect!")
            mqtt_client_instance.loop_stop()
            mqtt_client_instance.disconnect()
        if Set: 
            mqtt_client_instance.publish(SET_SAT_TOPIC, str(message))
            Set = False
            Update = True
            time_ = time_ + 30
            await asyncio.sleep(25)
        elif Update: 
            mqtt_client_instance.publish(UPDATE_ANGLE_TOPIC, str(message))
            time_ = time_ + 30
            await asyncio.sleep(30)


@app.get("/")
async def read_root():
    return {"message": "FastAPI with MQTT is running!"}

@app.get("/start_tracking/sat_name:{sat_name}")
async def read_root(sat_name):
    global mqtt_client_instance, Set, Update, Out_Of_Visible, Satellite_TLEs_List, Update_TLEs_time, observer_location, ts
    if not Satellite_TLEs_List or (int(time.time()) - Update_TLEs_time) > 3600:
        vnredsat_tle = await get_vnredsat()
        tle_list = await get_tles()
        iss_tle = await get_iss()
        Satellite_TLEs_List = {**iss_tle, **vnredsat_tle, **tle_list}
        Update_TLEs_time = int(time.time())
        for name, tle in Satellite_TLEs_List.items(): 
            satellite = EarthSatellite(tle["line_1"], tle["line_2"], name)
            visible_time = get_visible_time(satellite, observer_location, ts)
            Satellite_TLEs_List[name]["visible_time"] = visible_time["local_time"]
            Satellite_TLEs_List[name]["time_seconds"] = visible_time["time_seconds"]
    if sat_name not in Satellite_TLEs_List.keys(): 
        return {"message": "satellite not found!"}
    Set = True
    Update = False
    Out_Of_Visible = False
    mqtt_client_instance = connect_mqtt()
    mqtt_client_instance.loop_start()
    satellite = EarthSatellite(Satellite_TLEs_List[sat_name]["line_1"], Satellite_TLEs_List[sat_name]["line_2"], sat_name)
    # Chạy tác vụ nền để gửi message
    asyncio.create_task(publish_message(mqtt_client_instance, int(Satellite_TLEs_List[sat_name]["time_seconds"]), satellite, observer_location))
    return {"message": f"Tracker start with: {sat_name}"}

@app.get("/stop")
async def read_root():
    global mqtt_client_instance, Set, Update, Out_Of_Visible
    if mqtt_client_instance:
        mqtt_client_instance.publish(STOP_TOPIC, "STOP")
        mqtt_client_instance.loop_stop()
        mqtt_client_instance.disconnect()
    Set = True
    Update = False
    if Out_Of_Visible: 
        Out_Of_Visible = False
    return {"message": "MQTT stoped!"}

@app.get("/get_tle") 
async def get_tle_route():
    global Satellite_TLEs_List, Update_TLEs_time, observer_location, ts
    if Satellite_TLEs_List and (int(time.time()) - Update_TLEs_time) < 3600: 
        return Satellite_TLEs_List
    else: 
        vnredsat_tle = await get_vnredsat()
        tle_list = await get_tles()
        iss_tle = await get_iss()
        Satellite_TLEs_List = {**iss_tle, **vnredsat_tle, **tle_list}
        Update_TLEs_time = int(time.time())
        for name, tle in Satellite_TLEs_List.items(): 
            satellite = EarthSatellite(tle["line_1"], tle["line_2"], name)
            visible_time = get_visible_time(satellite, observer_location, ts)
            Satellite_TLEs_List[name]["visible_time"] = visible_time["local_time"]
            Satellite_TLEs_List[name]["time_seconds"] = visible_time["time_seconds"]
        return Satellite_TLEs_List

@app.get("/get_satellite_location/satellite:{sat_name}")
async def get_sat_location_route(sat_name): 
    global Satellite_TLEs_List, Update_TLEs_time, observer_location, ts
    if not Satellite_TLEs_List or (int(time.time()) - Update_TLEs_time) > 3600:
        vnredsat_tle = await get_vnredsat()
        tle_list = await get_tles()
        iss_tle = await get_iss()
        Satellite_TLEs_List = {**iss_tle, **vnredsat_tle, **tle_list}
        Update_TLEs_time = int(time.time())
        for name, tle in Satellite_TLEs_List.items(): 
            satellite = EarthSatellite(tle["line_1"], tle["line_2"], name)
            visible_time = get_visible_time(satellite, observer_location, ts)
            Satellite_TLEs_List[name]["visible_time"] = visible_time["local_time"]
            Satellite_TLEs_List[name]["time_seconds"] = visible_time["time_seconds"]
    satellite = EarthSatellite(Satellite_TLEs_List[sat_name]["line_1"], Satellite_TLEs_List[sat_name]["line_2"], sat_name)
    location = sat_location(int(time.time()), satellite, observer_location)
    res = {sat_name: {
        **Satellite_TLEs_List[sat_name], **location
    }}
    return res