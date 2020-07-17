'''
from backend.dhri.log import Logger
from backend.dhri.markdown import split_into_sections
from backend.dhri_settings import STATIC_IMAGES, LESSON_TRANSPOSITIONS
from pathlib import Path
import re
import requests
from requests.exceptions import HTTPError, MissingSchema
from bs4 import BeautifulSoup, Comment
from backend.dhri.webcache import WebCache

log = Logger(name='lesson-parser')

PARSER = GitHubParser()
'''