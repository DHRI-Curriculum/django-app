from django import template
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


register = template.Library()


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code class="highlight">%s</code></pre>\n' % \
                mistune.escape(code)
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter()
            return highlight(code, lexer, formatter)
        except:
            return '\n<pre><code class="highlight">%s</code></pre>\n' % \
                mistune.escape(code)


@register.filter
def markdown(value):
    try:
        renderer = HighlightRenderer()
        markdown = mistune.Markdown(renderer=renderer)
        return markdown(value)
    except:
        return value

@register.filter
def as_string(value):
    return str(value)

@register.filter
def nl2br(value):
    return str(value).replace('\n', '<br />')

@register.filter
def get_item(dictionary, key):
    if key in dictionary: return dictionary.get(key)
    return ''

@register.filter
def get_item_type(dictionary, key):
    if dictionary.get(key): return(type(dictionary.get(key)))
    return(None)

@register.filter
def is_list(dictionary, key):
    if dictionary.get(key): return(isinstance(dictionary.get(key), list))
    return(False)

@register.filter
def page_window(page, last, size=7):
    if page < size // 2 + 1:
        return range(1, min(size+1, last + 1)) # remember the range function won't
                                                # include the upper bound in the output
    else:
        return range(page - size // 2, min(last + 1, page + 1 + size // 2))
