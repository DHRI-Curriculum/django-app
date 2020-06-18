from dhri.markdown_parser import get_raw_content, split_md_into_sections_batch
from dhri.parser import normalize_data
from dhri.backend import *
from dhri.models import Question, Answer, QuestionType
from dhri.meta import reset_all
from dhri.utils.markdown import get_bulletpoints, is_exclusively_bullets
from dhri.utils.downloader import Downloader

reset_all()



d = Downloader(
        repo='https://github.com/DHRI-Curriculum/project-lab',
        branch='v2.0rhody-edits'
    )


print(d.frontmatter)
print(d.praxis)
print(d.assessment)

data = split_md_into_sections_batch({'frontmatter', 'theory-to-practice', 'assessment'}, data['content'])


praxis_data = normalize_data(data['theory-to-practice'], 'theory-to-practice')




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

has = test_praxis_sections(praxis_data)


for section in has:
    print(section)
    if isinstance(praxis_data[section], str) and is_exclusively_bullets(praxis_data[section]):
        bullets = get_bulletpoints(praxis_data[section])
        for bullet in bullets:
            print("\n".join(bullet))
