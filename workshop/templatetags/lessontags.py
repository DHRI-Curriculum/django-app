from django import template

register = template.Library()


# Moved this to markdownify.py because it wouldn't register correctly otherwise.