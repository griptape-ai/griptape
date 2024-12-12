from pathlib import Path

from griptape.configs import Defaults
from griptape.configs.drivers import DriversConfig
from griptape.structures import Agent

config_file = "config.json"

# Save config
config_text = Defaults.drivers_config.to_json()
Path(config_file).write_text(config_text)

# Load config
config_text = Path(config_file).read_text()
Defaults.drivers_config = DriversConfig.from_json(config_text)


agent = Agent()
