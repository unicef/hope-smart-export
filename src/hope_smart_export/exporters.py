import abc
import io
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from django.db.models import Model, QuerySet
from django.template import Context

if TYPE_CHECKING:
    from .models import ExportConfig

Registry = TypedDict("Registry", {"txt": "type[ExportAsText]"})
# TODO: this should be taken by Registry.keys()
Formats = Literal["txt"]


class Exporter(abc.ABC):

    def __init__(self, cfg: "ExportConfig"):
        self.config = cfg
        super().__init__()

    @abc.abstractmethod
    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO | str | bytes:
        pass

    def inspect(self, queryset: QuerySet[Model]) -> Any:
        pass


class ExportAsText(Exporter):
    def export(self, queryset: QuerySet[Model]) -> io.BytesIO | io.StringIO:
        output = io.StringIO()
        columns = self.config.parse_simple_config()
        for record in queryset:
            for column in columns:
                col_value = column.render(Context({"record": record}))
                output.write(f"{col_value};")
            output.write("\n")
        output.seek(0)
        return output


registry: Registry = {"txt": ExportAsText}
