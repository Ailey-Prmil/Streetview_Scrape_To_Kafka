import requests
import time
import shutil

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewPartitions
from json import dumps

import os
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import re

time_delay = 1 # seconds to wait between clicks
topic_name = 'StreetviewImages'
kafka_server = 'localhost:9092'
class Data:
    # image_id: str - the name of the image file
    # location: [float, float] - the latitude and longitude of the image
    def __init__(self, image_id, latitude, longitude):
        self.image_id = image_id
        self.location = [latitude, longitude]
    def to_json(self):
        return json.dumps(self.to_dict()).encode('utf-8')
    def to_dict(self):
        return {
            'image_id': self.image_id,
            'latitude': self.location[0],
            'longitude': self.location[1],
        }

    def __str__(self):
        return f"Data(image_id={self.image_id}, location={self.location})"
def get_lat_lon_from_url(url):
    match = re.search(r"/@([-\d.]+),([-\d.]+)", url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def highlight_click(edge, rotate_button, x_offset, y_offset):
    
    # Highlight the click point
    highlight_script = f"""
        var elem = arguments[0];
        var rect = elem.getBoundingClientRect();
        var x = rect.left + {x_offset};
        var y = rect.top + {y_offset};
        var marker = document.createElement('div');
        marker.style.position = 'fixed';
        marker.style.left = x + 'px';
        marker.style.top = y + 'px';
        marker.style.width = '10px';
        marker.style.height = '10px';
        marker.style.backgroundColor = 'red';
        marker.style.borderRadius = '50%';
        marker.style.zIndex = '9999';
        marker.style.pointerEvents = 'none';
        document.body.appendChild(marker);
        setTimeout(() => marker.remove(), 1000);  // Auto-remove after 1 second
    """
    edge.execute_script(highlight_script, rotate_button)
def publish_streetview_image(data: Data):
    """
    Publish all video files in the given folder to a Kafka topic.
    Each video will be published with a unique key (video file name).
    
    :param data: data
    :param kafka_server: Kafka bootstrap server address
    :param topic_name: Kafka topic name
    """
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=kafka_server,
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: v  # raw bytes for frames
    )

    producer.send(topic_name, key=data.image_id, value=data.to_json())
    time.sleep(0.1)  # simulate slower stream
    print(f"Published image data: {data}")


    producer.flush()
    producer.close()

edge = webdriver.Edge()
kafka_client = KafkaAdminClient(bootstrap_servers=kafka_server)
places = []
with open('place_urls.txt', 'r') as f:
    for line in f:
        places.append(line.strip())

for place in places:
    # each place - there are 8 places in the file
    edge.get(place)
   

    # Wait for compass to be ready
    wait = WebDriverWait(edge, 20)
    rotate_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="compass"]/div')))
    # Get the image URL from the page
    for i in range(50):
        # Save current URL
        old_url = edge.current_url
        old_lat, old_lon = get_lat_lon_from_url(old_url)

        # Click to rotate view slightly
        action = ActionChains(edge)
        highlight_click(edge, rotate_button, -100, -50)

        action.move_to_element_with_offset(rotate_button, -100, -50).click().perform()

        # Wait for URL to change (timeout 10 seconds)
        try:
            WebDriverWait(edge, 10).until(lambda d: get_lat_lon_from_url(d.current_url) != (old_lat, old_lon))
        except Exception as e:
            while (get_lat_lon_from_url(edge.current_url) == (old_lat, old_lon)):
                # If URL didn't change, try clicking again
                x_offset = random.randint(-80, -30)
                y_offset = random.randint(-80, -30)
                highlight_click(edge, rotate_button, x_offset, y_offset)
                action.move_to_element_with_offset(rotate_button, x_offset, y_offset).click().perform()
                time.sleep(1)  # Wait for the page to update
            continue

        time.sleep(time_delay)  # Add delay to avoid clicking too fast
        url = edge.current_url
        # Download the image from the URL
        # try:
        url = url.strip()
        if not url.startswith('https://www.google.com/maps/@'):
            continue
        image_url = url.split('!6s')[1].split('!7i')[0]
        image_url = image_url.replace('%3D', '=').replace('%2F', '/')
        longitude = url.split('@')[1].split(',')[0]
        latitude = url.split('@')[1].split(',')[1]
        while True:
            try:
                response = requests.get(image_url, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)
        with open(f'images\{longitude}_{latitude}.jpg' , 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        image_data = Data(
            image_id=f"{longitude}_{latitude}.jpg",
            latitude=float(latitude),
            longitude=float(longitude)
        )
        print(f"Processed image: {image_data}")
        # Publish the image data to Kafka
        publish_streetview_image(image_data)
        # except Exception as e:
        #     print(f"Error processing URL {url}: {e}")
        #     continue