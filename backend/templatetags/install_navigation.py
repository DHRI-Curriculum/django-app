from django import template
from django.urls import reverse
from glossary.models import Term
from django.utils.safestring import mark_safe
from install.models import Instructions, OperatingSystem, Software
from django.template.loader import get_template


register = template.Library()


@register.simple_tag(takes_context=True)
def install_navigation(context):
    # Opening
    html = '<nav class="nav">'

    html += f'<a class="nav-link text-primary" href="{reverse("install:index")}"><strong>Installations</strong></a>'

    # By software
    html += '<a class="nav-link dropdown-toggle text-white" href="#" id="installBySoftware" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Software</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installBySoftware">'
    for software in Software.objects.all():
        html += get_template('install/fragments/menu/software.html').render({'software': software})
    html += '</div>'

    # By software
    html += '<a class="nav-link dropdown-toggle text-white" href="#" id="installByOperatingSystem" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Operating System</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installByOperatingSystem">'
    for os in OperatingSystem.objects.all():
        html += get_template('install/fragments/menu/os.html').render({'os': os})
    html += '</div>'

    # The end
    html += '</nav>'

    html = '<div class="navbar p-0 ml-2 my-1 d-flex flex-column align-items-start">'
    html += f'<a class="mr-0 mr-sm-3 text-white btn btn-sm" href="{reverse("install:index")}"><strong>Installations</strong></a>'

    html += '<div style="position: relative !important;"><a class="mr-0 mr-sm-3 text-white btn btn-sm dropdown-toggle" href="#" id="installBySoftware" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Software</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installBySoftware"><ul class="navbar-nav mr-auto">'
    for software in Software.objects.all():
        html += get_template('install/fragments/menu/software.html').render({'software': software})
    html += '</ul></div></div>'

    # By OS
    html += '<div style="position: relative !important;"><a class="mr-0 mr-sm-3 text-white btn btn-sm dropdown-toggle" href="#" id="installByOS" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">By Operating System</a>'
    html += '<div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="installByOS"><ul class="navbar-nav mr-auto">'
    for os in OperatingSystem.objects.all():
        html += get_template('install/fragments/menu/os.html').render({'os': os})
    html += '</ul></div></div>'

    html += '</div>'

    return mark_safe(html)