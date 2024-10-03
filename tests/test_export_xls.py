from typing import TYPE_CHECKING
from unittest import mock

import openpyxl
import pytest
from strategy_field.utils import fqn

from hope_smart_export.exporters.xls import ExportAsXls

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from openpyxl.workbook.workbook import Workbook
    from openpyxl.worksheet.worksheet import Worksheet

    from hope_smart_export.models import Configuration


@pytest.fixture()
def user():
    from demo.factories import UserFactory

    return UserFactory()


@pytest.fixture()
def cfg(db):
    from demo.factories import ConfigurationFactory
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    return ConfigurationFactory(
        content_type=ContentType.objects.get_for_model(User),
        columns="username\nemail",
        exporter=fqn(ExportAsXls),
        option="T",
        data={"sheet_name": "TestSheet #1"},
    )


@pytest.mark.parametrize(
    "line",
    [
        "username\nemail",
        "{{record.username}}\nemail",
        "{{record.username}}\n{{record.email}}",
        "{{record.username}}  \n   {{record.email}}   ",
        "{{record.username}}\n{{record.email}}",
    ],
)
def test_export(db, line, cfg: "Configuration", user: "User"):
    from django.contrib.auth.models import User

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        assert len(cfg.get_processor().columns) == 2
        data = cfg.export(User.objects.all())
        wb = openpyxl.load_workbook(data)
        assert wb


def test_export_headers(cfg: "Configuration", user: "User"):
    from django.contrib.auth.models import User

    with mock.patch.object(cfg, "headers", "username\nemail"):
        data = cfg.export(User.objects.all())
        wb: "Workbook" = openpyxl.load_workbook(data)
        sh: "Worksheet" = wb.worksheets[0]
        assert sh.title == "TestSheet #1"
        assert [c.value for c in list(sh.rows)[0]] == ["#", "username", "email"]
