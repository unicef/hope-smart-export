import io
from typing import TYPE_CHECKING

from django import forms
from django.db.models import Model, QuerySet
from django.template import Context
from django.utils.encoding import force_str
from django.utils.timezone import get_default_timezone

from .base import Exporter, ExporterConfig

if TYPE_CHECKING:
    from ..models import Processor


class XlsExporterConfig(ExporterConfig):
    defaults = {
        "date_format": "d/m/Y",
        "datetime_format": "N j, Y, P",
        "time_format": "P",
        "sheet_name": "Sheet1",
        "DateField": "DD MMM-YY",
        "DateTimeField": "DD MMD YY hh:mm",
        "TimeField": "hh:mm",
        "IntegerField": "#,##",
        "PositiveIntegerField": "#,##",
        "PositiveSmallIntegerField": "#,##",
        "BigIntegerField": "#,##",
        "DecimalField": "#,##0.00",
        "BooleanField": "boolean",
        "NullBooleanField": "boolean",
        # 'EmailField': lambda value: 'HYPERLINK("mailto:%s","%s")' % (value, value),
        # 'URLField': lambda value: 'HYPERLINK("%s","%s")' % (value, value),
        "CurrencyColumn": '"$"#,##0.00);[Red]("$"#,##0.00)',
    }


#


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
