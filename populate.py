from dhri import debug
from dhri.django import django, Fixture
from dhri.django.models import *
from dhri.interaction import Logger, get_or_default
from dhri.settings import AUTO_PROCESS, FIXTURE_PATH, REPLACEMENTS, LESSON_TRANSPOSITIONS, AUTO_PAGES
from dhri.utils.webcache import WebCache
from dhri.utils.loader import Loader
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list, get_contributors, Markdown, extract_links
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs, auto_replace
from dhri.utils.exceptions import MissingCurriculumFile, MissingRequiredSection

# Set up empty stuff for entire loop ##########################
log = Logger(name="main")
iteration, all_objects, done, collect_workshop_slugs = 0, list(), 'n', list()
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
        workshop = Workshop.objects.create(
                name = repo_name,
                parent_backend = l.parent_backend,
                parent_repo = l.parent_repo,
                parent_branch = l.parent_branch
            )
        log.log(saved_prefix + f'Workshop object {workshop.name} added (ID {workshop.id}).')
        collect_workshop_slugs.append(workshop.slug)


        ###### LESSONS ####################################
        if l.has_lessons:
            log.name = log.original_name + "-lessons"
            collector['lessons'] = list()
            collector['challenges'] = list()
            collector['solutions'] = list()

            order = 1

            for lesson_data in l.as_html.lessons:
                lesson = Lesson.objects.create(
                    workshop = workshop,
                    title = lesson_data['title'],
                    text = lesson_data['text'],
                    order = order
                )
                collector['lessons'].append(lesson)
                order += 1
                if lesson_data['challenge']:
                    challenge = Challenge.objects.create(
                        lesson = lesson,
                        text = lesson_data['challenge']
                    )
                    collector['challenges'].append(challenge)
                if lesson_data['solution']:
                    solution = Solution.objects.create(
                        challenge = challenge,
                        text = lesson_data['solution']
                    )
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
                frontmatter = Frontmatter.objects.create(
                    workshop = workshop,
                    abstract = l.abstract,
                    # ethical_considerations = l.ethical_considerations,
                    estimated_time = get_number(l.frontmatter['estimated_time']),
                )
                log.log(saved_prefix + f'Frontmatter object {frontmatter.id} added to workshop {workshop}.')

                collector['ethical_considerations'] = list()
                for label in l.ethical_considerations:
                    o = EthicalConsideration.objects.create(
                        frontmatter = frontmatter,
                        label = str(label)
                    )
                    collector['ethical_considerations'].append(o)
                if len(collector['ethical_considerations']):
                    log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["ethical_considerations"])} ethical considerations.')

            # frontmatter.LearningObjective
            elif model == LearningObjective:
                log.name = log.original_name + "-learning-obj"
                collector['learning_objectives'] = list()
                for line in l.learning_objectives:
                    o = LearningObjective.objects.create(
                        frontmatter = frontmatter,
                        label = str(line)
                    )
                    collector['learning_objectives'].append(o)
                if len(collector['learning_objectives']):
                    log.log(f'Summary: Frontmatter {frontmatter.id} updated with {len(collector["learning_objectives"])} learning objectives.')

            # frontmatter.Project
            elif model == Project:
                log.name = log.original_name + "-projects"
                collector['projects'] = list()
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
                collector['frontmatter_readings'] = list()
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
                collector['contributors'] = list()
                for contributor in l.contributors:
                    o = Contributor.objects.create(
                        first_name = contributor.get('first_name'),
                        last_name = contributor.get('last_name'),
                        role = contributor.get('role'),
                        url = contributor.get('url'),
                    )
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
                praxis = Praxis.objects.create(
                    workshop = workshop,
                    discussion_questions = l.discussion_questions,
                    next_steps = l.next_steps
                )
                log.log(saved_prefix + f'Theory-to-practice object {praxis.id} added to workshop {workshop}.')

            elif model == Tutorial:
                log.name = log.original_name + "-tutorials"
                collector['tutorials'] = list()
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
                collector['praxis_readings'] = list()
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
    collector['pages'] = list()
    collector['groups'] = list()

    log.log("Installing pages...")
    for page in AUTO_PAGES:
        if Page.objects.filter(name = page['name']).count() > 0:
            log.warning(f'Page `page["name"]` already exists.')
        else:
            p = Page.objects.create(
                name = page['name'],
                slug = page['slug'],
                text = page['text'],
                template = page['template']
            )
            collector['pages'].append(p)
            log.log('Page `page["name"]` added.')

    log.log("Installing authorization data...")
    if Group.objects.filter(name = 'Learner').count() > 0:
        log.warning("Group `Learner` already exists.")
    else:
        g = Group.objects.create(name = 'Learner')
        collector['groups'].append(g)
        log.log("Group `Learner` added.")

    fixtures.add(collector=collector)

    fixtures.save()

    from dhri.setup import setup
    setup(collect_workshop_slugs)
