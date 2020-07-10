from dhri import debug
from dhri.django import django, Fixture
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor, Lesson, Challenge, Solution, Page
from dhri.interaction import Logger, get_or_default
from dhri.settings import AUTO_PROCESS, FIXTURE_PATH, REPLACEMENTS
from dhri.utils.loader import WebCache
from dhri.utils.loader_v2 import Loader
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list, get_contributors, Markdown, extract_links
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs, auto_replace
from dhri.utils.exceptions import MissingCurriculumFile, MissingRequiredSection
from dhri.utils.regex import all_images

# Set up empty stuff for entire loop ##########################
log = Logger(name="main")
iteration, all_objects, done, collect_workshop_slugs = 0, [], 'n', []
fixtures = Fixture(name='fixtures')
saved_prefix = '-----> '
###############################################################

if __name__ == '__main__':
    while done == 'n':
        repo, repo_name, branch, collector = '', '', '', {}

        try:
            repo, branch = AUTO_PROCESS.pop(0)
            log.name = 'populate'
            log.log(f'In AUTO_PROCESS mode: Current iteration {iteration}. Processing {repo}/{branch}, Remaining: {len(AUTO_PROCESS)}. Finished workshops: {collect_workshop_slugs}')
        except IndexError:
            repo = get_or_default(f'What is the repo name (assuming DHRI-Curriculum as username) or whole GitHub link you want to import?', repo)
            if repo == '':
                log.error('No repository name, exiting...', kill=None)
                done = 'y'
                continue

            branch = get_or_default(f'What is the branch name you want to import?', branch)
            if branch == '':
                log.error('No branch name, exiting...', kill=None)
                done = 'y'
                continue

        if not repo.startswith('https://github.com/'): # FIXME: If we decide to move to a different backend
            repo = f'https://github.com/DHRI-Curriculum/{repo}'


        ###### Load in data from GitHub (handled by dhri.utils.loader.Loader)

        try:
            l = Loader(repo, branch)
        except MissingRequiredSection:
            log.error(f"One or more required section(s) could not be found in {l.repo_name}.", kill=False)


        ###### Test for data consistency
        if sum([l.has_frontmatter, l.has_praxis, l.has_assessment]) <= 2:
            log.error(f"The repository {l.repo_name} does not have enough required files present. The import of the entire repository will be skipped.", kill=None)
            iteration += 1
            continue


        if AUTO_PROCESS:
            repo_name = l.meta['repo_name']
        else:
            repo_name = get_or_default('Repository', l.meta['repo_name'])

        repo_name = get_or_default('Workshop name', auto_replace(repo_name.title()))
        log.name = l.repo_name
        log.original_name = log.name


        ###### WORKSHOP MODEL ####################################

        log.name = log.original_name + "-workshop"
        workshop = Workshop(
                name = repo_name,
                parent_backend = l.parent_backend,
                parent_repo = l.parent_repo,
                parent_branch = l.parent_branch
            )
        workshop.save()
        log.log(saved_prefix + f'Workshop object {workshop.name} added (ID {workshop.id}).')
        collect_workshop_slugs.append(workshop.slug)


        ###### LESSONS ####################################
        if l.has_lessons:
            log.name = log.original_name + "-lessons"
            log.log("------ LESSONS ------------------------------------------")
            collector['lessons'] = []
            collector['challenges'] = []
            collector['solutions'] = []

            order = 1

            from pathlib import Path
            from dhri.utils.parse_lesson import download_image
            from bs4 import BeautifulSoup

            STATIC_IMAGES = Path('./app/workshop/static/images/lessons/')
            REPO_CLEAR = "".join(repo.split("https://github.com/DHRI-Curriculum/")[1:])

            for lesson_data in l.as_html.lessons:
                soup = BeautifulSoup(lesson_data['text'], 'lxml')
                for image in soup.find_all("img"):
                    filename = image['src'].split('/')[-1]
                    url = f'https://raw.githubusercontent.com/DHRI-Curriculum/{REPO_CLEAR}/{branch}/images/{filename}'
                    local_file = STATIC_IMAGES / Path(REPO_CLEAR) / filename
                    download_image(url, local_file)
                    local_url = f'/static/images/lessons/{REPO_CLEAR}/{filename}'
                    image['src'] = local_url

                for link in soup.find_all("a"):
                    href = link['href']
                    c = WebCache(href)
                    if "github.com/DHRI-Curriculum" in href:
                        log.warning("Internal links in curriculum detected.")
                    elif href.startswith('http'):
                        if c.status_code != 200:
                            log.warning(f"Link detected in lesson that generated a {c.status_code} status code: {href}")
                    '''
                    except:
                        log.error(f"Fatal error when connecting to URL detected in lesson: {href}", kill=False)
                    '''

                clean_html = str(soup).replace('<html><body>', '').replace('</body></html>', '').replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')

                lesson = Lesson(
                    workshop = workshop,
                    title = lesson_data['title'],
                    text = clean_html,
                    order = order
                )
                lesson.save()
                collector['lessons'].append(lesson)
                order += 1
                if lesson_data['challenge']:
                    clean_html = lesson_data['challenge'].replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')
                    challenge = Challenge(
                        lesson = lesson,
                        text = clean_html
                    )
                    challenge.save()
                    collector['challenges'].append(challenge)
                if lesson_data['solution']:
                    clean_html = lesson_data['solution'].replace('<br />', '</p><p>').replace('<br/>', '</p><p>').replace('<br>', '</p><p>')
                    solution = Solution(
                        challenge = challenge,
                        text = clean_html
                    )
                    solution.save()
                    collector['solutions'].append(solution)

            if len(collector['lessons']):
                log.log(f'Summary: Workshop {workshop.name} updated with {len(collector["lessons"])} lessons.')

            if len(collector['challenges']):
                log.log(f'Summary: Lessons had {len(collector["challenges"])} challenges added to them.')

            if len(collector['solutions']):
                log.log(f'Summary: Lessons had {len(collector["solutions"])} challenges added to them.')

        ###### FRONTMATTER MODELS ####################################

        for model in l.frontmatter_models:

            # frontmatter.Frontmatter
            if model == Frontmatter:
                log.name = log.original_name + "-frontmatter"
                log.log("------ FRONTMATTER ------------------------------------------")
                frontmatter = Frontmatter(workshop = workshop)
                frontmatter.abstract = l.abstract
                frontmatter.ethical_considerations = l.ethical_considerations
                frontmatter.estimated_time = get_number(l.frontmatter['estimated_time'])
                frontmatter.save()
                log.log(saved_prefix + f'Frontmatter object {frontmatter.id} added to workshop {workshop}.')

            # frontmatter.LearningObjective
            elif model == LearningObjective:
                log.name = log.original_name + "-learning-obj"
                collector['learning_objectives'] = []
                for line in l.learning_objectives:
                    label = str(line)
                    o = LearningObjective(frontmatter=frontmatter, label=label)
                    o.save()
                    collector['learning_objectives'].append(o)
                if len(collector['learning_objectives']):
                    log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["learning_objectives"])} learning objectives.')

            # frontmatter.Project
            elif model == Project:
                log.name = log.original_name + "-projects"
                collector['projects'] = []
                for line in l.projects:
                    o = Project()
                    o.annotation = str(line)
                    links = extract_links(line)
                    if links: o.title, o.url = links[0]
                    if len(links) > 1: log.warning(f'One project seems to contain more than one URL, but only one ({o.url}) is captured: {links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Project has no title. The annotation is set to: {o.annotation}", kill=None)
                        o.title = WebCache(o.url).title
                        o.title = get_or_default('Set a title for the project with the comment above', o.title, color='red')
                    o.save()
                    collector['projects'].append(o)
                    log.log(f'Project added: "{o.title}" ({o.url})')
                frontmatter.projects.set(collector['projects'])
                log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["projects"])} projects.')

            # frontmatter.Reading
            elif model == Reading:
                log.name = log.original_name + "-readings"
                collector['frontmatter_readings'] = []
                for line in l.readings:
                    o = Reading()
                    o.annotation = str(line)
                    if extract_links(line): o.title, o.url = extract_links(line)[0]
                    if len(extract_links(line)) > 1: log.warning(f'One reading seems to contain more than one URL, but only one ({o.url}) is captured: {line.links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Reading has no title. The annotation is set to: {o.annotation}", kill=None)
                        o.title = WebCache(o.url).title
                        o.title = get_or_default('Set a title for the reading with the annotation above', o.title, color='red')
                    o.save()
                    collector['frontmatter_readings'].append(o)
                    log.log(f'Reading added: "{o.title}" ({o.url})')
                frontmatter.readings.set(collector['frontmatter_readings'])
                log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["frontmatter_readings"])} readings.')

            # frontmatter.Contributor
            elif model == Contributor:
                log.name = log.original_name + "-contributors"
                collector['contributors'] = []
                for contributor in l.contributors:
                    first_name, last_name, role, url = contributor.get('first_name'), contributor.get('last_name'), contributor.get('role'), contributor.get('url')
                    o = Contributor()
                    o.first_name, o.last_name, o.role, o.url = first_name, last_name, role, url
                    o.save()
                    collector['contributors'].append(o)
                    msg = saved_prefix + f'Contributor {o.full_name} added.'
                    if o.role != '': msg = msg.replace('added', f'({o.role}) added')
                    log.log(msg)
                frontmatter.contributors.set(collector['contributors'])
                log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["contributors"])} contributors.')

            else:
                log.error(f'Have no way of processing {model} (for app `frontmatter`). The `populate` script must be adjusted accordingly.', kill=False)


        ###### PRAXIS MODELS ####################################

        for model in l.praxis_models:
            if model == Praxis:
                log.name = log.original_name + "-praxis"
                log.log("------ PRAXIS ------------------------------------------")
                praxis = Praxis(workshop = workshop)
                praxis.discussion_questions = l.discussion_questions
                praxis.next_steps = l.next_steps
                praxis.save()
                log.log(saved_prefix + f'Theory-to-practice object {praxis.id} added to workshop {workshop}.')

            elif model == Tutorial:
                log.name = log.original_name + "-tutorials"
                collector['tutorials'] = []
                for line in l.tutorials:
                    o = Tutorial()
                    o.annotation = str(line)
                    links = extract_links(line)
                    if links: o.label, o.url = links[0]
                    if len(links) > 1: log.warning(f'One tutorial seems to contain more than one URL, but only one ({o.url}) is captured: {links}')
                    if o.label.lower().strip() == '':
                        log.error(f"Tutorial has no label. The annotation is set to: {o.annotation}", kill=None)
                        o.label = WebCache(o.url).title
                        o.label = get_or_default('Set a label for the tutorial with the annotation above', o.label, color='red')
                    o.save()
                    collector['tutorials'].append(o)
                    log.log(f'Tutorial added: "{o.label}" ({o.url})')
                if len(collector['tutorials']):
                    praxis.tutorials.set(collector['tutorials'])
                    log.log(f'Summary: Praxis {praxis.id} updated with {len(collector["tutorials"])} tutorials.')

            elif model == Reading:
                log.name = log.original_name + "-readings"
                collector['praxis_readings'] = []
                for line in l.further_readings:
                    o = Reading()
                    o.annotation = str(line)
                    links = extract_links(line)
                    if links: o.title, o.url = links[0]
                    if len(links) > 1: log.warning(f'One reading (in the praxis section) seems to contain more than one URL, but only one ({o.url}) is captured: {links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Reading has no title. The annotation is set to: {o.annotation}", kill=None)
                        o.title = WebCache(o.url).title
                        o.title = get_or_default('Set a title for the reading with the annotation above', o.title, color='red')
                    o.save()
                    collector['praxis_readings'].append(o)
                    log.log(f'Reading added: "{o.title}" ({o.url})')
                if len(collector['praxis_readings']):
                    praxis.further_readings.set(collector['praxis_readings'])
                    log.log(f'Summary: Praxis {praxis.id} updated with {len(collector["praxis_readings"])} further readings.')

            else:
                log.error(f'Have no way of processing {model} for app `praxis`. The `populate` script must be adjusted accordingly.', kill=False)



        fixtures.add(workshop=workshop, frontmatter=frontmatter, praxis=praxis, collector=collector)

        if AUTO_PROCESS:
          done, msg = 'n', 'Are you done? [y/N] '
          done = get_or_default(msg, done, color='red').lower()
        else:
          done = 'y'

        iteration += 1

    # Add standard setup of pages
    collector = dict()
    collector['pages'] = []

    p = Page(
        name = 'Workshops',
        slug = 'workshops',
        text = '<p class="lead">This is the workshop page.</p>',
        template = 'workshop/workshop-list.html'
    )
    p.save()
    collector['pages'].append(p)

    p = Page(
        name = 'About',
        slug = 'about',
        text = '<p class="lead">This is the about page.</p>',
        template = 'website/page.html'
    )
    p.save()
    collector['pages'].append(p)

    p = Page(
        name = 'Library',
        slug = 'library',
        text = '<p class="lead">This is the library page.</p>',
        template = 'library/all-library-items.html'
    )
    p.save()
    collector['pages'].append(p)

    fixtures.add(collector=collector)

    fixtures.save()

    from dhri.setup import setup
    setup(collect_workshop_slugs)
