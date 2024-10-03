import io

from django import forms
from django.db.models import Model, QuerySet
from django.utils.encoding import force_str

from .base import Exporter, ExporterConfig


class XlsExporterConfig(ExporterConfig):
    defaults = {"sheet_name": "Sheet #1"}
    sheet_name = forms.CharField(max_length=100, required=False)


class ExportAsXls(Exporter):
    config_class = XlsExporterConfig

    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        import xlsxwriter

        config = self.config.get_config()
        out = io.BytesIO()
        book = xlsxwriter.Workbook(out, {"in_memory": True})
        sheet_name = config.pop("sheet_name")
        sheet = book.add_worksheet(sheet_name)
        # TODO: this should be imporved to get fk/nested field types
        formats = {"_general_": book.add_format()}

        row = 0
        sheet.write(row, 0, force_str("#"), formats["_general_"])
        processor = self.config.get_processor()
        headers = processor.headers
        if headers:
            for col, fieldname in enumerate(headers, start=1):
                sheet.write(row, col, force_str(fieldname), formats["_general_"])

        # settingstime_zone = get_default_timezone()
        for rownum, row in enumerate(queryset):
            sheet.write(rownum + 1, 0, rownum + 1)
            values = processor.get_row_values(row)
            for idx, value in enumerate(values):
                fmt = formats.get(idx, formats["_general_"])
                sheet.write(rownum + 1, idx + 1, values[idx], fmt)

        book.close()
        out.seek(0)
        return out
