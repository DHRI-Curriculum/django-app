from django import template
from django.template import Template
from django.utils.safestring import mark_safe
from website.models import Snippet

register = template.Library()


@register.simple_tag(takes_context=True)
def snippet(context, identifier):
    num_snippets = Snippet.objects.filter(identifier=identifier).count()
    if not num_snippets:
        return mark_safe(f'<!-- Error: Snippet "{identifier}" not found --><script>console.error("snippet `{identifier}` not found — see source code for information");</script>')
    elif num_snippets == 1:
        template_str = Snippet.objects.get(identifier=identifier).snippet
        return mark_safe(Template(template_str).render(context))
    else:
        return mark_safe(f'<!-- Error: Too many snippets with identifier "{identifier}" found --><script>console.error("too many snippets with identifier `{identifier}` found — see source code for information");</script>')
