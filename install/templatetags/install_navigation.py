from django import template
from django.urls import reverse
from glossary.models import Term
from django.utils.safestring import mark_safe
from install.models import Instruction

register = template.Library()


def get_installation_menu_items():
    all_instructions = Instruction.objects.all().order_by(
        'software__software', 'software__operating_system'
    )
    per_software, per_os = dict(), dict()
    for x in all_instructions:
        if not x.software.software in per_software: per_software[x.software.software] = list()
        per_software[x.software.software].append(x)

        if not x.software.operating_system in per_os: per_os[x.software.operating_system] = list()
        per_os[x.software.operating_system].append(x)
    return {'per_software': per_software, 'per_os': per_os}

@register.simple_tag(takes_context=True)
def install_navigation(context):
    menu_items = get_installation_menu_items()

    # Opening
    html = '<nav class="nav nav-underline">'
    html += '<a class="nav-link text-black" href="/install/"><strong>Installations</strong></a>' # TODO: replace with reverse

    # By software
    html += '<a class="nav-link dropdown-toggle" href="#" id="dropdownA" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Software</a> \
                <div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="dropdown">'
    for software, instructions in menu_items['per_software'].items():
        html += f'''<div class="dropdown-submenu">
                        <a class="dropdown-item dropdown-toggle" data-toggle="dropdown" href="#">{software}</a>
                            <div class="dropdown-menu dropdown-menu-special shadow-sm">'''
        for instruction in instructions:
            html += f'''<a class="dropdown-item" href="{ reverse('install:installation', kwargs={'slug':instruction.slug}) }">{instruction.software.operating_system}</a>'''

        html += '</div></div>'

    html += '</div>'

    # By OS
    html += '<a class="nav-link dropdown-toggle" href="#" id="dropdownA" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Operating System</a> \
                <div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="dropdown">'
    for os, instructions in menu_items['per_os'].items():
        html += f'''<div class="dropdown-submenu">
                        <a class="dropdown-item dropdown-toggle" data-toggle="dropdown" href="#">{os}</a>
                            <div class="dropdown-menu dropdown-menu-special shadow-sm">'''
        for instruction in instructions:
            html += f'''<a class="dropdown-item" href="{ reverse('install:installation', kwargs={'slug':instruction.slug})  }">{instruction.software.software}</a>'''

        html += '</div></div>'

    html += '</div>'

    # The end
    html += '</nav>'
    return mark_safe(html)