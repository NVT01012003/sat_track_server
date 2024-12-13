from skyfield.api import load, Topos, EarthSatellite, utc
from datetime import datetime, timezone, timedelta
from math import radians, cos
from pytz import timezone as time_z
import time
import httpx
from bs4 import BeautifulSoup
import json


def get_message(time, satellite, observer_location):
  text = ""
  count = 0
  for i in range(time - 2, time + 32): 
    skyfield_time = time_convert(i)

    difference = satellite - observer_location
    topocentric = difference.at(skyfield_time)

    alt, az, distance = topocentric.altaz()

    alt_radians = radians(alt.degrees)
    text += f"{i} {alt.degrees:.2f} {az.degrees:.2f},"
    count = count + 1
    # if i == time + 32 and ground_distance > 2000: 
    #   return False
  print(count)
  return text

def sat_location(time, satellite, observer_location):
    skyfield_time = time_convert(time)
    difference = satellite - observer_location
    topocentric = difference.at(skyfield_time)

    geocentric = satellite.at(skyfield_time)
    subpoint = geocentric.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees
    altitude = subpoint.elevation.km

    alt, az, distance = topocentric.altaz()

    alt_radians = radians(alt.degrees)
    _distance = distance.km * cos(alt_radians)
    return {
       "ground_distance": _distance, 
       "longitude": longitude, 
       "latitude": latitude, 
       "altitude": altitude
    }

def time_convert(time_seconds: int): 
  utc_time = datetime.fromtimestamp(time_seconds, tz=timezone.utc)
  ts = load.timescale()
  skyfield_time = ts.utc(utc_time.year, utc_time.month, utc_time.day,
                       utc_time.hour, utc_time.minute, utc_time.second)
  return skyfield_time

def get_visible_time(satellite, observer_location, ts): 
  start_time = ts.now()
  end_time = ts.utc(datetime.now(utc) + timedelta(days=1))  # Dự đoán trong 1 ngày

  elevation_threshold = 5  # Đơn vị: độ

  times, events = satellite.find_events(observer_location, start_time, end_time, altitude_degrees=elevation_threshold)

  vietnam_tz = time_z('Asia/Ho_Chi_Minh')
  if not times: 
    return False
  ti = times[0]
  dt_utc = ti.utc_datetime()
  time_seconds = (dt_utc - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
  # time_seconds = ti.utc_seconds
  local_time = ti.utc_datetime().replace(tzinfo=utc).astimezone(vietnam_tz)
  return {"local_time": local_time, "time_seconds": time_seconds}


async def get_vnredsat():
    url = "https://www.n2yo.com/satellite/?s=39160"  # URL của vệ tinh VNREDSAT-1 (NORAD ID: 39160)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        tle_section = soup.find('pre')  
        if tle_section:
            tle_data = tle_section.get_text(strip=True)
            tle_lines = tle_data.split('\n')
            if len(tle_lines) >= 2:     
                line_1 = tle_lines[0].strip()
                line_2 = tle_lines[1].strip() 
                return {"VNREDSAT-1": {"line_1": line_1, "line_2": line_2}}
            else: return False
        else:
            return False
    else:
        return False

async def get_tles():
    url = "https://api.tinygs.com/v1/tinygs_supported.txt"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code == 200:
        tle_data = response.text.splitlines()
        tle_list = filter_tle(tle_data)
        if not tle_list: 
            return False
        return tle_list
    else:
        return False
    
async def get_iss():
    url = "https://db.satnogs.org/api/tle/?norad_cat_id=25544"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code == 200:
        tle_data = response.json()
        if tle_data: 
          return {f"{tle_data[0]["tle0"][2:]}": {"line_1": tle_data[0]["tle1"], "line_2": tle_data[0]["tle2"]}}
        else:
          return False
    else:
        return False
    
def filter_tle(tle_data): 
  tle_names = ["Norby", "Tianqi-21", "Tianqi-22", "Tianqi-23", "Tianqi-24"]
  tle_list = {}
  for i in range(len(tle_data)): 
    if tle_data[i] in tle_names: 
      tle_list[tle_data[i]] = {"line_1": tle_data[i + 1], "line_2": tle_data[i + 2]}
  return tle_list