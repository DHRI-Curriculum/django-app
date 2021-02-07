from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView


from .models import Resource


payload = dict()


def get_all_categories():
    return {x[1]: reverse('resource:category', kwargs={'category': x[0]}) for x in Resource.CATEGORY_CHOICES_PLURAL}


class Index(ListView):
    template_name = 'resource/index.html'

    def get_queryset(self):
        return Resource.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readings'] = Resource.objects.filter(category=Resource.READING).order_by('?')[:3]
        context['tutorials'] = Resource.objects.filter(category=Resource.TUTORIAL).order_by('?')[:3]
        context['projects'] = Resource.objects.filter(category=Resource.PROJECT).order_by('?')[:3]
        context['all_categories'] = get_all_categories()
        return context

def lazyload(request, category=Resource.UNCATEGORIZED):
    print(request.headers)
    page = request.headers.get('page')
    resources = Resource.objects.filter(category=category).order_by('title')
    paginator = Paginator(resources, 3)
    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(2)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)

    projects_html = loader.render_to_string(
        'resource/fragments/resource_objects.html',
        {'resources': resources}
    )
    output_data = {'html': projects_html, 'has_next': resources.has_next()}
    return JsonResponse(output_data)


class Category(ListView):
    template_name = 'resource/category_list.html'
    paginate_by = 10

    def get_category(self, plural=False):
        if plural:
            source = Resource.CATEGORY_CHOICES_PLURAL
        else:
            source = Resource.CATEGORY_CHOICES
        if self.kwargs.get('category') in [x[0] for x in source]:
            return [x for x in source if x[0] == self.kwargs.get('category')][0]
        return False

    def get_queryset(self):
        category = self.get_category()
        if category:
            return Resource.objects.filter(category=category[0]).order_by('title')
        else:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category(plural=True)[1]
        context['all_categories'] = get_all_categories()
        return context
