import pytest


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
def test_export(db, line):
    from demo.factories import UserFactory
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    user = UserFactory()
    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(User), config=f"#comment\n{line}"
    )
    cfg.save()
    assert len(cfg.parse_simple_config()) == 2
    data = cfg.export("txt", User.objects.all())
    assert data.read() == f"""{user.username};{user.email};\n"""


@pytest.mark.parametrize(
    "line",
    [
        "name\ncodename\ncontent_type.app_label",
    ],
)
def test_export_fk(db, line):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(Permission),
        config=f"#comment\n{line}",
    )
    cfg.save()
    data = cfg.export(
        "txt",
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
def test_export_filter(db, line):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(Permission),
        config=f"#comment\n{line}",
    )
    cfg.save()
    data = cfg.export(
        "txt",
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
def test_export_iter(db, line):
    from demo.factories import GroupFactory
    from django.contrib.auth.models import Group
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    GroupFactory(name="Group #1", permissions=["admin.add_logentry"])
    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(Group),
        config=f"#comment\n{line}",
    )
    cfg.save()
    data = cfg.export("txt", Group.objects.all())
    assert data.readline() == "Group #1;add_logentry;\n"
