from unittest import mock

import pytest
from strategy_field.utils import fqn

from hope_smart_export.exporters import ExportAsText


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
        columns="username\nemail",
        exporter=fqn(ExportAsText),
        data={"field_separator": ";"},
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
def test_export(db, line, cfg, user):
    from django.contrib.auth.models import User

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        assert len(cfg.get_processor().columns) == 2
        data = cfg.export(User.objects.all())
        assert data.read() == f"""{user.username};{user.email};\n"""


@pytest.mark.parametrize(
    "line",
    [
        "name\ncodename\ncontent_type.app_label",
    ],
)
def test_export_fk(db, line, cfg):
    from django.contrib.auth.models import Permission

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        data = cfg.export(
            Permission.objects.filter(
                content_type__app_label="admin",
                codename="add_logentry",
            ),
        )
    assert data.readline() == "Can add log entry;add_logentry;admin;\n"


@pytest.mark.parametrize(
    "line",
    [
        "name\ncodename\ncontent_type.app_label|upper",
    ],
)
def test_export_filter(db, line, cfg, user):
    from django.contrib.auth.models import Permission

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        data = cfg.export(
            Permission.objects.filter(
                content_type__app_label="admin",
                codename="add_logentry",
            ),
        )
    assert data.readline() == "Can add log entry;add_logentry;ADMIN;\n"


@pytest.mark.parametrize(
    "line",
    [
        "name\n{% for p in record.permissions.all %}{{p.codename}}{%endfor%}",
    ],
)
def test_export_iter(db, line, cfg):
    from demo.factories import GroupFactory
    from django.contrib.auth.models import Group

    GroupFactory(name="Group #1", permissions=["admin.add_logentry"])

    with mock.patch.object(cfg, "columns", f"#comment\n{line}"):
        data = cfg.export(Group.objects.all())
    assert data.readline() == "Group #1;add_logentry;\n"


@pytest.mark.parametrize(
    "headers",
    [
        "1",
        "1\n2",
        "1\n2\n3",
    ],
)
def test_export_balance_headers(db, headers, cfg):
    with mock.patch.object(cfg, "headers", headers):
        assert len(cfg.get_processor().headers) == 2
