import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from variables import *
import requests
from dotenv import load_dotenv
from simpleserver import *
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get("https://visas-de.tlscontact.com")
print(response.text)

# Start the server in a separate thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
email = os.getenv("email")
password = os.getenv("password")

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, email, password]):
    raise EnvironmentError("Missing one or more required environment variables.")

# Selenium WebDriver Settings
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_experimental_option("detach", True)
CHROME_OPTIONS.add_argument("--incognito")
CHROME_OPTIONS.add_argument("--disable-gpu")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--remote-debugging-port=9222")
CHROME_OPTIONS.add_argument("--disable-setuid-sandbox")
CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")  # Recommended for Render
#CHROME_OPTIONS.add_argument("--user-data-dir=/tmp/chrome_user_data")  # Unique data dir
#CHROME_OPTIONS.add_argument(
#    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
#CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
#CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])


driver = webdriver.Chrome(options=CHROME_OPTIONS)
wait = WebDriverWait(driver, 60)  # Increased timeout for Render's slower responses


# Helper Functions
def send_telegram_notification(message):
    """Send a notification via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print("Notification sent via Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")


def safe_find(by, value):
    try:
        return wait.until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        driver.save_screenshot("error_screenshot.png")  # Save screenshot for debugging
        print(driver.page_source)  # Log page source
        raise RuntimeError(f"Error locating element by {by}: {value}") from e


def safe_click(by, value):
    """Wait for an element and click it."""
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
    except Exception as e:
        print(f"Error clicking element: {e}")
        raise RuntimeError(f"Error clicking element by {by}: {value}") from e


def login():
    """Log in to the application."""
    try:
        safe_find(By.ID, email_field).send_keys(email)
        password_input = safe_find(By.ID, password_field)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(10)  # Allow time for the login to process
    except Exception as e:
        raise RuntimeError("Error during login process.") from e


def run_script():
    try:
        # Navigate to the website
        driver.get(link)
        time.sleep(10)

        # Wait for login button and proceed
        login_buttons = safe_find(By.XPATH, login_button)
        while not login_buttons.is_displayed():
            send_telegram_notification("Page didn't load correctly. Waiting 40 Sec")
            time.sleep(40)
            #driver.refresh()

        send_telegram_notification("Page loaded correctly. No waiting needed. Continuing... ")

        # Perform login
        safe_click(By.XPATH, login_button)
        login()

        # Navigate to Application Page
        application_button = safe_find(By.XPATH, enter_application_button)
        actions = ActionChains(driver)
        time.sleep(5)
        actions.move_to_element(application_button).click().perform()

        # Book Appointment
        book_button = safe_find(By.XPATH, book_appointment)
        actions = ActionChains(driver)
        time.sleep(10)
        actions.move_to_element(book_button).click().perform()

        # Slot Checking Loop
        while True:
            try:
                no_slots_element = safe_find(By.XPATH, no_slots_confirm)
                if no_slots_element.is_displayed():
                    print("No slots available. Retrying...")
                    send_telegram_notification("No free slots available yet.")
                    no_slots_element.click()
                    driver.refresh()
                    time.sleep(600)
                    login()  # Re-login if necessary
                else:
                    print("Slots available!")
                    send_telegram_notification("🎉 Free slots are available! Go book them now!")
                    break
            except Exception as e:
                print(f"Error occurred while checking slots: {e}")
                send_telegram_notification("An error occurred while checking slots.")
                break
    finally:
        driver.quit()
        print("Script execution completed.")


if __name__ == "__main__":
    try:
        while True:  # Infinite loop to keep the script running
            run_script()  # Call the main logic of script
            time.sleep(60)  # Wait for 60 seconds before the next iteration
    except KeyboardInterrupt:
        print("Script stopped manually.")
