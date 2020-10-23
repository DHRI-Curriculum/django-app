from django import template
from django.urls import reverse
from glossary.models import Term
from django.utils.safestring import mark_safe
from install.models import Instruction
from django.template.loader import get_template


register = template.Library()


@register.simple_tag(takes_context=True)
def install_navigation(context):
    # Opening
    html = '<nav class="nav">'

    html += '<a class="nav-link text-primary" href="/install/"><strong>Installations</strong></a>' # TODO: replace with reverse

    # By software
    html += '<a class="nav-link dropdown-toggle text-white" href="#" id="installBySoftware" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Software</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installBySoftware">'
    for software, items in Instruction.objects.by_software().items():
        html += get_template('install/menu-elements/software.html').render({'software': software, 'instructions': list(items.values())})
    html += '</div>'

    # By software
    html += '<a class="nav-link dropdown-toggle text-white" href="#" id="installByOperatingSystem" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Operating System</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installByOperatingSystem">'
    for os, items in Instruction.objects.by_os().items():
        html += get_template('install/menu-elements/os.html').render({'os': os, 'instructions': list(items.values())})
    html += '</div>'

    # The end
    html += '</nav>'
    return mark_safe(html)