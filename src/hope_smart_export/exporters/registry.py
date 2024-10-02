from strategy_field.registry import Registry

from .base import Exporter
from .txt import ExportAsText
from .csv import ExportAsCSV

registry = Registry(Exporter)
registry.register(ExportAsText)
registry.register(ExportAsCSV)
