from unittest import mock

import pytest
from django.core.exceptions import ValidationError


def test_create_base(db):
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(User),
        config="username\npassword",
    )
    cfg.save()
    assert cfg.pk


@pytest.mark.parametrize(
    "line,expected",
    [
        ("username\nemail", True),
        ("{{record.username}}  \nemail ", True),
        ("{{record.username}}\n{{record.email}}", True),
        ("{record.username}}\n{{record.email}}", False),
        ("{{record.username}}\n\n\n{{record.email}}", False),
        ("123", True),
        ("\n\n\n", False),
    ],
)
def test_validate(db, line, expected):
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    cfg = ExportConfig(
        content_type=ContentType.objects.get_for_model(User), config=f"#comment\n{line}"
    )
    if expected:
        cfg.clean()
    else:
        with pytest.raises(ValidationError):
            cfg.clean()


@pytest.mark.parametrize("opt", ["T", "M"])
def test_process_qs(db, opt):
    from demo.factories import UserFactory
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    from hope_smart_export.models import ExportConfig

    with mock.patch("hope_smart_export.utils.DEFAULT_BATCH_SIZE", 10):
        UserFactory.create_batch(20)
        cfg = ExportConfig(
            content_type=ContentType.objects.get_for_model(User),
            config="username\npassword",
            option=opt,
        )
        cfg.save()
        data = cfg.export("txt", User.objects.all())
        assert data
