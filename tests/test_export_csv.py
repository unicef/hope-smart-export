import csv
from unittest import mock

import pytest
from strategy_field.utils import fqn

from typing import TYPE_CHECKING

from hope_smart_export.exporters.csv import ExportAsCSV

if TYPE_CHECKING:
    from hope_smart_export.models import Configuration
    from django.contrib.auth.models import User


@pytest.fixture()
def user():
    from demo.factories import UserFactory

    return UserFactory()


@pytest.fixture()
def cfg():
    from demo.factories import ConfigurationFactory
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    return ConfigurationFactory(
        content_type=ContentType.objects.get_for_model(User),
        columns="id\n",
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
        "{{record.username}}\n{{record.email}}",
    ],
)
def test_export(db, line, cfg: "Configuration", dialect: str, user: "User"):
    from django.contrib.auth.models import User

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        cfg.data["dialect"] = dialect
        assert len(cfg.get_processor().columns) == 2
        data = cfg.export(User.objects.all())
        assert data.read() == f'''{user.username},{user.email}\r\n'''
