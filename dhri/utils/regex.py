import re

MULTILINE_ITEM = r"\s{3,10}"
HAS_BULLETPOINTS = r"\n?-"
GET_BULLETPOINTS = {
    'ALL': r'\n?- (.*)(?:(?=\s{2,8})\s{2,8}(.*))?',
    'THOSE_WITH_EXTRA_PARAGRAPH': r'\n?- (.*)\n(?=  )\s+(.*)\n?',
    'THOSE_WITH_NO_EXTRA_PARAGRAPH': r'\n?- (.*)\n(?!  )'
}
GET_NUMBERED_LISTS = {
    'ALL': r'\n?[1-9]\. (.*)(?>(?=\s{2,8})\s{2,8}(.*))?',
}
GET_QUESTIONS = {
    'ALL': r'', # TODO: this one is hard for my head right now
    'ONLY_QUESTIONS': r'\n|^(?(?!- ).*)',
    'ONLY_ANSWERS': r'\n|^(?(?=- ).*)',
}

ALL_BULLETS = GET_BULLETPOINTS['ALL']
BULLETS_EXTRA_P = GET_BULLETPOINTS['THOSE_WITH_EXTRA_PARAGRAPH']
BULLETS_NO_EXTRA_P = GET_BULLETPOINTS['THOSE_WITH_NO_EXTRA_PARAGRAPH']
ALL_NUMBERS = GET_NUMBERED_LISTS['ALL']

MD_LIST_ELEMENTS = r'\- (.*)(\n|$)'
NUMBERS = r'(\d+([\.,][\d+])?)'

URL_COMPONENTS = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?'
URL = r'((http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?)'

MARKDOWN_HREF = r'\[(.*)\]\((.*)\)' # [Text to link](http://URL)