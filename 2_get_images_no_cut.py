import os
import requests
import time
import shutil

text_file = 'raw_urls.txt'
with open(text_file, 'r') as file:
    urls = file.readlines()
for url in urls:
    try:
        url = url.strip()
        if not url.startswith('https://www.google.com/maps/@'):
            continue
        image_url = url.split('!6s')[1].split('!7i')[0]
        image_url = image_url.replace('%3D', '=').replace('%2F', '/')
        longitude = url.split('@')[1].split(',')[0]
        latitude = url.split('@')[1].split(',')[1]
        image_pi = 15

        image_ya = image_url.split('-ya')[1].split('-')[0]
        new_image_ya = [float(image_ya)]

        image_fo = 70 # Default focal length
        image_url_prefix = image_url.split('pi-')[0]
        for image_ya in new_image_ya:
            image_url = f"{image_url_prefix}pi-{image_pi}-ya{image_ya}-ro0-fo{image_fo}"
            while True:
                try:
                    response = requests.get(image_url, stream=True)
                    break
                except requests.ConnectionError:
                    print("Connection error. Trying again in 2 seconds.")
                    time.sleep(2)
            with open (f"image_urls.txt", "a") as f:
                f.write(f"{image_url}\n")

            with open(f'images\{longitude}_{latitude}_{image_ya}.jpg' , 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        continue
    