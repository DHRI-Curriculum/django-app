from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets, get_list
from dhri.utils.loader import Loader
from dhri.utils.text import get_urls, get_number, get_markdown_hrefs

from dhri.backend import *
from dhri.models import *
from dhri.meta import reset_all, get_or_default


reset_all()

repo = 'https://github.com/DHRI-Curriculum/project-lab'
branch = 'v2.0rhody-edits'

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

'''
##### This will be left here because this is how we can process frontmatter ########

for model in l.frontmatter_models:
    if model == Contributor:
        for section in l.frontmatter_models[model]:
            print("***", section, "***")
            print(l.frontmatter[section])
        pass # process contributors
    elif model == Project:
        for section in l.frontmatter_models[model]:
            print("***", section, "***")
            print(l.frontmatter[section])
        pass # process contributors
    elif model == Reading:
        for section in l.frontmatter_models[model]:
            print("***", section, "***")
            print(l.frontmatter[section])
        pass # process contributors
    elif model == Frontmatter:
        for section in l.frontmatter_models[model]:
            print("***", section, "***")
            print(l.frontmatter[section])
        pass # process frontmatter
    else:
        print(f"Have no way of processing {model}. The `populate` script must be adjusted accordingly.")

    # I could also do things programmatically here...
    for section in l.praxis_models[model]:
        if isinstance(l.praxis[section], list):
            for entry in l.praxis[section]:
                print('we have an entry:', entry, model)
        elif isinstance(l.praxis[section], str):
            print('we have a string')
        else:
            print(f"Have no way of processing a section of type {type(l.praxis[section])}. The `populate` script must be adjusted accordingly.")
'''



###### PRAXIS MODELS ####################################

for model in l.praxis_models:
    if model == Praxis:
        praxis = Praxis(
                workshop = workshop,
                discussion_questions = l.praxis['discussion_questions'],
                next_steps = l.praxis['next_steps']
            )
        praxis.save()
        dhri_log(f'Praxis object {praxis.id} added for workshop {workshop}.')

    elif model == Tutorial:
        if isinstance(l.praxis['tutorials'], str) and not is_exclusively_bullets(l.praxis['tutorials']):
            dhri_warning("The Tutorials section contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
        
        collector = []
        for item in l.praxis['tutorials']:
            label, comment = item
            o = Tutorial()
            o.label = label
            o.comment = comment
            urls = get_urls(label)
            if urls:
                o.url = urls[0]
            o.save()
            collector.append(o)
            dhri_log(f'Tutorial {o.id} added.')
        praxis.tutorials.set(collector)
        dhri_log(f'Praxis {praxis.id} updated with tutorials.')

    elif model == Reading:
        if isinstance(l.praxis['further_readings'], str) and not is_exclusively_bullets(l.praxis['further_readings']):
            dhri_warning("Further readings contains not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
        
        collector = []
        for item in l.praxis['further_readings']:
            title, _ = item # TODO: add field on reading for comment (and replace _)
            o = Reading()
            o.title = title
            o.save()
            collector.append(o)
            dhri_log(f'Reading {o.id} added.')
        praxis.further_readings.set(collector)
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
                learning_objectives = l.frontmatter['learning_objectives'],
                ethical_considerations = l.frontmatter['ethical_considerations'],
                estimated_time = get_number(l.frontmatter['estimated_time']),
            )
        frontmatter.save()
        dhri_log(f'Frontmatter object {frontmatter.id} added for workshop {workshop}.')

    # frontmatter.Project
    elif model == Project:
        if isinstance(l.frontmatter['projects'], str) and not is_exclusively_bullets(l.frontmatter['projects']):
            dhri_warning("Projects contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
        
        collector = []
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
            collector.append(o)
            dhri_log(f'Project {o.title} added.')
        frontmatter.projects.set(collector)
        dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector)} projects.')

    # frontmatter.Reading
    elif model == Reading:
        if isinstance(l.frontmatter['readings'], str) and not is_exclusively_bullets(l.frontmatter['readings']):
            dhri_warning("Readings contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
        
        collector = []
        for item in l.frontmatter['readings']:
            md = "\n".join(item).strip()
            o = Reading()
            o.comment = md
            hrefs = get_markdown_hrefs(md)
            if hrefs:
                o.title, o.url = hrefs[0]
            o.save()
            collector.append(o)
            dhri_log(f'Reading {o.title} added.')
        frontmatter.readings.set(collector)
        dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector)} readings.')

    # frontmatter.Contributor
    elif model == Contributor:
        if isinstance(l.frontmatter['contributors'], str) and not is_exclusively_bullets(l.frontmatter['contributors']):
            dhri_warning("Contributors contain not exclusively bulletpoints. Will import as list, and exclude elements that are not bulletpoints.")
        
        if isinstance(l.frontmatter['contributors'], str):
            l.frontmatter['contributors'] = get_list(l.frontmatter['contributors'])
        
        collector = []
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
            collector.append(o)
            dhri_log(f'Contributor {o.full_name} ({o.role}) added.')
        frontmatter.contributors.set(collector)
        dhri_log(f'Frontmatter {frontmatter.id} updated with {len(collector)} contributors.')

    else:
        print(f"Have no way of processing {model} (for app `frontmatter`). The `populate` script must be adjusted accordingly.")

