from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import get_template

from insight.models import Insight
from workshop.models import Workshop
from learner.models import Progress
from install.models import Instruction


register = template.Library()

def get_workshops_with_progress(profile):
    _ = list()
    for p in Progress.objects.filter(profile_id=300):
        _.append(p.workshop)
    return _

def get_all_objects(context):
    d = {
        'insights': Insight.objects.all().order_by('title'),
        'workshops': {
            'all': Workshop.objects.all().order_by('name'),
            'with_progress': [],
        },
        'installations': Instruction.objects.by_software()
    }
    if context.get('user'):
        d['workshops']['with_progress'] = get_workshops_with_progress(context.get('user').profile)
    return d

@register.simple_tag(takes_context=True)
def main_navigation(context):
    obj = get_all_objects(context)

    html = get_template('website/menu-elements/main-menu.html').render({'request': context.request, 'is_home': context.request.get_full_path() == '/'}) # Warning: is_home is also defined in a context processor

    #### Start mini menus
    html += '<div id="mini-menus" class="container-fluid m-0 p-0">'

    # Workshops mini menu
    html += get_template('website/menu-elements/workshops-mini-menu.html').render({'with_progress': obj['workshops']['with_progress'], 'all': obj['workshops']['all']})

    # Installations mini menu
    html += get_template('website/menu-elements/installations-mini-menu.html').render({'all': obj['installations']})

    # Insights mini menu
    html += get_template('website/menu-elements/insights-mini-menu.html').render({'all': obj['insights']})

    #### End mini menus
    html += '</div></div>'

    return mark_safe(html)