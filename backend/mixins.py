from bs4 import BeautifulSoup
import re


def quote_converter(string):
    """Takes a string and returns it with dumb quotes, single and double,
    replaced by smart quotes. Accounts for the possibility of HTML tags
    within the string."""

    # Find dumb double quotes coming directly after letters or punctuation,
    # and replace them with right double quotes.
    string = re.sub(r'([a-zA-Z0-9.,?!;:\'\"])"', r'\1”', string)
    # Find any remaining dumb double quotes and replace them with
    # left double quotes.
    string = string.replace('"', '“')

    # Follow the same process with dumb/smart single quotes
    string = re.sub(r"([a-zA-Z0-9.,?!;:\"\'])'", r'\1’', string)
    string = string.replace("'", '‘')

    return string


class CurlyQuotesMixin:
    curly_fields = []

    def save(self, *args, **kwargs):
        for field in self.curly_fields:
            html = getattr(self, field)
            soup = BeautifulSoup(html, 'lxml')
            for text_node in soup.find_all(string=True):
                text_node.replaceWith(quote_converter(text_node))
            html = "".join([str(x) for x in soup.body.children])
            setattr(self, field, html)

        super().save(*args, **kwargs)
