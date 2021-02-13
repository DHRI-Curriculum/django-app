from django.http.response import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
import random
from .models import Term


class TermList(ListView):
    model = Term

    def get(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('slug')

        if not self.slug:
            self.slug = 'A'
        
        if len(self.slug) > 1:
            t = Term.objects.filter(slug=self.slug)
            if t.count() == 1:
                url = reverse('glossary:term', kwargs={'slug': t[0].slug})
            else:
                slug = self.slug[:1].upper()
                url = reverse('glossary:letter', kwargs={'slug': slug})
            print(url)
            return HttpResponseRedirect(url)

        if self.get_queryset().count() == 0:
            return HttpResponseRedirect(reverse('glossary:index'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        allowed = [x.lower() for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        extra = {}
        for t in Term.objects.all().order_by('term'):
            if not t.term[0].lower() in allowed:
                done = False
                for i in range(2,len(t.term)):
                    if done: continue
                    if t.term[i-1:i].lower() in allowed:
                        if not t.term[i-1:i] in extra:
                            extra[t.term[i-1:i]] = []
                        extra[t.term[i-1:i]].append(t.term)
                        done = True
        
        if self.slug in extra.keys():
            for term in extra[self.slug]:
                objects = Term.objects.filter(term=term)
        try:
            return objects | Term.objects.filter(term__istartswith=self.slug)
        except:
            return Term.objects.filter(term__istartswith=self.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = self.slug
        if self.model.objects.count() > 4:
            context['random_items'] = random.sample(list(self.model.objects.all()), 4)
        return context


class TermDetail(DetailView):
    model = Term

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_slug'] = self.object.term[:1].upper()
        return context