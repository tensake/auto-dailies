import traceback
import time
import random
import re
import functools

from selenium.webdriver.support.ui import WebDriverWait
from difflib import SequenceMatcher
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import overload, Literal
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidElementStateException,
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
)

from src.constants import SwalSelectors, Condition, SelEnum, \
    CurrencyType
from src.logger import prerror, prdebug
from src.models import Swal
from src.config import CONFIG

def wait_for(c, wait: WebDriverWait, sel: SelEnum) -> WebElement | None:
    """
    Wait for a selector to satisfy the given condition
    and then return the WebElement.
    """
    try:
        return wait.until(c(sel))
    except TimeoutException:
        prdebug(f"Timeout while waiting for {sel}")
    except WebDriverException as e:
        prerror(f"Driver error while waiting for {sel}: {e}")
    except AttributeError as e:
        prerror(f"Invalid selector {sel}: {e}")

    return None

@overload
def find(driver, sel: SelEnum | tuple[str, str], *, multiple: Literal[True]) -> list[WebElement]: ...
@overload
def find(driver, sel: SelEnum | tuple[str, str], *, multiple: Literal[False] = False) -> WebElement | None: ...
def find(driver: WebDriver | WebElement, sel: SelEnum | tuple[str, str], *, multiple: bool = False
) -> WebElement | None | list[WebElement]:
    """
    Find an element and return it.
    Also supports finding multiple elements.
    """
    try:
        if multiple:
            return driver.find_elements(*sel)
        return driver.find_element(*sel)

    except (NoSuchElementException, StaleElementReferenceException):
        prdebug(f"Element not found: {sel}")

    except WebDriverException as e:
        prerror(f"Driver error while finding element {sel}: {e}")

    return [] if multiple else None

def switch_newtab(driver) -> str:
    """Switch the driver to a new tab. """
    driver.switch_to.window(driver.window_handles[-1])
    return driver.current_window_handle

def tab_exists(driver, handle: str) -> bool:
    try:
        return handle in driver.window_handles
    except Exception:
        return False

def close_all_tabs(driver):
    """Close all tabs. """
    for tab in driver.window_handles:
        driver.switch_to.window(tab)
        driver.close()

def handle_exceptions(default=None, retry: bool = False):
    """
    A decorator that catches and logs any exceptions
    if has exceptions returns a default value.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_result = None
            for _ in range(2 if retry else 1):
                try:
                    res = func(*args, **kwargs)
                    prdebug(f"{func.__name__} result: {res}")

                    if getattr(res, "success", True):
                        return res
                    last_result = res
                except Exception as e:
                    tb = traceback.format_exc()
                    prdebug(f"Exception in {func.__name__}: {e}\n{tb}")
            return last_result if last_result is not None else default
        return wrapper
    return decorator

def parse_text(el: WebElement | str | None) -> str | None:
    if el:
        return el.text.strip() if isinstance(el, WebElement) else el.strip()
    return None

def parse_attr(el: WebElement | None, attr: str = "class") -> str:
    if el:
        return str(el.get_attribute(attr))
    return ''

@overload
def parse_num(el: WebElement | str | None, is_percent: Literal[True]) -> float | None: ...
@overload
def parse_num(el: WebElement | str | None, is_percent: Literal[False] = False) -> int | None: ...
def parse_num(el: WebElement | str | None, is_percent: bool = False) -> int | float | None:
    if el:
        num = re.search(r'\d+', str(parse_text(el)))
        if num:
            res = int(num.group())
            if is_percent:
                res = float(res) / 100
            return res
    return None

def parse_img(el: WebElement | None) -> str:
    return parse_attr(el, "src")

def parse_currency(el: WebElement | str | None) -> CurrencyType:
    res = CurrencyType.UNKNOWN
    tex = str(parse_text(el)).lower()

    words = [w for w in tex.split() if '-' not in w] # ignore mor-lg
    tex = words[-1]

    if 'чайник' in tex or 'coin' in tex:
        res = CurrencyType.COIN
    elif 'мор' in tex or 'mor' in tex:
        res = CurrencyType.GOLD
    elif 'рис' in tex or 'rice' in tex:
        res = CurrencyType.RICE
    return res

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def compare_list(a: str, b: list[str]) -> float:
    """Compare a string against a list of strings. """
    return any(similarity(a, item) for item in b)

def random_sleep(amount: float = 2.0, r: float = 0.5):
    """Sleep for certain amount of time with a random jitter. """
    time.sleep(max(0.0, amount + random.uniform(-r, r)))

def is_docker():
    """Check if running in a Docker container. """
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or (cgroup.is_file() and 'docker' in cgroup.read_text())

def scroll_into(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

def click_el(driver, element, retries=5):
    for i in range(retries):
        try:
            if element:
                wait_for(Condition.CLICKABLE, WebDriverWait(driver, CONFIG.wait_timeout), element)
                scroll_into(driver, element)
                element.click()
                return True
        except (ElementClickInterceptedException,
                StaleElementReferenceException,
                ElementNotInteractableException,
                InvalidElementStateException) as e:
            prdebug(f"Click attempt {i + 1} failed: {e}")
    return False

def get_swal(driver) -> Swal:
    """Get 'SweetAlert' (swal) alert. """
    wait = WebDriverWait(driver, CONFIG.wait_timeout)

    swal = wait_for(Condition.PRESENCE, wait, SwalSelectors.MODAL)
    time.sleep(0.5) # animation
    if swal:
        title = find(swal, SwalSelectors.TITLE)
        text = find(swal, SwalSelectors.TEXT)
        icon = find(swal, SwalSelectors.ICON)

        confirm_button = wait_for(Condition.CLICKABLE, wait, SwalSelectors.CONFIRM_BUTTON)

        # Some alerts have content and footer instead of title, text and icon
        if not title or not text:
            content = find(swal, SwalSelectors.CONTENT)
            if content:
                title = find(content, SwalSelectors.CONTENT_TITLE)
                text = find(content, SwalSelectors.CONTENT_TEXT)
                icon = find(content, SwalSelectors.CONTENT_ICON)

        data = Swal(
            title=parse_text(title),
            text=parse_text(text),
            icon=parse_img(icon),
            confirm_button=confirm_button
        )
        prdebug(data)
        return data

    return Swal()
