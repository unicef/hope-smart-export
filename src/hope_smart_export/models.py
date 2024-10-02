import io
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model, QuerySet
from django.template import Template, TemplateSyntaxError

from hope_smart_export.exporters import registry
from hope_smart_export.utils import chunked_iterator

if TYPE_CHECKING:
    from hope_smart_export.exporters import Exporter, Formats


class ExportConfig(models.Model):
    class Option(models.TextChoices):
        MEMORY = "M", "Memory Safe"
        TIME = "T", "Fastest"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    config = models.TextField(default="", blank=False)
    option = models.CharField(max_length=1, choices=Option.choices, default=Option.TIME)

    def parse_simple_config(self) -> list[Template]:
        columns = []
        for config_line in self.config.split("\n"):
            raw_line = config_line.strip()
            if raw_line.startswith("#"):
                continue
            elif raw_line.startswith("{{"):
                line = raw_line
            elif raw_line.startswith("{%"):
                line = raw_line
            elif raw_line:
                if "record." not in raw_line:
                    line = "{{record.%s}}" % raw_line
                else:
                    line = "{{%s}}}" % raw_line
            else:
                raise ValidationError(f"Unexpected format: {raw_line}")
            try:
                columns.append(Template(line))
            except TemplateSyntaxError:
                raise ValidationError(f"Invalid synthax: {line}")
        return columns

    def clean(self):
        self.parse_simple_config()

    def export(self, fmt: "Formats", queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        exporter: type[Exporter] = registry[fmt]
        if self.option == ExportConfig.Option.MEMORY:
            data = exporter(self).export(chunked_iterator(queryset))
        else:
            data = exporter(self).export(queryset.iterator())
        return data
