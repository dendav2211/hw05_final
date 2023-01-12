from django.core.paginator import Paginator
from django.conf import settings


def paginator_utils(request, post_list):
    paginator = Paginator(post_list, settings.POST_COUNT)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
