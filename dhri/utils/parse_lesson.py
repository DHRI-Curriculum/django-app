from dhri.interaction import Logger
from dhri.utils.markdown import split_into_sections
from dhri.settings import STATIC_IMAGES, LESSON_TRANSPOSITIONS
from pathlib import Path
import requests
import markdown
from requests.exceptions import HTTPError, MissingSchema
from bs4 import BeautifulSoup, Comment
from dhri.utils.webcache import WebCache

log = Logger(name='lesson-parser')
md_to_html_parser = markdown.Markdown(extensions=['extra', 'codehilite', 'sane_lists', 'nl2br'])



def download_image(url, local_file):
    if not isinstance(local_file, Path): local_file = Path(local_file)
    if not local_file.parent.exists(): local_file.parent.mkdir(parents=True)
    if not local_file.exists():
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_file, 'wb+') as f:
                for chunk in r:
                    f.write(chunk)
        elif r.status_code == 404:
            url = url.replace('/images/', '/sections/images/')
            r = requests.get(url)
            if r.status_code == 200:
                with open(local_file, 'wb+') as f:
                    for chunk in r:
                        f.write(chunk)
            elif r.status_code == 404:
                log.warning(f"Could not download image {local_file.name} (not found): {url}")
            elif r.status_code == 403:
                log.warning(f"Could not download image {local_file.name} (not allowed)")
        elif r.status_code == 403:
            log.warning(f"Could not download image {local_file.name} (not allowed)")



class LessonParser():

    def __init__(self, markdown:str, loader:object):
        self.markdown = markdown
        try:
            self.repo = loader.repo
            self.branch = loader.branch
        except:
            self.repo = None
            self.branch = None
            log.warning('No loader object provided so will not download images from lesson file for repository.')

        self.data = []
        self.html_data = []

        for title, body in split_into_sections(self.markdown, level_granularity=1, clear_empty_lines=False).items():
            droplines = []

            challenge = ""
            # 1. Test markdown for challenge
            if "challenge" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## challenge"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                challenge += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            solution = ""
            # 2. Test markdown for solution
            if "solution" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## solution"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                solution += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            # 3. Fix markdown body
            cleaned_body = ''
            for i, line in enumerate(body.splitlines()):
                if line.strip() == '': continue
                if i not in droplines:
                    cleaned_body += line + '\n'

            # 4. Clean up all markdown data
            title = title.strip()
            body = body.strip()
            challenge = challenge.strip()
            solution = solution.strip()

            if challenge == '': challenge = None
            if solution == '': solution = None

            if solution and not challenge:
                log.error(f"The lesson `{title}` has a solution but no challenge. The program has stopped.")
            elif challenge and not solution:
                log.warning(f'The lesson `{title}` has a challenge with no solution.')

            data = {
                    'title': title,
                    'text': cleaned_body,
                    'challenge': challenge,
                    'solution': solution
                }

            self.data.append(data)


            # Next up: HTML parsing

            html_body = md_to_html_parser.convert(cleaned_body.replace('\n', '\n'))
            html_challenge, html_solution = '', ''
            if challenge: html_challenge = md_to_html_parser.convert(challenge)
            if solution: html_solution = md_to_html_parser.convert(solution)

            soup = BeautifulSoup(html_body, 'lxml')

            # 1. Attempt to download any images
            if self.repo:
                REPO_CLEAR = "".join(self.repo.split("https://github.com/DHRI-Curriculum/")[1:])
                for image in soup.find_all("img"):
                    src = image.get('src')
                    if not src:
                        log.warning(f"An image with no src attribute detected in lesson: {image}")
                        continue
                    filename = image['src'].split('/')[-1]
                    url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{REPO_CLEAR}/{self.branch}/images/{filename}'
                    local_file = STATIC_IMAGES['LESSONS'] / Path(REPO_CLEAR) / filename
                    download_image(url, local_file)
                    local_url = f'/static/images/lessons/{REPO_CLEAR}/{filename}'
                    image['src'] = local_url

            # 2. Find and test links
            for link in soup.find_all("a"):
                href = link.get('href')
                if not href:
                    log.warning(f"A link with no href attribute detected in lesson: {link}")
                    continue
                c = WebCache(href)
                if "github.com/DHRI-Curriculum" in href:
                    log.warning("Internal links in curriculum detected.")

            # 3. Fix tables
            for table in soup.find_all("table"):
                table['class'] = table.get('class', []) + ['table']

            # 4. Replace transpositions
            string_soup = str(soup)
            for transposition in LESSON_TRANSPOSITIONS:
                if (string_soup.find(transposition + '<br>'),
                    string_soup.find(transposition + '<br/>'),
                    string_soup.find(transposition + '<br />')):
                    string_soup = string_soup.replace(transposition + '<br>', transposition).replace(transposition + '<br/>', transposition).replace(transposition + '<br />', transposition)
                string_soup = string_soup.replace(transposition, LESSON_TRANSPOSITIONS[transposition])

            # 5. Replace body with string_soup, after cleaning it up
            html_body = string_soup.replace('<html><body>', '').replace('</body></html>', '').replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')

            # 6. Clean up any challenge and solution data
            html_challenge = html_challenge.replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')
            html_solution = html_solution.replace('\n<br />\n', '').replace('\n<br />\n', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')

            html_data = {
                    'title': title,
                    'text': html_body,
                    'challenge': html_challenge,
                    'solution': html_solution
                }

            self.html_data.append(html_data)


    def __len__(self):
        return(len(self.data))