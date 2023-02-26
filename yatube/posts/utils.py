from django.core.paginator import Paginator
from django.conf import settings


def get_paginator(request, post_list):
    page_number = request.GET.get('page')
    page_obj = Paginator(post_list,
                         settings.POSTS_PER_PAGE
                         ).get_page(page_number)
    return page_obj
