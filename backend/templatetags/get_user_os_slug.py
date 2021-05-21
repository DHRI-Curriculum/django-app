from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_os_slug(context):
    if 'mac' in context.request.META.get('HTTP_USER_AGENT', '').lower():
        return 'macos'
    elif 'windows' in context.request.META.get('HTTP_USER_AGENT', '').lower():
        return 'windows'
    
    return 'NONE'