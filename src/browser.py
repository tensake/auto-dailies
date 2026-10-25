import pickle
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from src.config import CONFIG
from src.common import is_docker
from src.logger import prdebug

def create_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = CONFIG.chromium_path
    if (CONFIG.headless if not CONFIG.new_account else False):
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    if is_docker():
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # Ignore images and trackers loading
    options.page_load_strategy = "eager"

    # Remove browser automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # User agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    )
    options.add_argument("--window-size=1920,1080")

    service = Service(executable_path=CONFIG.chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Remove navigator.webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
    })

    return driver

def load_cookies(driver, cookie_file) -> tuple[bool, str]:
    """
    Read, filter and inject cookies in to the driver.

    Returns:
        tuple[bool, str]: (success, error)
    """

    # Read cookies from file
    if not os.path.exists(cookie_file):
        return False, "Cookie file not found."
    try:
        with open(cookie_file, "rb") as f:
            cookies = pickle.load(f)
    except Exception as e:
        return False, f"Failed to read cookie file: {e}"

    # Get all valid cookies by filtering expired cookies and sorting by priority
    now = time.time()
    valid_cookies = [c for c in cookies if c.get("expiry", now + 1) > now]
    valid_cookies.sort(key=lambda c: not c["name"].startswith(("XSRF-TOKEN", "app_uid", "remember_web_")))

    # Filter cookies to stay under limit
    kept = []
    total_size = 0
    for cookie in valid_cookies:
        size = len(cookie["name"]) + 1 + len(cookie["value"]) + 2
        if total_size + size > 7800: # this is to stay under nginx's 8192 bytes limit
            continue
        if "sameSite" in cookie:
            cookie["sameSite"] = cookie["sameSite"].capitalize()
        kept.append(cookie)
        total_size += size

    prdebug(f"Got {len(kept)}/{len(cookies)} cookies, {len(cookies) - len(valid_cookies)} expired skipped, total {total_size} bytes.")

    # Add cookies
    try:
        for cookie in kept:
            driver.add_cookie(cookie)
        return True, ""
    except Exception as e:
        return False, f"Failed to load cookies: {e}"

def save_cookies(driver, cookie_file): pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
