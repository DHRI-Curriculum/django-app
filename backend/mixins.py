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


# Perhaps I should move this to the markdown processing instead and exclude the codeblocks from this....? # TODO: #410
def convert_html_quotes(html, strip_surrounding_body=True, strip_surrounding_p=False):
    if not html:
        return ''
    soup = BeautifulSoup(html, 'lxml')
    for text_node in soup.find_all(string=True):
        if 'code' in [x.name for x in text_node.parents]:
            text_node = text_node
        elif 'span' in [x.name for x in text_node.parents]:
            import pprint
            pprint.pprint([x for x in text_node.parents])
            exit()
            # TODO: Here, we need to also find any div elements that contain code....
        else: # TODO: #410 this should exclude code, where we don't want to enforce any curly quotes due to accessibility (ease of copying code etc)
            text_node.replaceWith(quote_converter(text_node))

    if strip_surrounding_body:
        if soup.body:
            try:
                html = "".join([str(x) for x in soup.body.children])
            except AttributeError:
                print('strip_surrounding_body: ' + html)
                exit()
        else:
            print('strip_surrounding_body called but no body:')
            print(soup)
            exit()
    elif strip_surrounding_p:
        bottom_elem = soup.p
        if not bottom_elem:
            bottom_elem = soup.body
        if not bottom_elem:
            print('strip_surrounding_p called but no p:')
            print(soup)
            exit()
            
        try:
            html = "".join([str(x) for x in bottom_elem.children])
        except AttributeError:
            print('strip_surrounding_p: ' + html)
            exit()
    else:
        html = str(soup)
        print('here.....')
        exit()

    return html


class CurlyQuotesMixin:
    curly_fields = []
    unwrap_p = False

    def save(self, *args, **kwargs):
        for field in self.curly_fields:
            html = getattr(self, field, None)
            if html == None or html == '' or html == 'NULL':
                continue
            # print(field, '-->', html)
            if self.unwrap_p:
                html = convert_html_quotes(html, strip_surrounding_body=False, strip_surrounding_p=True)
            else:
                html = convert_html_quotes(html)
            setattr(self, field, html)

        super().save(*args, **kwargs)

