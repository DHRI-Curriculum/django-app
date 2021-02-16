from django import template
from django.urls import reverse
from glossary.models import Term
from django.utils.safestring import mark_safe
from .glossary_navigation import get_letter_nav


register = template.Library()


@register.simple_tag(takes_context=True)
def glossary_navigation_secondary(context):
    letter_nav = get_letter_nav()

    html = '''
            <a class="text-white d-block d-md-none nav-link dropdown-toggle" href="#" id="GlossaryNavDropdown" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Navigate to letter</a>
            <div class="dropdown-menu dropdown-menu-special shadow" aria-labelledby="GlossaryNavDropdown">
            '''

    for letter, exists in letter_nav.items():
        disabled, aria_disabled = 'disabled', 'true'
        current = context.get('slug') == letter
        if current:
            current = 'current'
        else:
            current = ''
        if exists == True:
            disabled, aria_disabled = '', 'false'
        url = reverse('glossary:letter', kwargs={'slug': letter})
        html += f'''
            <a class="dropdown-item {disabled} {current}" href="{ url }" aria-disabled="{aria_disabled}">{ letter }</a>
        '''

    html += '''</div>'''

    return mark_safe(html)