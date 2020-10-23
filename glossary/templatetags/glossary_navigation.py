from django import template
from django.urls import reverse
from glossary.models import Term
from django.utils.safestring import mark_safe


register = template.Library()


def get_letter_nav():
    d = dict()
    letters = [x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    for t in Term.objects.all().order_by('term'):
        if not t.term[:1].upper() in letters: letters.append(t.term[:1].upper())
    for letter in letters:
        d[letter] = Term.objects.filter(term__startswith=letter).exists()
    return d

@register.simple_tag(takes_context=True)
def glossary_navigation(context):
    letter_nav = get_letter_nav()

    html = '''<nav class="d-none d-md-flex justify-content-center" id="glossary-nav" aria-label="Glossary navigation"><ul class="pagination pagination-sm">'''
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
        <li class="page-item {disabled} {current}">
            <a class="page-link {disabled} {current}" href="{ url }" tabindex="-1" aria-disabled="{aria_disabled}">{ letter }</a>
        </li>
        '''

    html += '''</ul></nav>'''

    return mark_safe(html)
