from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait

from src.logger import prsuccess
from src.constants import LoginSelectors, CommonSelectors, Condition
from src.config import CONFIG
from src.constants import BASE_URL, PROFILE_URL
from src.common import handle_exceptions, wait_for, click_el, \
    switch_newtab, random_sleep, tab_exists, parse_text

def get_secretcode(driver) -> str | None:
    """Get user secret code for verification in Telegram bot. """
    if driver.current_url != PROFILE_URL:
        driver.get(PROFILE_URL)

    driver.execute_script('$("#MySecretCode").modal("show");')
    random_sleep(2)
    return parse_text(
        wait_for(
            Condition.PRESENCE,
            WebDriverWait(driver, CONFIG.wait_timeout),
            LoginSelectors.SECRET_CODE
        )
    )

@handle_exceptions(default=False)
def oauth_loop(driver, tab) -> bool:
    """Oauth window loop for Telegram login. """
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    while tab_exists(driver, tab):
        # Check for phone input
        phone_input = wait_for(
            Condition.CLICKABLE, wait, LoginSelectors.TG_PHONE_INPUT
        )
        if phone_input:
            for i in range(4):
                random_sleep(0.3, 0.1)
                phone_input.send_keys(Keys.BACKSPACE)
            phone_input.send_keys(str(CONFIG.new_account), Keys.ENTER)

        # Check for accept button
        if tab_exists(driver, tab):
            if click_el(driver, wait_for(
                Condition.CLICKABLE, wait, LoginSelectors.ACCEPT_BUTTON
            )):
                break

    return True

@handle_exceptions(default=False)
def run_login_tg(driver) -> bool:
    """Login using Telegram with a phone number set in config. """
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    driver.get(CONFIG.referral_url or BASE_URL)
    origin_tab = driver.current_window_handle

    # Open Telegram login page if not open already. Don't retry because
    # theres a possiblity of this form appearing automatically.
    click_el(
        driver,
        wait_for(
            Condition.CLICKABLE,
            wait,
            LoginSelectors.LOGIN_BUTTON),
        retries=0
    )

    # Proceed with authentication
    if click_el(driver, wait_for(
        Condition.CLICKABLE, wait, LoginSelectors.TG_LOGIN_BUTTON
        )):
        # Open Telegram OAuth window
        tg_tab = switch_newtab(driver)
        tg_iframe = wait_for(
            Condition.PRESENCE, wait, CommonSelectors.IFRAME
        )
        if tg_iframe:
            driver.switch_to.frame(tg_iframe)
            click_el(driver, wait_for(
                Condition.CLICKABLE, wait, CommonSelectors.BUTTON
            ))
            # Complete oauth
            if oauth_loop(driver, switch_newtab(driver)):
                # Switch back to tg login tab
                driver.switch_to.window(tg_tab)
                click_el(driver, wait_for(
                    Condition.CLICKABLE, wait, CommonSelectors.BUTTON
                ))
                driver.close()

                # Switch back to main window and refresh
                driver.switch_to.window(origin_tab)
                driver.refresh()

                prsuccess(f"Login successful, secret code: {get_secretcode(driver)}")
                return True

    return False
