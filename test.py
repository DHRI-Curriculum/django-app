from dhri.utils.loader_v2 import Loader
from dhri.interaction import Logger
from bs4 import BeautifulSoup
from pathlib import Path
import requests



repo = "https://github.com/DHRI-Curriculum/text-analysis"
branch = 'v2.0-rafa-edits'

STATIC_IMAGES = Path('./app/workshop/static/images/lessons/')
REPO_CLEAR = "".join(repo.split("https://github.com/DHRI-Curriculum/")[1:])


l = Loader(repo)
log = Logger()



for lesson_data in l.as_html.lessons:
    soup = BeautifulSoup(lesson_data['text'], 'lxml')
    for image in soup.find_all("img"):
        filename = image['src'].split('/')[-1]
        url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{REPO_CLEAR}/{branch}/images/{filename}'
        local_file = STATIC_IMAGES / Path(REPO_CLEAR) / filename
        download_image(url, local_file)
        local_url = f'/static/images/lessons/{REPO_CLEAR}/{filename}'
        image['src'] = local_url

    # do something with soup...