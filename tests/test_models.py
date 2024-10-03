from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from hope_smart_export.exporters.txt import ExportAsText


@pytest.fixture()
def cfg(db):
    from demo.factories import ConfigurationFactory
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    return ConfigurationFactory(
        content_type=ContentType.objects.get_for_model(User),
        columns="id",
        exporter=fqn(ExportAsText),
        data={"field_separator": ";"},
    )


@pytest.mark.parametrize(
    "line,expected",
    [
        ("username\nemail", True),
        ("{{record.username}}  \nemail ", True),
        ("{{record.username}}\n{{record.email}}", True),
        ("{record.username}}\n{{record.email}}", False),
        ("{{record.username}}\n\n\n{{record.email}}", False),
        ("{$ecord.username}}\n{{record.email}}", False),
        ("{% for %}\n{{record.email}}", False),
        ("123", True),
    ],
)
def test_validate(db, cfg, line, expected):
    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        if expected:
            cfg.clean()
        else:
            with pytest.raises(ValidationError):
                cfg.clean()


@pytest.mark.parametrize("opt", ["T", "M"])
def test_process_qs(db, opt, cfg):
    from demo.factories import UserFactory
    from django.contrib.auth.models import User

    with mock.patch.object(cfg, "columns", "username\npassword"):
        with mock.patch.object(cfg, "option", opt):
            with mock.patch("hope_smart_export.utils.DEFAULT_BATCH_SIZE", 10):
                UserFactory.create_batch(20)
                data = cfg.export(User.objects.all())
                assert data


def test_inspect_qs(cfg):
    from django.contrib.auth.models import Permission

    with mock.patch.object(cfg, "columns", "name"):
        qs = Permission.objects.all()[:10]
        data = cfg.inspect(qs, 5)
        assert len(data.captured_queries) == 1

    with mock.patch.object(cfg, "columns", "content_type.model"):
        data = cfg.inspect(qs)
        assert len(data.captured_queries) == 10
