from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import requests
import os
import time
import csv 
# Function to find desired items
def find_desired_items(driver):
    lis=[]
    cars=driver.find_elements(By.XPATH,"//div[@class='list-item']")
    for car in cars:
        try:
            link=car.find_element(By.XPATH,".//div[@class='title-wrap']/h2/a")
            li=link.get_attribute('href')
            tex=link.text
            lis.append({"Title": tex, 'links':li})
        except:
            print('not found')
    return lis

# Function to scroll down the page
def scroll_down(driver):
    scroll_increment = driver.execute_script("return window.innerHeight * 0.3;")
    # Initial scroll position
    scroll_position = 0
    # Loop until the bottom of the page is reached
    while True:
        # Scroll down by the defined increment
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        # Wait for the page to load
        time.sleep(1)  # Adjust as needed
        # Update the scroll position
        scroll_position += scroll_increment
        # Check if we have reached the bottom of the page
        if scroll_position >= driver.execute_script("return document.body.scrollHeight;"):
            break
    pass

# Function to append data to CSV file
def append_to_csv(data, folder_path):
    csv_file = os.path.join(folder_path, 'UK.csv')
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title','links'])
        writer.writerows(data)

# Function to download images
def download_images_from_urls(image_urls, folder_path):
    images_folder = os.path.join(folder_path, "images")
    
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    for url in image_urls:
        filename = os.path.join(images_folder, url.split("/")[-1])
        with open(filename, 'wb') as f:
            response = requests.get(url)
            if response.status_code == 200:
                f.write(response.content)
            else:
                print(f"Failed to download image from {url}")
# Function to click the "Next" button
def click_next_button(driver):
    try:
        next_button = driver.find_element(By.XPATH, '//button[text()="›"]')
        next_button.click()
        print("Next button found:")
    except:
        print("Next button not found or issue:")
        pass

# Initialize headless Chrome browser
options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode
service = Service(ChromeDriverManager().install())  # Use WebDriverManager to get ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the website URL
url = 'https://ev-database.org/uk/'
driver.get(url)

# Wait for the page to load
time.sleep(2)  # Adjust as needed

# Main loop to iterate through pages
while True:
    try:
        # Scroll down the page
        scroll_down(driver)

        # Find desired items on the current page
        data = find_desired_items(driver)

        # Folder path to save images
        folder_path = "C:\\Users\\DELL 5400\\Desktop\\EV-Data"

        # Save data into CSV
        append_to_csv(data, folder_path)

        # Find all image elements and extract URLs
        image_urls = [img.get_attribute("src") for img in driver.find_elements(By.XPATH, "//div[@class='list-item']//div[@class='img']//a//img")]

        # Download images
        download_images_from_urls(image_urls, folder_path)

        # Get the current URL
        current_url = driver.current_url

        # Check if there is a "Next" button
        next_button = driver.find_element(By.XPATH, '//button[text()="›"]')
        next_button.click()
        
        # Wait for the URL to change or timeout after 10 seconds
        WebDriverWait(driver, 10).until(EC.url_changes(current_url))
    except (NoSuchElementException, StaleElementReferenceException):
        break

# Quit the browser
driver.quit()