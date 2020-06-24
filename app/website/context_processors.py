# from workshop.models import Workshop

def add_to_all_contexts(request):
    context_data = dict()

    user_agent = request.META['HTTP_USER_AGENT'].lower()
    context_data['user_agent'] = user_agent
    context_data['is_ie'] = ('trident' in user_agent) or ('msie' in user_agent)
    # context_data['all_workshops'] = Workshop.objects.all().count()
    return context_data