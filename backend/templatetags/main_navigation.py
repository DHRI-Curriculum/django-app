from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import get_template

from insight.models import Insight
from workshop.models import Workshop
from learner.models import Progress
from install.models import Software


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
        'software': Software.objects.all()
    }
    if context.request.user.is_authenticated:
        d['workshops']['with_progress'] = get_workshops_with_progress(
            context.get('user').profile)
    return d


def get_standard_os_slug(request):
    if 'mac' in request.META.get('HTTP_USER_AGENT', '').lower():
        return 'macos'
    elif 'windows' in request.META.get('HTTP_USER_AGENT', '').lower():
        return 'windows'
    
    return ''


@register.simple_tag(takes_context=True)
def main_navigation(context):
    obj = get_all_objects(context)

    # Warning: is_home is also defined in a context processor
    html = get_template('_main-navbar/main-menu.html').render(
        {'request': context.request, 'is_home': context.request.get_full_path() == '/'})

    # Start mini menus
    html += '<nav id="mini-menus" class="bg-primary"><div class="container-xxl">'

    # Workshops mini menu
    html += get_template('_main-navbar/workshops-mini-menu.html').render(
        {'with_progress': obj['workshops']['with_progress'], 'all': obj['workshops']['all']})

    # Installations mini menu
    html += get_template('_main-navbar/installations-mini-menu.html').render(
        {
            'software': obj['software'],
            'request': context.request,
            'standard_os_slug': get_standard_os_slug(context.request)
        })

    # Insights mini menu
    html += get_template('_main-navbar/insights-mini-menu.html').render(
        {'all': obj['insights']})

    # End mini menus
    html += '</div></nav>'

    return mark_safe(html)
