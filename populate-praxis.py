from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets
from dhri.utils.loader import Loader

from dhri.backend import *
from dhri.models import *
from dhri.meta import reset_all

reset_all()



l = Loader(repo='https://github.com/DHRI-Curriculum/project-lab', branch='v2.0rhody-edits')



'''
l.frontmatter
l.praxis
l.assessment
'''


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

'''

for model in l.praxis_models:
    if model == Tutorial:
        for item in l.praxis['tutorials']:
            label, comment = item
            o = Tutorial()
            o.label = label
            o.comment = comment
            o.url = "url" # find url in label
            o.save()
            print(o)
    elif model == Reading:
        for item in l.praxis['further_readings']:
            title, _ = item # TODO: add field on reading for comment (and replace _)
            o = Reading()
            o.name = title
            o.save()
            print(o)
    elif model == Praxis:
        o = Praxis()
        o.discussion_questions = l.praxis['discussion_questions']
        o.next_steps = l.praxis['next_steps']
        o.save()
        print(o)
    else:
        print(f"Have no way of processing {model}. The `populate` script must be adjusted accordingly.")

    '''
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
    