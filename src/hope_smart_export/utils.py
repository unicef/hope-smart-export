from django.core.paginator import Paginator

DEFAULT_BATCH_SIZE = 100000


def chunked_iterator(queryset, chunk_size=DEFAULT_BATCH_SIZE):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        for obj in paginator.page(page).object_list:
            yield obj
