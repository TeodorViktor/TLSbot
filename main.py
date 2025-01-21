import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from variables import *
import variables
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
email = os.getenv("email")
password = os.getenv("password")

# Selenium WebDriver Settings
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_experimental_option("detach", True)
CHROME_OPTIONS.add_argument("--incognito")
CHROME_OPTIONS.add_argument("--disable-gpu")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")  # Recommended for Render
driver = webdriver.Chrome(options=CHROME_OPTIONS)
wait = WebDriverWait(driver, 30)


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
    """Wait for an element and return it."""
    try:
        return wait.until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        print(f"Error locating element: {e}")
        raise


def safe_click(by, value):
    """Wait for an element and click it."""
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
    except Exception as e:
        print(f"Error clicking element: {e}")
        raise


def login_if_page_loggedout():
    """Log in if the page is logged out."""
    try:
        email_input = safe_find(By.ID, email_field)
        email_input.send_keys(email)
        password_input = safe_find(By.ID, password_field)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(10)
    except Exception as e:
        print(f"Error during login: {e}")


# Main Script
def run_script():
    try:
        # Navigate to the website
        driver.get(link)
        driver.maximize_window()
        time.sleep(10)
        while True:
            try:
                login_buttons = safe_find(By.XPATH, login_button)
                if not login_buttons.is_displayed():
                    driver.refresh()
                    time.sleep(10)
                else:
                    break
            except Exception as e:
                print(f"Page didn't load correctly: {e}")
                send_telegram_notification("Page didn't load correctly.")
                break
        # Login
        safe_click(By.XPATH, login_button)
        safe_find(By.ID, email_field).send_keys(email)
        password_field = safe_find(By.ID, variables.password_field)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)

        # Navigate to Application Page
        if safe_find(By.XPATH, enter_application_button).is_displayed():
            safe_click(By.XPATH, enter_application_button)

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
                    login_if_page_loggedout()
                else:
                    print("Slots available!")
                    send_telegram_notification("🎉 Free slots are available! Go book them now!")
                    break
            except Exception as e:
                print(f"Error occurred while checking slots: {e}")
                send_telegram_notification("An error occurred while checking slots.")
                break
    finally:
        # driver.quit()
        print("Script execution completed.")


if __name__ == "__main__":
    try:
        while True:  # Infinite loop to keep the script running
            run_script()  # Call the main logic of your script
            time.sleep(60)  # Wait for 60 seconds before the next iteration
    except KeyboardInterrupt:
        print("Script stopped manually.")  # Graceful exit if stopped
