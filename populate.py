from dhri.django import django
from dhri.django.models import *
from dhri.interaction import Logger, get_or_default
from dhri.settings import AUTO_PROCESS, FIXTURE_PATH
from dhri.utils.exceptions import UnresolvedNameOrBranch
from dhri.utils.loader import Loader
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs

# dev part - remove in production #############
from dhri.meta import reset_all
reset_all()
###############################################

if __name__ == '__main__':


    log = Logger(name="populate")

    iteration, all_objects, done = 0, [], 'n'
    while done == 'n':

        iteration += 1

        try:
            repo, branch = AUTO_PROCESS[iteration-1]
        except:
            repo, branch = '', ''

        repo = get_or_default(f'What is the repo name (assuming DHRI-Curriculum as username) or whole GitHub link you want to import?', repo)
        if repo == '':
            log.error('No repository name, exiting...', kill=None)
            done = 'YES'
            continue

        branch = get_or_default(f'What is the branch name you want to import?', branch)
        if branch == '':
            log.error('No branch name, exiting...', kill=None)
            done = 'YES'
            continue

        if not repo.startswith('https://github.com/'):
            repo = f'https://github.com/DHRI-Curriculum/{repo}'


        ###### Load in data from GitHub (handled by dhri.utils.loader.Loader)

        l = Loader(repo, branch)


        ###### Setup empty and standard variables

        collector = {}

        repo = get_or_default('Repository', l.meta['repo_name'])
        name = get_or_default('Workshop name', repo.replace('-', ' ').title())


        ###### WORKSHOP MODELS ####################################

        workshop = Workshop(
                name = name,
                parent_backend = l.parent_backend,
                parent_repo = l.parent_repo,
                parent_branch = l.parent_branch
            )
        workshop.save()
        log.log(f'Workshop object {workshop.name} added (ID {workshop.id}).')


        ###### PRAXIS MODELS ####################################

        for model in l.praxis_models:
            if model == Praxis:
                praxis = Praxis(
                        workshop = workshop,
                    )
                try:
                    praxis.discussion_questions = l.praxis['discussion_questions']
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for discussion questions.')
                try:
                    praxis.next_steps = l.praxis['next_steps']
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for next steps.')
                praxis.save()
                log.log(f'Praxis object {praxis.id} added for workshop {workshop}.')

            elif model == Tutorial:
                try:
                  if isinstance(l.praxis['tutorials'], str) and not is_exclusively_bullets(l.praxis['tutorials']):
                      log.warning('The Tutorials section contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for tutorials.')
                    continue

                collector['tutorials'] = []
                if isinstance(l.praxis['tutorials'], str):
                    l.praxis['tutorials'] = get_list(l.praxis['tutorials'])

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
                  if isinstance(l.praxis['further_readings'], str) and not is_exclusively_bullets(l.praxis['further_readings']):
                      log.warning('Further readings contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for further readings.')
                    continue

                collector['praxis_readings'] = []
                if isinstance(l.praxis['further_readings'], str):
                    l.praxis['further_readings'] = get_list(l.praxis['further_readings'])

                for item in l.praxis['further_readings']:
                    title, _ = item # TODO: add field on reading for comment (and replace _)
                    o = Reading()
                    o.title = title
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
                    frontmatter.abstract = l.frontmatter['abstract']
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for abstract.', color='red') # red because it is a significant thing to be missing

                try:
                    frontmatter.ethical_considerations = l.frontmatter['ethical_considerations']
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for ethical considerations.')

                try:
                    frontmatter.estimated_time = get_number(l.frontmatter['estimated_time'])
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for estimated time.')

                frontmatter.save()
                log.log(f'Frontmatter object {frontmatter.id} added for workshop {workshop}.')

            # frontmatter.LearningObjective
            elif model == LearningObjective:
                try:
                  if isinstance(l.frontmatter['learning_objectives'], str) and not is_exclusively_bullets(l.frontmatter['learning_objectives']):
                      log.warning('Learning objectives contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for learning objectives.')
                    continue

                collector['learning_objectives'] = []
                if isinstance(l.frontmatter['learning_objectives'], str):
                    l.frontmatter['learning_objectives'] = get_list(l.frontmatter['learning_objectives'])

                for item in l.frontmatter['learning_objectives']:
                    label = '\n'.join(item).strip()
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
                    if isinstance(l.frontmatter['projects'], str) and not is_exclusively_bullets(l.frontmatter['projects']):
                        log.warning('Projects contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for projects.')
                    continue

                collector['projects'] = []
                if isinstance(l.frontmatter['projects'], str):
                    l.frontmatter['projects'] = get_list(l.frontmatter['projects'])

                print(l.frontmatter['projects'])

                for item in l.frontmatter['projects']:
                    md = '\n'.join(item).strip()
                    o = Project()
                    o.comment = md
                    urls = get_markdown_hrefs(md)
                    for url in urls:
                        print(url)
                        o.title, o.url = url[:2]
                        if len(urls) > 1: log.warning(f'One project seems to contain more than one URL, but only one ({url}) is captured:\n    {md}')
                        continue
                    o.save()
                    collector['projects'].append(o)
                    log.log(f'Project added:\n    {o.title}')
                frontmatter.projects.set(collector['projects'])
                log.log(f'Frontmatter {frontmatter.id} updated with {len(collector["projects"])} projects.')

            # frontmatter.Reading
            elif model == Reading:
                try:
                    if isinstance(l.frontmatter['readings'], str) and not is_exclusively_bullets(l.frontmatter['readings']):
                        log.warning('Readings contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for readings.')
                    continue

                collector['frontmatter_readings'] = []
                if isinstance(l.frontmatter['readings'], str):
                    l.frontmatter['readings'] = get_list(l.frontmatter['readings'])

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
                    if isinstance(l.frontmatter['contributors'], str) and not is_exclusively_bullets(l.frontmatter['contributors']):
                        log.warning('Contributors contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.')
                except KeyError:
                    log.warning(f'{l.parent_repo}/{l.parent_branch} does not seem to have the frontmatter.md section for contributors.')
                    continue

                if isinstance(l.frontmatter['contributors'], str):
                    l.frontmatter['contributors'] = get_list(l.frontmatter['contributors'])

                collector['contributors'] = []
                for item in l.frontmatter['contributors']:
                    md = '\n'.join(item).strip()
                    role = None
                    o = Contributor()
                    if ':' in md:
                        role, name = md.split(':')[0].strip(), ' '.join(md.split(':')[1:]).strip()
                    else:
                        name = md

                    first_name, last_name = name.split(' ')[0].strip(), ' '.join(name.split(' ')[1:]).strip()

                    if name == None or name.strip() == '' or name.lower().strip() == 'none' or first_name == 'none' or last_name == 'none':
                        log.warning(f'Could not interpret name ("{name}") and will not insert the collaborators on the workshop {workshop.name}. Verify in admin tool later.')
                        continue

                    first_name = get_or_default(f'Confirm {first_name} {last_name}\'s first name. Type NO to skip contributor.', first_name)
                    if first_name.lower() == 'no':
                        log.warning(f'Skipping contributor {name}.')
                        continue

                    last_name = get_or_default(f'Confirm {first_name} {last_name}\'s last name. Type NO to skip contributor.', last_name)
                    if last_name.lower() == 'no':
                        log.warning(f'Skipping contributor {name}.')
                        continue

                    role = get_or_default(f'Confirm {first_name} {last_name}\'s role. Type NO to skip contributor.', role)
                    if role == 'NO':
                        log.warning(f'Skipping contributor {name}.')
                        continue
                    elif role == 'None':
                        role = None
                    o.first_name, o.last_name, o.role = first_name, last_name, role
                    o.save()
                    collector['contributors'].append(o)
                    log.log(f'Contributor added:\n    {o.full_name} ({o.role})')
                frontmatter.contributors.set(collector['contributors'])
                log.log(f'Frontmatter {frontmatter.id} updated with {len(collector)} contributors.')

            else:
                log.error(f'Have no way of processing {model} (for app `frontmatter`). The `populate` script must be adjusted accordingly.', kill=False)

        # Create fixtures.json
        import json
        from django.core import serializers

        workshop_dict = json.loads(serializers.serialize('json', [workshop], ensure_ascii=False))[0]
        workshop_dict['fields'].pop('created')
        workshop_dict['fields'].pop('updated')

        frontmatter_dict = json.loads(serializers.serialize('json', [frontmatter], ensure_ascii=False))[0]
        praxis_dict = json.loads(serializers.serialize('json', [praxis], ensure_ascii=False))[0]

        all_objects.extend([workshop, frontmatter, praxis])
        for _ in collector.values():
            all_objects.extend([x for x in _])

        if iteration == len(AUTO_PROCESS):
          done = 'y'
          msg = 'Are you done? [Y/n] '
        else:
          done = 'n'
          msg = 'Are you done? [y/N] '
        done = get_or_default(msg, done, color='red').lower()

    log.log(f'Generating fixtures file for Django...')
    # Create fixtures.json
    all_objects_dict = json.loads(serializers.serialize('json', all_objects, ensure_ascii=False))

    from pathlib import Path
    Path(FIXTURE_PATH).write_text(json.dumps(all_objects_dict))
    log.log(f'Fixture file generated: {FIXTURE_PATH}')
