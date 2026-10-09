from selenium.webdriver.support.ui import WebDriverWait

from src.logger import prsuccess, prwarn
from src.common import get_swal, parse_num, click_el, handle_exceptions, \
    wait_for, find, parse_currency
from src.config import CONFIG
from src.constants import CHECKIN_URL, CheckinSelectors, Condition
from src.models import CheckinResult, CurrencyType

@handle_exceptions(default=CheckinResult(success=False, reason="Failed to check in"), retry=True)
def run_daily_checkin(driver) -> CheckinResult:
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != CHECKIN_URL:
        driver.get(CHECKIN_URL)

    # Check if button exists
    button = wait_for(Condition.CLICKABLE, wait, CheckinSelectors.BUTTON)
    if not button:
        prwarn("No daily check-in button detected. Seems like you already checked in today")
        return _build_result(driver, success=False, title=None, reason="Already checked in")

    # Click checkin button
    click_el(driver, button)
    prsuccess("Daily check-in button clicked")

    # Check if chekin was successful
    # Handle no response
    swal = get_swal(driver)
    if not swal:
        prwarn("No response after check-in click")
        driver.refresh()
        return _build_result(driver, success=False, title=None, reason="No response from button")

    # Handle error from checkin
    text = (swal.text or "").lower()
    fail_texts = ["fail", "системная ошибка"]
    if any(t in text for t in fail_texts):
        prwarn(f"Check-in failed: {swal.text}")
        driver.refresh()
        return _build_result(driver, success=False, title=None, reason=f"Site error: {swal.text}")

    swal.click_confirm()
    return _build_result(driver, success=True, title=swal.title, reason=None)

def _build_result(driver, success: bool, title, reason) -> CheckinResult:
    streak = parse_num(find(driver, CheckinSelectors.STREAK))
    monthly_bonus = parse_num(find(driver, CheckinSelectors.MONTHLY_BONUS), is_percent=True)
    payments_bonus = parse_num(find(driver, CheckinSelectors.PAYMENTS_BONUS), is_percent=True)
    skipped_day = not bool(find(driver, CheckinSelectors.SKIP_AVAILABLE))

    return CheckinResult(
        success=success,
        streak=streak or 0,
        monthly_bonus=monthly_bonus or 0.0,
        payments_bonus=payments_bonus or 0.0,
        skipped_day=skipped_day,
        earned=(parse_num(title) or 0) if title else 0,
        currency_type=parse_currency(title) if title else CurrencyType.UNKNOWN,
        reason=reason,
    )
