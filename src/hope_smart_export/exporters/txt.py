import io
from typing import TYPE_CHECKING

from django import forms
from django.db.models import Model, QuerySet

from .base import Exporter, ExporterConfig

if TYPE_CHECKING:
    from ..models import Processor


class TxtExporterConfig(ExporterConfig):
    field_separator = forms.CharField(max_length=1)


class ExportAsText(Exporter):
    config_class = TxtExporterConfig

    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        output = io.StringIO()
        processor: "Processor" = self.config.get_processor()
        # columns = self.config.parse_simple_config()
        for record in queryset:
            values = processor.get_row_values(record)
            output.write(self.config.data["field_separator"].join(values) + self.config.data["field_separator"])
            # for column in columns:
            #     col_value = column.render(Context({"record": record}))
            # output.write(f"{col_value}{self.config.data['field_separator']}")
            output.write("\n")
        output.seek(0)
        return output
