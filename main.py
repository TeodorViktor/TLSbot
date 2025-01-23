import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from variables import *
import requests
from dotenv import load_dotenv
import cloudscraper
from simpleserver import *

# Initialize cloudscraper
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
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--incognito")
CHROME_OPTIONS.add_argument("--disable-gpu")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")
CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
CHROME_OPTIONS.add_experimental_option("detach", True)
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=CHROME_OPTIONS)
wait = WebDriverWait(driver, 60)


# Helper Functions
def send_telegram_notification(message):
    """Send a notification via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")


def safe_find(by, value, timeout=60):
    """Wait and locate an element."""
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        driver.save_screenshot("error_screenshot.png")
        with open("error_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise RuntimeError(f"Error locating element by {by}: {value}") from e


def safe_click(by, value):
    """Wait and click an element."""
    element = safe_find(by, value)
    try:
        element.click()
    except Exception as e:
        raise RuntimeError(f"Error clicking element by {by}: {value}") from e


def login():
    """Log in to the application."""
    safe_find(By.ID, email_field).send_keys(email)
    password_input = safe_find(By.ID, password_field)
    password_input.send_keys(password, Keys.ENTER)
    time.sleep(5)  # Allow time for the login to process


def check_slots():
    """Check for available slots and notify if found."""
    try:
        no_slots_element = safe_find(By.XPATH, no_slots_confirm, timeout=30)
        if no_slots_element.is_displayed():
            send_telegram_notification("No free slots available yet. Retrying...")
            driver.refresh()
            time.sleep(600)  # Wait before retrying
        else:
            send_telegram_notification("🎉 Free slots are available! Go book them now!")
            return True
    except Exception:
        send_telegram_notification("An error occurred while checking slots.")
    return False


def run_script():
    """Main script logic."""
    try:
        driver.get(link)
        safe_click(By.XPATH, login_button)
        login()

        safe_click(By.XPATH, enter_application_button)
        time.sleep(2)

        safe_click(By.XPATH, book_appointment)
        time.sleep(2)

        while not check_slots():
            time.sleep(60)  # Retry every minute
    finally:
        driver.quit()


if __name__ == "__main__":
    try:
        while True:
            run_script()
    except KeyboardInterrupt:
        print("Script stopped manually.")
