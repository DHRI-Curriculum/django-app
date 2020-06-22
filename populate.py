from dhri import debug
from dhri.django import django, Fixture
from dhri.django.models import Workshop, Praxis, Tutorial, Reading, Frontmatter, LearningObjective, Project, Contributor
from dhri.interaction import Logger, get_or_default
from dhri.settings import AUTO_PROCESS, FIXTURE_PATH
from dhri.utils.loader import Loader
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list, get_contributors, destructure_list
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs
from dhri.utils.exceptions import MissingCurriculumFile, MissingRequiredSection

# Set up empty stuff for entire loop ##########################
log = Logger(name="main")
iteration, all_objects, done, collect_workshop_slugs = 0, [], 'n', []
fixtures = Fixture(name='fixtures')
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
            log.error("A required section could not be found.", kill=False)

        if AUTO_PROCESS:
            repo_name = l.meta['repo_name']
        else:
            repo_name = get_or_default('Repository', l.meta['repo_name'])

        repo_name = get_or_default('Workshop name', repo_name.replace('-', ' ').title().replace('Html Css', 'HTML/CSS')) # TODO: #61 Add an autocorrection in settings
        log.name = l.repo_name


        ###### Test for data consistency

        if not l.has_frontmatter and not l.has_praxis and not l.has_assessment:
            log.error("The repository has none of the required files present. The import of the entire repository will be skipped.", kill=None)
            done = 'y'
            continue


        ###### WORKSHOP MODELS ####################################

        workshop = Workshop(
                name = repo_name,
                parent_backend = l.parent_backend,
                parent_repo = l.parent_repo,
                parent_branch = l.parent_branch
            )
        workshop.save()
        log.log(f'Workshop object {workshop.name} added (ID {workshop.id}).')
        collect_workshop_slugs.append(workshop.slug)


        ###### PRAXIS MODELS ####################################

        for model in l.praxis_models:
            if model == Praxis:
                praxis = Praxis(
                        workshop = workshop,
                    )
                try:
                    praxis.discussion_questions = l.praxis['discussion_questions'] # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for discussion questions.')
                try:
                    praxis.next_steps = l.praxis['next_steps'] # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for next steps.')
                praxis.save()
                log.log(f'Praxis object {praxis.id} added for workshop {workshop}.')

            elif model == Tutorial:
                try:
                  if isinstance(l.praxis['tutorials'], str) and not is_exclusively_bullets(l.praxis['tutorials']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                      log.warning('The Tutorials section contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for tutorials.')
                    continue

                collector['tutorials'] = []
                if isinstance(l.praxis['tutorials'], str):
                    l.praxis['tutorials'] = get_list(l.praxis['tutorials']) # FIXME: #52 Remove dependencies on get_list for destructure_list

                for item in l.praxis['tutorials']:
                    label, comment = item
                    o = Tutorial()
                    o.label = label
                    o.comment = comment
                    urls = get_urls(label)
                    if urls:
                        o.url = urls[0]
                    o.save()
                    collector['tutorials'].append(o)
                    log.log(f'Tutorial {o.id} added:\n    {o.label}')
                praxis.tutorials.set(collector['tutorials'])
                log.log(f'Praxis {praxis.id} updated with tutorials.')

            elif model == Reading:
                try:
                  if isinstance(l.praxis['further_readings'], str) and not is_exclusively_bullets(l.praxis['further_readings']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                      log.warning('Further readings contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for further readings.')
                    continue

                collector['praxis_readings'] = []
                if isinstance(l.praxis['further_readings'], str):
                    l.praxis['further_readings'] = get_list(l.praxis['further_readings']) # FIXME: #52 Remove dependencies on get_list for destructure_list

                for item in l.praxis['further_readings']:
                    title, comment = item
                    o = Reading()
                    o.title = title
                    o.comment = comment
                    o.save()
                    collector['praxis_readings'].append(o)
                    log.log(f'Reading {o.id} added:\n    {o.title}')
                praxis.further_readings.set(collector['praxis_readings'])
                log.log(f'Praxis {praxis.id} updated with further readings.')

            else:
                log.error(f'Have no way of processing {model} for app `praxis`. The `populate` script must be adjusted accordingly.', kill=False)



        ###### FRONTMATTER MODELS ####################################

        for model in l.frontmatter_models:

            # frontmatter.Frontmatter
            if model == Frontmatter:
                frontmatter = Frontmatter(workshop = workshop)

                try:
                    frontmatter.abstract = l.frontmatter['abstract'] # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for abstract.', color='red') # red because it is a significant thing to be missing

                try:
                    frontmatter.ethical_considerations = l.frontmatter['ethical_considerations'] # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for ethical considerations.', color='red')

                try:
                    frontmatter.estimated_time = get_number(l.frontmatter['estimated_time']) # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for estimated time.', color='red')

                frontmatter.save()
                log.log(f'Frontmatter object {frontmatter.id} added for workshop {workshop}.')

            # frontmatter.LearningObjective
            elif model == LearningObjective:
                try:
                  if isinstance(l.frontmatter['learning_objectives'], str) and not is_exclusively_bullets(l.frontmatter['learning_objectives']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                      log.warning('Learning objectives contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for learning objectives.')
                    continue

                collector['learning_objectives'] = []

                for item in destructure_list(l.frontmatter['learning_objectives']):
                    label, urls = item
                    if urls:
                        log.warning(f'Looks like the learning objectives have URLs but the database has no way to keep them.')
                    o = LearningObjective(
                            frontmatter=frontmatter,
                            label=label
                        )
                    o.save()
                    collector['learning_objectives'].append(o)
                    log.log(f'Learning objective for frontmatter {frontmatter.id} added:\n    {o.label}.')

            # frontmatter.Project
            elif model == Project:
                try:
                    if isinstance(l.frontmatter['projects'], str) and not is_exclusively_bullets(l.frontmatter['projects']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                        log.warning('Projects contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for projects.')
                    continue

                collector['projects'] = []
                for item in destructure_list(l.frontmatter['projects']):
                    comment, urls = item
                    o = Project()
                    o.comment = comment
                    for url in urls:
                        o.title, o.url = urls[0]
                    o.save()
                    collector['projects'].append(o)
                    if o.title == '':
                        log.log(f'Project added:\n    {o.url} (title missing, but comment starts with: {o.comment[:60]}...)')
                    else:
                        log.log(f'Project added:\n    {o.title} ({o.url})')
                    if len(urls) > 1:
                        all_urls = ", ".join([_[1] for _ in urls])
                        log.warning(f'The project above seems to contain had {len(urls)} URLs, but only the first one has been captured:\n    {all_urls}')
                frontmatter.projects.set(collector['projects'])
                log.log(f'Frontmatter {frontmatter.id} updated with {len(collector["projects"])} projects.')

            # frontmatter.Reading
            elif model == Reading:
                try:
                    if isinstance(l.frontmatter['readings'], str) and not is_exclusively_bullets(l.frontmatter['readings']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                        log.warning('Readings contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for readings.')
                    continue

                collector['frontmatter_readings'] = []
                if isinstance(l.frontmatter['readings'], str):
                    l.frontmatter['readings'] = get_list(l.frontmatter['readings']) # FIXME: #52 Remove dependencies on get_list for destructure_list

                for item in l.frontmatter['readings']:
                    md = '\n'.join(item).strip()
                    o = Reading()
                    o.comment = md
                    urls = get_markdown_hrefs(md)
                    for url in urls:
                        o.title, o.url = url[:2]
                        if len(urls) > 1: log.warning(f'One reading seems to contain more than one URL, but only one ({url}) is captured:\n    {md}')
                        continue
                    o.save()
                    collector['frontmatter_readings'].append(o)
                    log.log(f'Reading added:\n    {o.title}')
                frontmatter.readings.set(collector['frontmatter_readings'])
                log.log(f'Frontmatter {frontmatter.id} updated with {len(collector["frontmatter_readings"])} readings.')

            # frontmatter.Contributor
            elif model == Contributor:
                try:
                    if isinstance(l.frontmatter['contributors'], str) and not is_exclusively_bullets(l.frontmatter['contributors']): # FIXME: #50 Move into the dhri.utils.loader.Loader object and make them accessible as properties
                        log.warning('Contributors contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for contributors.')
                    continue

                collector['contributors'] = []
                for contributor in get_contributors(l.frontmatter['contributors']):
                    o = Contributor()
                    o.first_name, o.last_name, o.role, o.link = contributor
                    o.save()
                    collector['contributors'].append(o)
                    msg = f'Contributor added:\n    {o.full_name}'
                    if o.role != '': msg += f' ({o.role})'
                    log.log(msg)
                frontmatter.contributors.set(collector['contributors'])
                log.log(f'Frontmatter {frontmatter.id} updated with {len(collector)} contributors.')

            else:
                log.error(f'Have no way of processing {model} (for app `frontmatter`). The `populate` script must be adjusted accordingly.', kill=False)

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
