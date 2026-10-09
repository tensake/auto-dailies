from selenium.webdriver.support.ui import WebDriverWait

from src.config import CONFIG
from src.models import GiveawayResult
from src.logger import prsuccess, prwarn, prinfo
from src.constants import GIVEAWAY_URL, GiveawaySelectors, Condition, \
    GiveawayResultType
from src.common import random_sleep, get_swal, parse_num, \
    handle_exceptions, click_el, wait_for, find, parse_attr, \
    CurrencyType, parse_currency, parse_text

@handle_exceptions(default=GiveawayResult(success=False, reason="Failed to join giveaways"))
def run_giveaway(driver) -> GiveawayResult:
    """Checks out all giveaways on the giveaways main page. """
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != GIVEAWAY_URL:
        driver.get(GIVEAWAY_URL)

    # Wait for at least one giveaway to load, then get all giveaways
    wait_for(Condition.VISIBLE, wait, GiveawaySelectors.GIVEAWAY)
    giveaways = find(driver, GiveawaySelectors.GIVEAWAY, multiple=True)
    links = []
    for giveaway in giveaways:
        links.append(
            parse_attr(find(giveaway, GiveawaySelectors.LINK), "href")
        )

    # Check past giveaways
    box = wait_for(Condition.VISIBLE, wait, GiveawaySelectors.PAST_GIVEAWAY_BOX)
    past_links = []
    if box:
        giveaways = find(box, GiveawaySelectors.PAST_GIVEAWAY, multiple=True)
        for giveaway in giveaways:
            past_links.append(
                parse_attr(find(giveaway, GiveawaySelectors.LINK), "href")
            )

    # Join all giveaways
    joined = []
    for link in links:
        prinfo(f"Checking out giveaway: {link}")
        random_sleep(1)
        if join_giveaway(driver, link):
            joined.append(link)
            random_sleep(5)

    # Check if won any past giveaway
    won_giveaways = []
    for link in past_links:
        prinfo(f"Checking out past giveaway: {link}")
        random_sleep(1)
        won = check_won_giveaway(driver, link)
        if won:
            won_giveaways.append(won)
            random_sleep(1)

    return GiveawayResult(
        success=True,
        giveaways=links,
        joined=joined,
        won=won_giveaways
    )

def join_giveaway(driver, href) -> bool:
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != href:
        driver.get(href)

    # Wait for join button
    join_button = wait_for(Condition.CLICKABLE, wait, GiveawaySelectors.JOIN_BUTTON)
    if not join_button:
        prwarn("No giveaway join button detected. Seems like you already joined this giveaway")
        return False

    # Decide if to join the giveaway
    price_element = wait_for(Condition.PRESENCE, wait, GiveawaySelectors.PRICE)
    if price_element:
        price = parse_num(price_element)
        currency = parse_currency(parse_attr(find(price_element, GiveawaySelectors.CURRENCY)))
        if currency in [CurrencyType.GOLD]:
            prwarn(f"Giveaway currency is {currency.value}. Skipping.")
            return False
        if price and currency == CurrencyType.COIN:
            if price > CONFIG.giveaway_price_threshold:
                prwarn(f"Giveaway price ({price} {currency.value}) is above {CONFIG.giveaway_price_threshold}. Skipping.")
                return False

    # Join giveaway
    click_el(driver, join_button)
    swal = get_swal(driver)
    if swal.title or swal.text:
        prsuccess(f"Giveaway join button clicked for {href}.")
        if swal.title == GiveawayResultType.FAILURE:
            return False

    return True

def check_won_giveaway(driver, href) -> dict[str, str | None] | None:
    wait = WebDriverWait(driver, CONFIG.wait_timeout)
    if driver.current_url != href:
        driver.get(href)

    # Check if we won something from giveaway
    claim_price_button = wait_for(Condition.CLICKABLE, wait, GiveawaySelectors.WIN_BUTTON)
    if not claim_price_button:
        return None
    prsuccess(f"Won giveaway! {href}")

    # Get price info
    click_el(driver, claim_price_button)
    swal = get_swal(driver)
    if swal.title or swal.text:
        return {
            "promocode": parse_text(wait_for(Condition.VISIBLE, wait, GiveawaySelectors.WIN_PROMOCODE)),
            "item_text": parse_text(wait_for(Condition.VISIBLE, wait, GiveawaySelectors.WIN_ITEM_TEXT)),
            "item_icon": swal.icon
        }

    return None
