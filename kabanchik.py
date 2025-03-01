# Full script 

# TODO why does it sometimes fail to log in
# TODO save cookies only if login was successful

import os
import pickle  # For saving and loading cookies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import datetime
import logging
from config import BOT_TOKEN, CHAT_ID, MOM_CHAT_ID, PHONE_NUMBER, PASSWORD

# Set up logging
logging.basicConfig(filename='kabanchik_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options() # Set up Chrome options for headless browsing
chrome_options.add_argument("--headless")  # Runs Chrome in headless mode
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--disable-blink-features=AutomationControlled') # Optional: To help avoid detection by some websites

def message_on_telegram(message="Hello from Python on Telegram!"):
    # Message Mom
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message, 'disable_notification': False}
    requests.post(url, data=payload)
    
    payload = {'chat_id': MOM_CHAT_ID, 'text': message, 'disable_notification': False}
    requests.post(url, data=payload)

def get_posts(page_source):
    # Extract posts from page source
    soup = BeautifulSoup(page_source, 'html.parser')
    dashboard_div = soup.find('div', {'data-bazooka': 'Dashboard'})
    posts = []
    if dashboard_div:
        post_divs = dashboard_div.find_all('div', class_='kb-dashboard-performer')
        for post_div in post_divs:
            title_tag = post_div.find('a', class_='kb-dashboard-performer__title')
            posts.append({
                'title': title_tag.get_text(strip=True) if title_tag else '',
                'link': title_tag['href'] if title_tag else '',
            })
    return posts

def load_cookies(driver, cookies_file):
    if os.path.exists(cookies_file): 
        # Load cookies if the file exists
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies: # Some cookies may have an expiry set; ensure correct format
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
        logging.info("Cookies loaded. Session is now persistent.")
        return True
    else:
        logging.info('No cookies found. Logging in...')
        return False

def login(driver, wait):
    driver.get('https://kabanchik.ua/ua/auth/login') # Navigate to the login page
    username_field = wait.until(EC.presence_of_element_located((By.NAME, 'phoneEmail')))  # Wait for the username and password fields to be present
    password_field = wait.until(EC.element_to_be_clickable((By.NAME, 'password')))

    # Log In
    username_field.send_keys(PHONE_NUMBER)
    password_field.send_keys(PASSWORD)
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_button.click()

    # Wait for the login to complete by checking for a change in the URL or presence of a logged-in element
    logging.info('Waiting for login to complete...')
    time.sleep(10)
    # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-bazooka='BaseHeader']")))

    # Save cookies to file for future sessions
    if driver.find_elements(By.CSS_SELECTOR, "div[data-bazooka='BaseHeader']"): 
        cookies = driver.get_cookies()
        with open(f'cookies_{time.time()}.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        logging.info("Logged in and cookies saved for session persistence.")
    else:
        logging.error("Login failed.")

def check_for_new_posts(driver, wait, seen_posts):
    driver.get('https://kabanchik.ua/ua/cabinet/dnipro/category/maliunky-ta-iliustratsii') # Reload the page
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'kb-dashboard-performer'))) 
    
    # Get the updated posts
    page_source = driver.page_source
    current_posts = get_posts(page_source)
    logging.info(f"First post's title: {current_posts[0]['title']}")

    # Check for new posts
    logging.info('Checking for new posts...')
    for post in current_posts:
        if post['title'] not in [p['title'] for p in seen_posts]:
            logging.info(f"New post found: {post['title']} {post['link']}")
            message_on_telegram(f"New post!  {post['title']} {post['link']}")
            seen_posts.append(post)
 
def main():
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 30)  # Max wait time on the wait.until commands
        driver.get('https://kabanchik.ua') # Navigate to the base domain to set the correct context for cookies
        cookies_file = 'cookies_030125.pkl'

        if not load_cookies(driver, cookies_file):
            login(driver, wait)

        # Navigate to the desired page
        driver.get('https://kabanchik.ua/ua/cabinet/dnipro/category/maliunky-ta-iliustratsii')
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'kb-dashboard-performer')))
        logging.info(f'Fetched {driver.title}')

        # Initial extraction of posts
        page_source = driver.page_source
        seen_posts = get_posts(page_source)
        logging.info(f"First post's title: {seen_posts[0]['title']}")

        # Periodically check for new posts
        while True:
            time.sleep(10) # Reload every 10 seconds
            check_for_new_posts(driver, wait, seen_posts)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    while True:
        main()
        time.sleep(10)
