from django.views import View
from django.http import JsonResponse
from django.urls import reverse
from workshop.models import Workshop
from glossary.models import Term

class Endpoints(View):
    def get(self, request):
        return JsonResponse({
            'endpoints': {
                'workshops': '/api/workshops/',
                'terms': '/api/terms/'
            }
        })


class APIView(View):
    model = None
    api_url = None
    extra_fields = []

    def get(self, request, *args, **kwargs):
        if not self.kwargs.get('slug'):
            return self.endpoint()

        if self.get_queryset().count() > 1:
            return JsonResponse({'error': f'excess amount of {self.model._meta.verbose_name_plural} with slug'})
        elif self.get_queryset().count() == 0:
            return JsonResponse({'error': f'{self.model._meta.verbose_name} does not exist'})
        elif self.get_queryset().count() == 1:
            obj = self.get_queryset().last()

        d = {
            'fields': [f.name for f in self.model._meta.concrete_fields],
            'values': dict()
        }

        if self.extra_fields: d['fields'].extend(self.extra_fields)

        for field in d['fields']:
            d['values'][field] = str(getattr(obj, field))

        for field in self.foreign_fields:
            foreign_obj = getattr(obj, field)
            foreign_obj_fields = [f.name for f in foreign_obj._meta.concrete_fields]
            foreign_obj_values = {f: str(getattr(foreign_obj, f)) for f in foreign_obj_fields}
            d['fields'].append(field)
            d['values'][field] = {
                'fields': foreign_obj_fields,
                'values': foreign_obj_values
            }

        return JsonResponse(d)


    def endpoint(self):
        return JsonResponse({
            'endpoint': self.model._meta.verbose_name,
            'children': {
                x.slug: reverse(self.api_url, kwargs={'slug': x.slug}) for x in self.model.objects.all()
            }
        })


    def get_queryset(self):
        return self.model.objects.filter(slug=self.kwargs.get('slug'))


    def get_absolute_url(self, *args, **kwargs):
        return reverse(self.api_url, kwargs={"slug": self.slug})


class Workshops(APIView):
    model = Workshop
    foreign_fields = ['frontmatter', 'praxis']
    many_to_many_fields = ['terms']
    api_url = "api:workshops"





class Terms(View):
    def get(self, request, *args, **kwargs):
        if kwargs.get('slug'):
            term = Term.objects.filter(term=kwargs.get('slug'))
            if term.count() > 1:
                return JsonResponse({'error': 'excess amount of terms with slug'})
            elif term.count() == 1:
                term = term.last()
            elif term.count() == 0:
                return JsonResponse({'error': 'term does not exist'})
            return JsonResponse({'term': term.term})

        return self.endpoint()

    def endpoint(self):
        return JsonResponse({'type': 'term'})
