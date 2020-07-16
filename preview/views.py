from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, HttpResponse
import requests
from backend.models import Workshop
from backend.dhri.markdown import split_into_sections
from backend.dhri.loader import _normalize_data, as_list, ContributorParser
from backend.dhri.parse_lesson import LessonParser, md_to_html_parser


BASE_URL = 'https://raw.githubusercontent.com/'
FILES = {
    'frontmatter': 'frontmatter.md',
    'praxis': 'theory-to-practice.md',
    'lessons': 'lessons.md',
}


@staff_member_required
def menu(request):
    return render(request, 'preview/menu.html', {'workshops': Workshop.objects.all()})

@staff_member_required
def repository(request, repo=None):
    payload = dict()
    payload['workshop'] = get_object_or_404(Workshop, slug=repo)
    payload['files'] = FILES
    payload['BASE_URL'] = BASE_URL
    return render(request, 'preview/repository.html', payload)

def get_from_url(url:str, type:str, workshop=None): # type = 'frontmatter' | 'theory-to-practice' | 'lessons'
    payload = dict()

    r = requests.get(url)

    # Generate markdown & HTML
    payload['markdown_text'] = r.text
    payload['html_text'] = md_to_html_parser.convert(r.text)

    if type == 'frontmatter' or type == 'theory-to-practice':
        # Split sections
        payload['sections'] = split_into_sections(r.text)
        payload['sections'] = _normalize_data(payload['sections'], type)
        if type == 'frontmatter':
            # Emulate fixings in `loader.py`
            if 'learning_objectives' in payload['sections'].keys(): payload['sections']['learning_objectives'] = as_list(payload['sections']['learning_objectives'])
            if 'readings' in payload['sections'].keys(): payload['sections']['readings'] = as_list(payload['sections']['readings'])
            if 'projects' in payload['sections'].keys(): payload['sections']['projects'] = as_list(payload['sections']['projects'])
            if 'ethical_considerations' in payload['sections'].keys(): payload['sections']['ethical_considerations'] = as_list(payload['sections']['ethical_considerations'])
            if 'contributors' in payload['sections'].keys(): payload['sections']['contributors'] = ContributorParser(payload['sections']['contributors']).data
        elif type == 'theory-to-practice':
            # Emulate fixings in `loader.py`
            if 'discussion_questions' in payload['sections'].keys(): payload['sections']['discussion_questions'] = as_list(payload['sections']['discussion_questions'])
            if 'tutorials' in payload['sections'].keys(): payload['sections']['tutorials'] = as_list(payload['sections']['tutorials'])
            if 'further_readings' in payload['sections'].keys(): payload['sections']['further_readings'] = as_list(payload['sections']['further_readings'])
            if 'next_steps' in payload['sections'].keys(): payload['sections']['next_steps'] = as_list(payload['sections']['next_steps'])

    elif type == 'lessons':
        import re
        from backend.dhri.loader import Loader
        payload['markdown_text'] = re.sub(r'', '', payload['markdown_text'])
        l = Loader(repo=f'https://github.com/{workshop.parent_repo}', branch=workshop.parent_branch)
        payload['sections'] = l.lessons
        payload['sections_html'] = l.lessons_html
        for i, section in enumerate(payload['sections']):
            payload['sections'][i]['text'] = payload['sections'][i]['text'].replace('\n', '<br />')

    return(payload)

@staff_member_required
def frontmatter(request, repo=None):
    workshop = get_object_or_404(Workshop, slug=repo)

    url = f'{BASE_URL}{workshop.parent_repo}/{workshop.parent_branch}/{ FILES["frontmatter"] }'
    _ = get_from_url(url=url, type='frontmatter')

    payload = dict()
    payload['workshop'] = workshop
    payload['files'] = FILES
    payload['type'] = 'frontmatter'
    payload['markdown_text'] = _.get('markdown_text')
    payload['html_text'] = _.get('html_text')
    payload['sections'] = _.get('sections')

    return render(request, 'preview/preview.html', payload)

@staff_member_required
def praxis(request, repo=None):
    workshop = get_object_or_404(Workshop, slug=repo)
    url = f'{BASE_URL}{workshop.parent_repo}/{workshop.parent_branch}/{ FILES["praxis"] }'
    _ = get_from_url(url=url, type='theory-to-practice')

    payload = dict()
    payload['workshop'] = workshop
    payload['files'] = FILES
    payload['type'] = 'praxis'
    payload['markdown_text'] = _.get('markdown_text')
    payload['html_text'] = _.get('html_text')
    payload['sections'] = _.get('sections')

    return render(request, 'preview/preview.html', payload)

@staff_member_required
def lessons(request, repo=None):
    workshop = get_object_or_404(Workshop, slug=repo)
    url = f'{BASE_URL}{workshop.parent_repo}/{workshop.parent_branch}/{ FILES["lessons"] }'
    _ = get_from_url(url=url, type='lessons', workshop=workshop)

    payload = dict()
    payload['workshop'] = workshop
    payload['files'] = FILES
    payload['type'] = 'lessons'
    payload['markdown_text'] = _.get('markdown_text')
    payload['html_text'] = _.get('html_text')
    payload['sections'] = zip(_.get('sections'), _.get('sections_html'))

    return render(request, 'preview/preview.html', payload)
