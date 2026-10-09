import os
import tomllib
import argparse

class Config:
    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize the Config object, optionally with a config path.
        """
        args = self.parse_args()
        raw = self.load_toml(args.config_path or config_path)

        flags = raw.get("flags", {})
        self.headless = args.headless or flags.get("headless", False)
        self.debug = args.debug or flags.get("debug", False)
        self.checkin = args.checkin or flags.get("checkin", False)
        self.giveaway = args.giveaway or flags.get("giveaway", False)
        self.cases = args.cases or flags.get("cases", False)
        self.sell_inventory = args.sell_inventory or flags.get("sell_inventory", False)

        general = raw.get("general", {})
        self.wait_timeout = general.get("wait_timeout", 2)
        self.wait_after = args.wait_after if args.wait_after is not None else general.get("wait_after", 0)
        self.giveaway_price_threshold = general.get("giveaway_price_threshold", 0)
        self.case_price_threshold = general.get("case_price_threshold", 0)
        self.referral_url = args.referral_url or general.get("referral_url", "")

        targets = raw.get("targets", {})
        self.target_gold_amount = targets.get("target_gold_amount", 0)
        self.ignore_inventory = targets.get("ignore_inventory", False)
        self.target_case = targets.get("target_case", "")

        selling = raw.get("selling", {})
        self.sell_gold = selling.get("sell_gold", False)
        self.sell_ignored = selling.get("sell_ignored", False)
        self.sell_gold_price_threshold = selling.get("sell_gold_price_threshold", 0)

        discord = raw.get("discord", {})
        self.webhook_url = args.webhook_url or discord.get("webhook_url", "")
        self.webhook_name = discord.get("profile_name", "")
        self.webhook_avatar = discord.get("profile_avatar", "")

        telegram = raw.get("telegram", {})
        self.telegram_token = telegram.get("bot_token", "")
        self.telegram_chat_id = telegram.get("chat_id", "")

        db = raw.get("db", {})
        self.db_enabled = db.get("enabled", False)
        self.db_host = db.get("host", "")
        self.db_port = db.get("port", 0)
        self.db_name = db.get("name", "")
        self.db_username = db.get("username", "")
        self.db_password = db.get("password", "")

        paths = raw.get("paths", {})
        self.chromium_path = args.chromium_path or os.path.abspath(paths.get("chromium_path", ""))
        self.chromedriver_path = args.chromedriver_path or os.path.abspath(paths.get("chromedriver_path", ""))
        self.accounts_dir = paths.get("accounts_file", "accounts")
        self.new_account = args.new_account if args.new_account else None
        self.accounts = self.load_accounts()

        self.validate()

    def parse_args(self) -> argparse.Namespace:
        """Parse config options for AutoDailies. """
        parser = argparse.ArgumentParser(description="AutoDailies")

        # Flags
        parser.add_argument("-H", "--headless", action="store_true", help="Starts the browser in headless mode.")
        parser.add_argument("-d", "--debug", action="store_true", help="Enables debug.")
        parser.add_argument("-c", "--checkin", action="store_true", help="Runs the daily check-in.")
        parser.add_argument("-g", "--giveaway", action="store_true", help="Runs the giveaway.")
        parser.add_argument("-cs", "--cases", action="store_true", help="Opens the cases.")
        parser.add_argument("-si", "--sell_inventory", action="store_true", help="Sell items from inventory.")

        # General
        parser.add_argument("-w", "--wait-after", type=int, help="Number of seconds to wait before closing the browser.")

        # Discord
        parser.add_argument("--webhook_url", type=str, help="Discord webhook URL to send logs to.")

        # Paths
        parser.add_argument("--chromium_path", type=str, help="Path to the browser binary.")
        parser.add_argument("--chromedriver_path", type=str, help="Path to the Chromedriver.")
        parser.add_argument("--config_path", type=str, help="Path to the config file.")

        # For new pkl files
        parser.add_argument("--new_account", type=str, help="Phone number (with country code, only numbers) \
            of the new telegram account to be added.")
        parser.add_argument("--referral_url", type=str, help="Referral URL link that you can use for new accounts.")

        return parser.parse_args()

    def load_toml(self, user_config: str) -> dict:
        # Check if config file exists
        if not os.path.exists(user_config):
            raise FileNotFoundError(f"Config file not found: {user_config}. Please create a config file (you can find an example in the repo).")

        # Read config file
        with open(os.path.abspath(user_config), "rb") as f:
            return tomllib.load(f)

    def load_accounts(self) -> dict[str, str]:
        # Check if account directory exists
        if not os.path.exists(self.accounts_dir):
            raise FileNotFoundError(f"Specified account directory not found: {os.path.abspath(self.accounts_dir)}")

        # Get accounts pkl file paths
        acs =  {
            name: f"{self.accounts_dir}/{name}"
            for name in os.listdir("accounts")
            if name.endswith(".pkl")
        }

        # Handle new account
        if self.new_account:
            if self.new_account not in acs.keys():
                return {self.new_account: f"{self.accounts_dir}/{self.new_account}.pkl"}
            else:
                raise FileExistsError(f"Account already exists: {self.new_account}.pkl")

        return acs

    def validate(self):
        self._validate_paths()
        self._validate_values()

    def _validate_paths(self):
        # Check if paths exist
        for path in [self.chromium_path, self.chromedriver_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path not found: {path}")

    def _validate_values(self):
        # Check for negative values
        for value in [self.giveaway_price_threshold, self.case_price_threshold, self.wait_after, self.wait_timeout]:
            if value < 0:
                raise ValueError(f"{value} cannot be negative.")

        # Check for valid URLs
        if self.webhook_url and not self.webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValueError(f"Invalid webhook URL: {self.webhook_url}")

        # Check if accounts are not empty
        if not self.accounts or len(self.accounts) == 0:
            raise ValueError(f"No accounts are specified. Please ensure there are .pkl files in the accounts directory ({os.path.abspath(self.accounts_dir)}).")

        # Check if phone number is valid
        if self.new_account:
            if not self.new_account.isdigit() or not 7 < len(self.new_account) < 17:
                raise ValueError(f"Invalid phone number: {self.new_account}")

        # Check if referal link is valid
        if self.referral_url and not self.referral_url.startswith("https://genshindrop.io/ref/"):
            raise ValueError(f"Invalid referral URL link: {self.referral_url}")

CONFIG: Config = Config()
