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
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)


@register.filter
def markdown(value):
    renderer = HighlightRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(value)


@register.filter
def transpose_md_headers(value):
    """Transposes markdown headers down one degree in given string"""
    return value.replace("### ", "#### ").replace("## ", "### ").replace("# ", "## ")


@register.filter
def page_window(page, last, size=7):
    if page < size // 2 + 1:
        return range(1, min(size+1, last + 1)) # remember the range function won't
                                                # include the upper bound in the output
    else:
        return range(page - size // 2, min(last + 1, page + 1 + size // 2))
