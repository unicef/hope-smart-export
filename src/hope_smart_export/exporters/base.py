import abc
import io
from typing import TYPE_CHECKING, Any

from django import forms
from django.db.models import Model, QuerySet

if TYPE_CHECKING:
    from ..models import Configuration


class ExporterConfig(forms.Form):
    defaults: dict[str, Any] = {}


class Exporter(abc.ABC):
    config_class = ExporterConfig

    def __init__(self, cfg: "Configuration"):
        self.config = cfg
        super().__init__()

    @classmethod
    def name(cls):
        return cls.__name__

    @abc.abstractmethod
    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO | str | bytes:
        pass
