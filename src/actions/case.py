import random

from selenium.webdriver.support.ui import WebDriverWait

from src.logger import prinfo, prerror, prsuccess
from src.config import CONFIG
from src.models import Case, CasesResult
from src.common import random_sleep, get_swal, parse_num, click_el, \
    handle_exceptions, wait_for, find, parse_attr, parse_img, \
    parse_text, parse_currency
from src.constants import BASE_URL, IGNORE_CASES, \
    CaseSelectors, Condition, CurrencyType

def get_cases(driver) -> list[Case]:
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != BASE_URL:
        driver.get(BASE_URL)

    # Get case elements
    wait_for(Condition.PRESENCE, wait, CaseSelectors.BOX)
    res: list[Case] = []

    # Get containers for each game
    for container in find(driver, CaseSelectors.BOX, multiple=True):
        # Get case info for every container
        for case in find(container, CaseSelectors.CASE, multiple=True):
            href = parse_attr(case, "href")
            if href == '' or href in [case.link for case in res]:
                continue
            image = parse_img(find(case, CaseSelectors.IMAGE))
            name = parse_text(find(case, CaseSelectors.NAME))

            res.append(
                Case(
                    link=href,
                    image=image,
                    name=name,
                    is_ignored=href.split("/")[-1] in IGNORE_CASES,
                    is_target=href.split("/")[-1].lower() == CONFIG.target_case.lower(),
                )
            )

    return res

def open_case(driver, case: Case) -> bool:
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != case.link:
        driver.get(case.link)

    wait_for(Condition.PRESENCE, wait, CaseSelectors.CARD_LIST)
    random_sleep(3) # card animation

    # Extract case price
    price = None
    reqs_el = find(driver, CaseSelectors.REQUIREMENTS)
    if reqs_el:
        # Try to parse the price from all requirements
        for req_el in find(reqs_el, CaseSelectors.REQUIREMENT, multiple=True):
            if parse_currency(req_el) == CurrencyType.COIN:
                price = parse_num(req_el)

    # Decide if to open the case
    if case.is_target:
        prinfo("Target case detected. Opening regardless of price...")
    elif price is None:
        prinfo("No coin requirement found, opening the case anyway...")
    elif price > CONFIG.case_price_threshold:
        prinfo(f"Case price ({price}) is higher than threshold ({CONFIG.case_price_threshold}), skipping...")
        return False
    else:
        prinfo(f"Case price: {price} coins. Opening...")

    # Open the case
    card_el = find(driver, CaseSelectors.CARD_LIST)
    if card_el:
        available_cards = find(card_el, CaseSelectors.CARD, multiple=True)
        click_el(driver, random.choice(available_cards))

        # Check if successful
        swal = get_swal(driver)
        if not swal.text:
            return True

    return False

@handle_exceptions(default=CasesResult(success=False, reason="Failed to open cases"))
def run_cases(driver) -> CasesResult:
    opened_cases = 0
    ignored_cases = 0
    available_cases = get_cases(driver)

    for case in available_cases:
        # Skip ignored cases, unless target
        if case.is_target or not case.is_ignored:
            prinfo(f"Opening case: {case.name if case.name != '' else case.link}...")
            if open_case(driver, case):
                prsuccess(f"Opened case: {case.name}")
                opened_cases += 1
            else:
                prerror(f"Failed to open case: {case.name}")

            # Cooldown after each case
            random_sleep(7)
        else:
            ignored_cases += 1

    return CasesResult(
        success=True,
        available_cases=available_cases,
        opened_cases=opened_cases,
        ignored_cases=ignored_cases,
    )
