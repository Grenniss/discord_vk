from pathlib import Path

__title__ = "bot"
__author__ = "TrixiS"
__licence__ = "MIT"
__copyright__ = "Copyright 2021 TrixiS"
__version__ = "0.0.1"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

root_path = Path(__file__).parent.parent

from . import *
