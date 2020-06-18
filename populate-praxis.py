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

