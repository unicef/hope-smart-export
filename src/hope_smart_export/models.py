import io
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connections, models
from django.db.models import Model, QuerySet
from django.template import Context, Template, TemplateSyntaxError
from django.test.utils import CaptureQueriesContext
from django.utils.functional import cached_property
from strategy_field.fields import StrategyField

from hope_smart_export.exporters.registry import registry
from hope_smart_export.utils import chunked_iterator

if TYPE_CHECKING:
    from hope_smart_export.exporters import Exporter


class Processor:
    def __init__(self, cfg: "Configuration"):
        self.cfg = cfg
        self._columns: Optional[list[Template]] = None

    @cached_property
    def headers(self) -> list[str]:
        if self.cfg.headers:
            defined_headers = str(self.cfg.headers).split("\n")
            headers_len = len(defined_headers)
            columns_len = len(self.columns)
            for i in range(headers_len, columns_len):
                defined_headers.append("-")
            return defined_headers[:columns_len]
        return []

    @cached_property
    def columns(self) -> list[Template]:
        self._columns = []
        for config_line in self.cfg.columns.split("\n"):
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
                raise ValidationError(f"Unexpected format: '{raw_line}'")
            try:
                tpl = Template(line)
                tpl.render(Context({}))
                self._columns.append(tpl)
            except TemplateSyntaxError:
                raise ValidationError(f"Invalid synthax: {line}")
        return self._columns

    def get_row_values(self, record: "Any"):
        return [column.render(Context({"record": record})) for column in self.columns]


class ConfigurationQuerySet(models.QuerySet["AnyModel"]):
    pass


class ConfigurationManager(models.Manager["AnyModel"]):
    _queryset_class = ConfigurationQuerySet


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Configuration(models.Model):
    class Option(models.TextChoices):
        MEMORY = "M", "Memory Safe"
        TIME = "T", "Fastest"

    name = models.CharField(max_length=255, unique=True)
    code = models.SlugField(max_length=255, unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    columns = models.TextField(default="", blank=False)
    exporter: "Exporter" = StrategyField(registry=registry)
    headers = models.TextField(default="", blank=True, null=False)
    data = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=False, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    option = models.CharField(max_length=1, choices=Option.choices, default=Option.TIME)
    max_queries = models.IntegerField(
        default=0, blank=True, null=True, help_text="Max queries expected for this template. Log warning otherwise."
    )

    objects = ConfigurationManager

    def __str__(self) -> str:
        return str(self.name)

    def get_config(self) -> dict[str, Any]:
        return {**self.exporter.config_class.defaults, **self.data}

    def clean(self) -> None:
        self.get_processor().columns  # noqa

    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        # exporter: type[Exporter] = registry[fmt]
        if self.option == Configuration.Option.MEMORY:
            data = self.exporter.export(chunked_iterator(queryset))
        else:
            data = self.exporter.export(queryset.iterator())
        return data

    def inspect(self, queryset: QuerySet[Model], max_lines=10) -> CaptureQueriesContext:
        columns = self.get_processor().columns
        with CaptureQueriesContext(connections[queryset.db]) as ctx:
            for i, record in enumerate(queryset):
                for column in columns:
                    column.render(Context({"record": record}))
                if i >= max_lines:
                    break
        return ctx

    def get_processor(self) -> Processor:
        return Processor(self)
