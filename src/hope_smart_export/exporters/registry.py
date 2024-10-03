from strategy_field.registry import Registry

from .base import Exporter
from .csv import ExportAsCSV
from .txt import ExportAsText

registry = Registry(Exporter)
registry.register(ExportAsText)
registry.register(ExportAsCSV)
