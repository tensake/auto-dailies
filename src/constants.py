from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from enum import Enum

IGNORE_CASES = [
    # Other
    "druzeskii-keis",

    # Genshin
    "nescatnaya-paimon",
    "bednaya-mona",
    "korobka-vezuncika",
    "vse-ili-nicego",
    "damaznaya-udaca",
    "korobka-inadzumy",
    "dar-arxontov",
    "pokrovitelstvo-dilyuka",

    # HSR
    "usastaya-korobka",
    "lecebnaya-korobocka",
    "korobka-straza",
    "xakasskaya-korobka",
    "skrytaya-korobka-zele",
    "oruzeinaya-korobka-kafki",

    # ZZZ
    "kartonnyi-tv-boks",
    "tv-boks-randomplay",
    "tv-boks-agentstva-viktoriya",
    "korobka-zaicev",
    "tv-boks-sekcii-6",
    "tv-boks-ot-kombinata-belobog",
]

IGNORE_ITEMS = [
    # Limited items
    "2021", "2022", "2023", "2024", "2025", "2026"
    "памят",
    "сувенир",
    "фигурк",
    "чиби",

    # Paid items
    "кристалл",
    "благослов",
    "гранул",
    "гем",
    "молитв",
    "скин",
    "пак",
]

BASE_URL: str = "https://genshindrop.io"
CHECKIN_URL: str = f"{BASE_URL}/checkin"
GIVEAWAY_URL: str = f"{BASE_URL}/give"
PROFILE_URL: str = f"{BASE_URL}/profile"

class SelEnum(tuple, Enum):
    """Base class for selector enums. """
    @property
    def by(self) -> str: return self._value_[0]

    @property
    def val(self) -> str: return self._value_[1]

    def __new__(cls, value: tuple[str, str]):
        obj = tuple.__new__(cls, value)
        obj._value_ = value
        return obj

    def __str__(self):
        return f"{self.value[0]}={self.value[1]}"

class SwalSelectors(SelEnum):
    OVERLAY = (By.CLASS_NAME, 'swal-overlay')
    MODAL = (By.CLASS_NAME, 'swal-modal')
    CONTENT = (By.CLASS_NAME, 'swal-content')
    FOOTER = (By.CLASS_NAME, 'swal-footer')

    TITLE = (By.CLASS_NAME, 'swal-title')
    TEXT = (By.CLASS_NAME, 'swal-text')
    ICON = (By.CLASS_NAME, 'swal-icon')
    CONFIRM_BUTTON = (By.CSS_SELECTOR, ".swal-button.swal-button--confirm")

    CONTENT_TITLE = (By.TAG_NAME, 'h2')
    CONTENT_TEXT = (By.TAG_NAME, 'p')
    CONTENT_ICON = (By.TAG_NAME, 'img')

class CommonSelectors(SelEnum):
    """Selectors for common elements. """
    CONFIRM_BUTTON = (By.CLASS_NAME, 'swal-button swal-button--confirm')
    LINK = (By.TAG_NAME, 'a')
    IFRAME = (By.TAG_NAME, 'iframe')
    BUTTON = (By.TAG_NAME, 'button')

class LoginSelectors(SelEnum):
    """Selectors for telegram login actions. """
    SECRET_CODE = (By.CLASS_NAME, 'my-secret-code-value_val')
    LOGIN_BUTTON = (By.CSS_SELECTOR, "a.header-signin")
    TG_LOGIN_BUTTON = (By.CSS_SELECTOR, 'a.login-button.login-button_telegram')

    TG_PHONE_INPUT = (By.CSS_SELECTOR, 'input#login-phone.form-control')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    ACCEPT_BUTTON = (By.XPATH, "//button[@onclick='return confirmRequest()']")

class CheckinSelectors(SelEnum):
    """Selectors for check in page. """
    BUTTON = (By.CLASS_NAME, 'checkin-day-today-label-check')
    STREAK = (By.CSS_SELECTOR, 'div.checkin-today-value_text')
    MONTHLY_BONUS = (By.XPATH, "//div[contains(@class, 'checkin-status-item_value')]/i[contains(@class, 'i-calendar')]/..")
    PAYMENTS_BONUS = (By.XPATH, "//div[contains(@class, 'checkin-status-item_value')]/i[contains(@class, 'i-shop')]/..")
    SKIP_AVAILABLE = (By.CSS_SELECTOR, 'i.i.i-check')
    NOT_SKIP_AVAILABLE = (By.CSS_SELECTOR, 'i.i.i-cross')

class GiveawaySelectors(SelEnum):
    """Selectors for giveaway page. """
    LINK = (By.CLASS_NAME, 'give-box__link')
    GIVEAWAY = (By.CSS_SELECTOR, ".panel.give-box.col-12:not(.--history)")
    PAST_GIVEAWAY_BOX = (By.CSS_SELECTOR, ".give__endlist")
    PAST_GIVEAWAY = (By.CSS_SELECTOR, ".panel.give-box.--history")
    PRICE = (By.CLASS_NAME, 'give-pay_price__value')
    CURRENCY = (By.CSS_SELECTOR, '.give-pay_price__value i')
    JOIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Участвовать')]")

    WIN_BUTTON = (By.CSS_SELECTOR, 'button.give-prize_data__users_user__getprize')
    WIN_ITEM_TEXT = (By.CSS_SELECTOR, ".craft-recept-item .craft-recept-item__simple-title > div")
    WIN_PROMOCODE = (By.CSS_SELECTOR, 'div.my-secret-code-value div.my-secret-code-value_val')

class CaseSelectors(SelEnum):
    """Selectors for cases. """
    BOX = (By.CLASS_NAME, 'index-cat-container')
    CASE = (By.CLASS_NAME, 'index-case')
    IMAGE = (By.CLASS_NAME, 'index-case_cover')
    NAME = (By.CLASS_NAME, 'index-case_name')
    PRICE = (By.CLASS_NAME, 'index-case_price')

    REQUIREMENTS = (By.CLASS_NAME, 'give-requirements-list')
    REQUIREMENT = (By.CLASS_NAME, 'give-requirements-list_item__text')

    CARD_LIST = (By.CLASS_NAME, 'box-page-loot-cards')
    CARD = (By.CLASS_NAME, 'box-page-loot-cards-card')

class StateSelectors(SelEnum):
    """Selectors for state information. """
    GOLD = (By.CSS_SELECTOR, "span[data-key='user_mor_value']")
    COINS = (By.CSS_SELECTOR, "span[data-key='user_coin_value']")

class ProfileSelectors(SelEnum):
    """Profile page selectors. """
    PANEL_BOX = (By.CLASS_NAME, 'profile-account-panel')
    USERNAME = (By.CLASS_NAME, 'profile-username')

    DATA_BOX = (By.CLASS_NAME, 'profile-user-data')
    ID = (By.XPATH, '//span[contains(text(), "ID")]')
    AVATAR = (By.CSS_SELECTOR, 'div.profile-avatar img')
    RICE = (By.CSS_SELECTOR, 'div.profile-balance_value.rice span.icur-container > span')
    IS_VERIFIED = (By.CSS_SELECTOR, 'div.profile-verified_icon')

class InventorySelectors(SelEnum):
    """Profile inventory selectors. """
    BOX = (By.CLASS_NAME, 'inventory-item-wrapper')
    ITEM_BOX = (By.CSS_SELECTOR, 'div.inventory-item.win div.inventory-item_left')

    IMAGE = (By.CLASS_NAME, 'inventory-item_left__cover')
    NAME = (By.CLASS_NAME, 'profile-item-left-name')
    PRICE = (By.CSS_SELECTOR, 'span.icur-container.ml-1')
    SELL_BUTTON = (By.CSS_SELECTOR, 'a.inventory-item-link.inventory-item-link_sell')
    CURRENCY_TYPE = (By.XPATH, './/span[contains(@class,"icur-container")]//i')

    LOAD_MORE_BUTTON = (By.XPATH, '//button[contains(@class, "btn") and contains(normalize-space(.), "Больше")]')

class Condition:
    """
    Conditions for finding the element.
    """
    PRESENCE = EC.presence_of_element_located
    CLICKABLE = EC.element_to_be_clickable
    VISIBLE = EC.visibility_of_element_located

class CurrencyType(str, Enum):
    COIN = "coin"
    GOLD = "mora"
    RICE = "rice"
    UNKNOWN = "unknown"

class CaseResultType(str, Enum):
    """
    Result types for cases.

    Use text in swal for comparing.
    """
    COOLDOWN_FAILURE = "С момента последнего открытия коробки еще не прошло достаточно времени"
    PAYMENTS_FAILURE = "Выводы и покупки за указанное время не найдены 😔 Необходимо иметь хотя бы один вывод или покупку"

class GiveawayResultType(str, Enum):
    """
    Result messages for giveaways.

    Use title in swal for comparing.
    """
    SUCCESS = "Вы в раздаче"
    FAILURE = "Не получилось"

class SellResultType(str, Enum):
    """
    Result messages for selling items.

    Use title in swal for comparing.
    """
    SUCCESS = "Продано"
