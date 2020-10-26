from django import template


register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    return str(text).startswith(str(starts))