import csv
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from strategy_field.utils import fqn

from hope_smart_export.exporters.csv import ExportAsCSV

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from hope_smart_export.models import Configuration


@pytest.fixture
def user():
    from demo.factories import UserFactory  # noqa

    return UserFactory()


@pytest.fixture
def cfg(db):
    from demo.factories import ConfigurationFactory  # noqa
    from django.contrib.auth.models import User  # noqa
    from django.contrib.contenttypes.models import ContentType  # noqa

    return ConfigurationFactory(
        content_type=ContentType.objects.get_for_model(User),
        columns="username\nemail",
        exporter=fqn(ExportAsCSV),
        data={"delimiter": ",", "quotechar": "'", "quoting": csv.QUOTE_NONE, "escapechar": ""},
    )


@pytest.mark.parametrize("dialect", [None, "excel"])
@pytest.mark.parametrize(
    "line",
    [
        "username\nemail",
        "{{record.username}}\nemail",
        "{{record.username}}\n{{record.email}}",
        "{{record.username}}  \n   {{record.email}}   ",
    ],
)
def test_export(db, line, cfg: "Configuration", dialect: str, user: "User"):
    from django.contrib.auth.models import User  # noqa

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        cfg.data["dialect"] = dialect
        assert len(cfg.get_processor().columns) == 2
        data = cfg.export(User.objects.all())
        assert data.read() == f"""{user.username},{user.email}\r\n"""


def test_export_headers(cfg: "Configuration", user: "User"):
    from django.contrib.auth.models import User  # noqa

    with mock.patch.object(cfg, "headers", "username\nemail"):
        assert len(cfg.get_processor().columns) == 2
        data = cfg.export(User.objects.all())
        assert data.read() == f"""username,email\r\n{user.username},{user.email}\r\n"""
