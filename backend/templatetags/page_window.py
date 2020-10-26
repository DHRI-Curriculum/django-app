from django import template

register = template.Library()

@register.filter
def page_window(page, last, size=7):
    if page < size // 2 + 1:
        return range(1, min(size+1, last + 1)) # remember the range function won't
                                                # include the upper bound in the output
    else:
        return range(page - size // 2, min(last + 1, page + 1 + size // 2))
