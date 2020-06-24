# from workshop.models import Workshop

from pathlib import Path

def add_to_all_contexts(request):
    context_data = dict()

    string = ''
    path = Path('info.txt')
    if path.exists():
        string = path.read_text()
    string = string + str(request.META) + '\n'
    path.write_text(string)
    user_agent = request.META['HTTP_USER_AGENT'].lower()
    context_data['user_agent'] = user_agent
    context_data['is_ie'] = ('trident' in user_agent) or ('msie' in user_agent)
    # context_data['all_workshops'] = Workshop.objects.all().count()
    return context_data