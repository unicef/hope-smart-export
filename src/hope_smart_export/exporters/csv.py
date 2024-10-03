import csv
import io
from typing import TYPE_CHECKING

from django import forms
from django.db.models import Model, QuerySet
from django.utils.translation import gettext as _

from .base import Exporter, ExporterConfig

if TYPE_CHECKING:
    from ..models import Processor

delimiters = ",;|:"
quotes = "'\"`"
escapechars = " \\"


class TxtExporterConfig(ExporterConfig):
    defaults = {"delimiter": ",", "quotechar": "'", "quoting": csv.QUOTE_ALL, "escapechar": ""}
    delimiter = forms.ChoiceField(label=_("Delimiter"), choices=list(zip(delimiters, delimiters)), initial=",")
    quotechar = forms.ChoiceField(label=_("Quotechar"), choices=list(zip(quotes, quotes)), initial="'")
    quoting = forms.TypedChoiceField(
        coerce=int,
        label=_("Quoting"),
        choices=(
            (csv.QUOTE_ALL, _("All")),
            (csv.QUOTE_MINIMAL, _("Minimal")),
            (csv.QUOTE_NONE, _("None")),
            (csv.QUOTE_NONNUMERIC, _("Non Numeric")),
        ),
        initial=csv.QUOTE_ALL,
    )

    escapechar = forms.ChoiceField(label=_("Escapechar"), choices=(("", ""), ("\\", "\\")), required=False)


class ExportAsCSV(Exporter):
    config_class = TxtExporterConfig

    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        config = self.config.get_config()
        dialect = config.get("dialect", None)
        buffer = io.StringIO()

        if dialect is not None:
            writer = csv.writer(buffer, dialect=dialect)
        else:
            writer = csv.writer(
                buffer,
                escapechar=config["escapechar"] or None,
                delimiter=str(config["delimiter"]),
                quotechar=str(config["quotechar"]),
                quoting=int(config["quoting"]),
            )
        processor: "Processor" = self.config.get_processor()
        headers = processor.headers
        if headers:
            writer.writerow(headers)
        for record in queryset:
            values = processor.get_row_values(record)
            writer.writerow(values)
        buffer.seek(0)
        return buffer
