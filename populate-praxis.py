from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list
from dhri.utils.loader import Loader
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs

from dhri.backend import *
from dhri.models import *
from dhri.meta import reset_all, get_or_default


if __name__ == '__main__':


    # dev part - remove in production #############
    reset_all()
    AUTO_REPOS = [
            'command-line',
            'project-lab'
        ]
    AUTO_BRANCHES = [
            'v2.0-smorello-edits',
            'v2.0rhody-edits'
        ]
    ###############################################

    done = "n"

    all_objects = []

    iteration = 0

    while done == "n":

        iteration += 1

        repo = get_or_default(f'What is the repo name (assuming DHRI-Curriculum as username) or whole GitHub link you want to import?', AUTO_REPOS[iteration-1])

        if repo.startswith("https://github.com/"):
            pass
        else:
            repo = f"https://github.com/DHRI-Curriculum/{repo}"

        branch = get_or_default(f'What is the branch name you want to import?', AUTO_BRANCHES[iteration-1])

        l = Loader(repo, branch)

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
        dhri_log(f'Workshop object {workshop.name} added (ID {workshop.id}).')

        # Reset collector
        collector = {}

        ###### PRAXIS MODELS ####################################

        print(l.praxis)

        for model in l.praxis_models:
            if model == Praxis:
                praxis = Praxis(
                        workshop = workshop,
                    )
                try:
                    praxis.discussion_questions = l.praxis['discussion_questions']
                except:
                    dhri_warning(f"{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for discussion questions.")
                try:
                    praxis.next_steps = l.praxis['next_steps']
                except:
                    dhri_warning(f"{l.parent_repo}/{l.parent_branch} does not seem to have the theory-to-practice.md section for next steps.")
                praxis.save()
                dhri_log(f'Praxis object {praxis.id} added for workshop {workshop}.')

            elif model == Tutorial:
                if isinstance(l.praxis['tutorials'], str) and not is_exclusively_bullets(l.praxis['tutorials']):
                    dhri_warning("The Tutorials section contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
                
                collector['tutorials'] = []
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
                    dhri_log(f'Tutorial {o.id} added.')
                praxis.tutorials.set(collector['tutorials'])
                dhri_log(f'Praxis {praxis.id} updated with tutorials.')

            elif model == Reading:
                if isinstance(l.praxis['further_readings'], str) and not is_exclusively_bullets(l.praxis['further_readings']):
                    dhri_warning("Further readings contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")

                if isinstance(l.praxis['further_readings'], str):
                    l.praxis['further_readings'] = get_list(l.praxis['further_readings'])
                            
                collector['praxis_readings'] = []
                for item in l.praxis['further_readings']:
                    
                    title, _ = item # TODO: add field on reading for comment (and replace _)
                    o = Reading()
                    o.title = title
                    o.save()
                    collector['praxis_readings'].append(o)
                    dhri_log(f'Reading {o.id} added.')
                praxis.further_readings.set(collector['praxis_readings'])
                dhri_log(f'Praxis {praxis.id} updated with further readings.')

            else:
                print(f"Have no way of processing {model}. The `populate` script must be adjusted accordingly.")



        ###### FRONTMATTER MODELS ####################################

        for model in l.frontmatter_models:
            
            # frontmatter.Frontmatter
            if model == Frontmatter:
                frontmatter = Frontmatter(
                        workshop = workshop,
                        abstract = l.frontmatter['abstract'],
                        ethical_considerations = l.frontmatter['ethical_considerations'],
                        estimated_time = get_number(l.frontmatter['estimated_time']),
                    )
                frontmatter.save()
                dhri_log(f'Frontmatter object {frontmatter.id} added for workshop {workshop}.')

            # frontmatter.LearningObjective
            elif model == LearningObjective:
                if isinstance(l.frontmatter['learning_objectives'], str) and not is_exclusively_bullets(l.frontmatter['learning_objectives']):
                    dhri_warning("Learning objectives contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
                
                if isinstance(l.frontmatter['learning_objectives'], str):
                    l.frontmatter['learning_objectives'] = get_list(l.frontmatter['learning_objectives'])
                
                collector['learning_objectives'] = []
                for item in l.frontmatter['learning_objectives']:
                    label = "\n".join(item).strip()
                    o = LearningObjective(
                            frontmatter=frontmatter,
                            label=label
                        )
                    o.save()
                    collector['learning_objectives'].append(o)
                    dhri_log(f'Learning objective for frontmatter {frontmatter.id} added:\n    {o.label}.')
                
            # frontmatter.Project
            elif model == Project:
                if isinstance(l.frontmatter['projects'], str) and not is_exclusively_bullets(l.frontmatter['projects']):
                    dhri_warning("Projects contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
                
                collector['projects'] = []
                if isinstance(l.frontmatter['projects'], str):
                    l.frontmatter['projects'] = get_list(l.frontmatter['projects'])
                
                for item in l.frontmatter['projects']:
                    md = "\n".join(item).strip()
                    o = Project()
                    o.comment = md
                    hrefs = get_markdown_hrefs(md)
                    if hrefs:
                        o.title, o.url = hrefs[0]
                    o.save()
                    collector['projects'].append(o)
                    dhri_log(f'Project {o.title} added.')
                frontmatter.projects.set(collector['projects'])
                dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector["projects"])} projects.')

            # frontmatter.Reading
            elif model == Reading:
                if isinstance(l.frontmatter['readings'], str) and not is_exclusively_bullets(l.frontmatter['readings']):
                    dhri_warning("Readings contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
                
                collector['frontmatter_readings'] = []
                for item in l.frontmatter['readings']:
                    md = "\n".join(item).strip()
                    o = Reading()
                    o.comment = md
                    hrefs = get_markdown_hrefs(md)
                    if hrefs:
                        o.title, o.url = hrefs[0]
                    o.save()
                    collector['frontmatter_readings'].append(o)
                    dhri_log(f'Reading {o.title} added.')
                frontmatter.readings.set(collector['frontmatter_readings'])
                dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector["frontmatter_readings"])} readings.')

            # frontmatter.Contributor
            elif model == Contributor:
                if isinstance(l.frontmatter['contributors'], str) and not is_exclusively_bullets(l.frontmatter['contributors']):
                    dhri_warning("Contributors contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
                
                if isinstance(l.frontmatter['contributors'], str):
                    l.frontmatter['contributors'] = get_list(l.frontmatter['contributors'])
                
                collector['contributors'] = []
                for item in l.frontmatter['contributors']:
                    md = "\n".join(item).strip()
                    role = None
                    o = Contributor()
                    if ":" in md:
                        role, name = md.split(":")[0].strip(), " ".join(md.split(":")[1:]).strip()
                    else:
                        name = md
                    
                    first_name, last_name = name.split(" ")[0].strip(), " ".join(name.split(" ")[1:]).strip()
                    
                    if name == None or name.strip() == "" or name.lower().strip() == "none" or first_name == "none" or last_name == "none":
                        dhri_warning(f'Could not interpret name ("{name}") and chose to not insert the collaborators on the workshop {workshop.name}. Verify in admin tool later.')
                        continue
                    
                    first_name = get_or_default(f"Confirm {first_name} {last_name}'s first name. Type NO to skip contributor.", first_name)
                    if first_name == "NO":
                        dhri_warning(f"Skipping contributor {name}.")
                        continue
                    last_name = get_or_default(f"Confirm {first_name} {last_name}'s last name. Type NO to skip contributor.", last_name)
                    if last_name == "NO":
                        dhri_warning(f"Skipping contributor {name}.")
                        continue
                    role = get_or_default(f"Confirm {first_name} {last_name}'s role. Type NO to skip contributor.", role)
                    if role == "NO":
                        dhri_warning(f"Skipping contributor {name}.")
                        continue
                    o.first_name, o.last_name, o.role = first_name, last_name, role
                    o.save()
                    collector['contributors'].append(o)
                    dhri_log(f'Contributor {o.full_name} ({o.role}) added.')
                frontmatter.contributors.set(collector['contributors'])
                dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector)} contributors.')

            else:
                print(f"Have no way of processing {model} (for app `frontmatter`). The `populate` script must be adjusted accordingly.")

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

        done = get_or_default("Are you done? [y/N] ", done, color='red').lower()
        
    # Create fixtures.json
    all_objects_dict = json.loads(serializers.serialize('json', all_objects, ensure_ascii=False))

    print(all_objects_dict)
    from pathlib import Path
    Path('app/fixtures.json').write_text(json.dumps(all_objects_dict))

