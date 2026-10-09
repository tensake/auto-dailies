from selenium.webdriver.remote.webelement import WebElement
from dataclasses import dataclass, field, fields

from src.constants import CurrencyType
from src.config import CONFIG

@dataclass(slots=True)
class Result:
    success: bool
    reason: str | None = None

    def __post_init__(self):
        if self.success and self.reason is not None:
            raise ValueError("Cannot have reason when success is True")

    def __str__(self):
        return ', '.join(
            f"{f.name}={getattr(self, f.name)}"
            for f in fields(self)
            if getattr(self, f.name) is not None
        )

@dataclass(slots=True)
class Swal:
    title: str | None = None
    text: str | None = None
    icon: str | None = None
    confirm_button: WebElement | None = None

    def click_confirm(self) -> bool:
        if self.confirm_button:
            self.confirm_button.click()
            return True
        return False

@dataclass(slots=True)
class Case:
    link: str
    is_ignored: bool
    is_target: bool
    image: str | None = None
    name: str | None = None

@dataclass(slots=True)
class Balance:
    gold: int = 0
    coins: int = 0

@dataclass(slots=True)
class InventoryItem:
    name: str
    image: str | None = None
    price: int | None = None
    currency_type: CurrencyType = CurrencyType.UNKNOWN
    sold: bool = False

@dataclass(slots=True)
class InventoryMeta:
    all_coins: int = 0
    all_gold: int = 0
    sold_items: list = field(default_factory=list)

@dataclass(slots=True)
class Profile:
    id: str
    avatar_url: str | None = None
    username: str | None = None
    rice: int | None = None
    is_verified: bool | None = None

    balance: Balance = field(default_factory=Balance)

    inventory: list[InventoryItem] = field(default_factory=list)

    @property
    def inventory_meta(self) -> InventoryMeta:
        return InventoryMeta(
            sum(i.price or 0 for i in self.inventory if i.currency_type is CurrencyType.COIN and not i.sold),
            sum(i.price or 0 for i in self.inventory if i.currency_type is CurrencyType.GOLD and not i.sold),
            [i.name for i in self.inventory if i.sold],
        )

@dataclass(slots=True)
class CheckinResult(Result):
    streak: int = 0
    monthly_bonus: float = 0.0
    payments_bonus: float = 0.0
    skipped_day: bool = False
    earned: int = 0
    currency_type: CurrencyType = CurrencyType.UNKNOWN

@dataclass(slots=True)
class CasesResult(Result):
    available_cases: list[Case] = field(default_factory=list)
    opened_cases: int = 0
    ignored_cases: int = 0

@dataclass(slots=True)
class GiveawayResult(Result):
    giveaways: list[str] = field(default_factory=list)
    joined: list[str] = field(default_factory=list)
    won: list[str] = field(default_factory=list)

@dataclass(slots=True)
class RunResult(Result):
    # Initial Profile
    ip: Profile = field(default_factory=lambda: Profile(id=''))
    # Profile
    p: Profile = field(default_factory=lambda: Profile(id=''))

    checkin: CheckinResult | None = None
    giveaway: GiveawayResult | None = None
    cases: CasesResult | None = None

    @property
    def all_coins(self) -> int:
        return self.p.balance.coins + self.p.inventory_meta.all_coins

    @property
    def all_gold(self) -> int:
        return self.p.balance.gold + self.p.inventory_meta.all_gold

    @property
    def has_reached_target_gold(self) -> bool:
        if CONFIG.target_gold_amount > 0:
            gold = self.p.balance.gold if CONFIG.ignore_inventory else self.all_gold
            return gold >= CONFIG.target_gold_amount
        return False
