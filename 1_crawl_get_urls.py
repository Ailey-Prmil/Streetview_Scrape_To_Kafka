import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import re

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

edge = webdriver.Edge()
places = []
urls = []
with open('place_urls.txt', 'r') as f:
    for line in f:
        places.append(line.strip())

for place in places:
    edge.get(place)
   

    # Wait for compass to be ready
    wait = WebDriverWait(edge, 20)
    rotate_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="compass"]/div')))

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
                x_offset = random.randint(-100, -30)
                y_offset = random.randint(-100, -30)
                highlight_click(edge, rotate_button, x_offset, y_offset)
                action.move_to_element_with_offset(rotate_button, x_offset, y_offset).click().perform()
            continue
        # Append the new URL
        urls.append(edge.current_url)

        time.sleep(2)  # Add delay to avoid clicking too fast

# Save to file
text_file = 'raw_urls.txt'
with open(text_file, 'w') as file:
    for url in urls:
        file.write(url + '\n')

