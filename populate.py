from dhri import debug
from dhri.django import django, Fixture
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor
from dhri.interaction import Logger, get_or_default
from dhri.settings import AUTO_PROCESS, FIXTURE_PATH, REPLACEMENTS
from dhri.utils.loader import Loader, WebCache
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list, get_contributors, Markdown
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs, auto_replace
from dhri.utils.exceptions import MissingCurriculumFile, MissingRequiredSection

# Set up empty stuff for entire loop ##########################
log = Logger(name="main")
iteration, all_objects, done, collect_workshop_slugs = 0, [], 'n', []
fixtures = Fixture(name='fixtures')
saved_prefix = '-----> '
###############################################################

if __name__ == '__main__':
    while done == 'n':
        iteration += 1
        repo, branch, collector = '', '', {}
        AUTO_PROCESS_done = len(AUTO_PROCESS) == iteration

        if AUTO_PROCESS and not AUTO_PROCESS_done:
            repo, branch = AUTO_PROCESS[iteration-1]
        else:
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
            log.error("One or more required section(s) could not be found.", kill=False)

        if AUTO_PROCESS:
            repo_name = l.meta['repo_name']
        else:
            repo_name = get_or_default('Repository', l.meta['repo_name'])

        repo_name = get_or_default('Workshop name', auto_replace(repo_name.title()))
        log.name = l.repo_name
        log.original_name = log.name


        ###### Test for data consistency

        if not l.has_frontmatter and not l.has_praxis and not l.has_assessment:
            log.error("The repository has none of the required files present. The import of the entire repository will be skipped.", kill=None)
            done = 'y'
            continue


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
                if l.learning_objectives.links: log.warning(f'Looks like the learning objectives have URLs but the database has no way to keep them.')
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
                    o.comment = str(line)
                    if line.has_links: o.title, o.url = line.links[0]
                    if line.has_multiple_links: log.warning(f'One project seems to contain more than one URL, but only one ({o.url}) is captured: {line.links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Project has no title. The comment is set to: {o.comment}", kill=None)
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
                    o.comment = str(line)
                    if line.has_links: o.title, o.url = line.links[0]
                    if line.has_multiple_links: log.warning(f'One reading seems to contain more than one URL, but only one ({o.url}) is captured: {line.links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Reading has no title. The comment is set to: {o.comment}", kill=None)
                        o.title = WebCache(o.url).title
                        o.title = get_or_default('Set a title for the reading with the comment above', o.title, color='red')
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
                    first_name, last_name, role, link = contributor
                    o = Contributor()
                    o.first_name, o.last_name, o.role, o.link = contributor
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
                    o.comment = str(line)
                    if line.has_links: o.label, o.url = line.links[0]
                    if line.has_multiple_links: log.warning(f'One tutorial seems to contain more than one URL, but only one ({o.url}) is captured: {line.links}')
                    if o.label.lower().strip() == '':
                        log.error(f"Tutorial has no label. The comment is set to: {o.comment}", kill=None)
                        o.label = WebCache(o.url).title
                        o.label = get_or_default('Set a label for the tutorial with the comment above', o.label, color='red')
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
                    o.comment = str(line)
                    if line.has_links: o.title, o.url = line.links[0]
                    if line.has_multiple_links: log.warning(f'One reading (theory-to-practice) seems to contain more than one URL, but only one ({o.url}) is captured: {line.links}')
                    if o.title.lower().strip() == '':
                        log.error(f"Reading has no title. The comment is set to: {o.comment}", kill=None)
                        o.title = WebCache(o.url).title
                        o.title = get_or_default('Set a title for the reading with the comment above', o.title, color='red')
                    o.save()
                    collector['praxis_readings'].append(o)
                    log.log(f'Reading added: "{o.title}" ({o.url})')
                if len(collector['praxis_readings']):
                    praxis.further_readings.set(collector['praxis_readings'])
                    log.log(f'Summary: Praxis {praxis.id} updated with {len(collector["praxis_readings"])} further readings.')

            else:
                log.error(f'Have no way of processing {model} for app `praxis`. The `populate` script must be adjusted accordingly.', kill=False)



        fixtures.add(workshop=workshop, frontmatter=frontmatter, praxis=praxis, collector=collector)

        if AUTO_PROCESS and AUTO_PROCESS_done:
          done, msg = 'y', 'Are you done? [Y/n] '
        elif AUTO_PROCESS:
          done, msg = 'n', 'Are you done? [y/N] '
          done = get_or_default(msg, done, color='red').lower()
        else:
          done = 'y'

    fixtures.save()

    from dhri.setup import setup
    setup(collect_workshop_slugs)
