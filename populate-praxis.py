from dhri.markdown_parser import get_raw_content, split_md_into_sections_batch
from dhri.parser import normalize_data
from dhri.backend import *
from dhri.models import Question, Answer, QuestionType
from dhri.meta import reset_all
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets
from dhri.utils.loader import Loader

reset_all()



l = Loader(
        repo='https://github.com/DHRI-Curriculum/project-lab',
        branch='v2.0rhody-edits'
    )



'''
print(l.frontmatter)
print(l.praxis)
print(l.assessment)
'''


def test_praxis_sections(
        praxis_data,
        sections={
            'tutorials',
            'discussion_questions',
            'further_readings',
            'further_projects',
            'next_steps'
        }) -> list:
    has = []
    for section in sections:
        try:
            praxis_data[section]
            has.append(section)
        except KeyError:
            pass
    return(has)

has = test_praxis_sections(l.praxis)


for section in has:
    print(section)
    if isinstance(l.praxis[section], str) and is_exclusively_bullets(l.praxis[section]):
        bullets = get_bulletpoints(l.praxis[section])
        for bullet in bullets:
            print("\n".join(bullet))
