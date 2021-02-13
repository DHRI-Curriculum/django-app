from django.http.request import HttpRequest
from django.views import View
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from glossary.models import Term
from insight.models import Insight
from install.models import Instruction, Software
from django.urls import reverse


class IndexRedirect(View):
    def get(self, request):
        return HttpResponseRedirect('/')


class TermRedirectView(View):
    def get(self, *args, **kwargs):
        terms = Term.objects.filter(slug__icontains=kwargs.get('slug'))
        if terms.count() == 1:
            url = reverse('glossary:term', kwargs={'slug': terms[0].slug})
            return HttpResponseRedirect(url)
        elif terms.count() == 0:
            return HttpResponseBadRequest('Term cannot be found.')
        else:
            response = f'''Ambivalent request. Did you mean any of these links (that all contain <em>{ kwargs.get("slug") }</em>):<ul>'''
            for term in terms:
                url = reverse('glossary:term', kwargs={'slug': term.slug})
                response += f'''<li><a href="{url}">{term}</a></li>'''
            response += '</ul>'
            return HttpResponse(response)


class InsightRedirectView(View):
    def get(self, *args, **kwargs):
        insights = Insight.objects.filter(slug__icontains=kwargs.get('slug'))
        if insights.count() == 1:
            url = reverse('insight:insight', kwargs={'slug': insights[0].slug})
            return HttpResponseRedirect(url)
        elif insights.count() == 0:
            return HttpResponseBadRequest('Insight cannot be found.')
        else:
            response = f'''Ambivalent request. Did you mean any of these links (that all contain <em>{ kwargs.get("slug") }</em>):<ul>'''
            for insight in insights:
                url = reverse('insight:insight', kwargs={'slug': insight.slug})
                response += f'''<li><a href="{url}">{insight}</a></li>'''
            response += '</ul>'
            return HttpResponse(response)



class InstallRedirectView(View):
    def get(self, request, *args, **kwargs):
        is_mac = 'mac' in self.request.META.get('HTTP_USER_AGENT', '').lower()
        is_windows = 'mac' in self.request.META.get('HTTP_USER_AGENT', '').lower()

        installs = Instruction.objects.filter(slug__icontains=kwargs.get('slug').lower())
        if installs.count() == 2:
            if is_mac:
                obj = installs.filter(software__operating_system='macOS')
            elif is_windows:
                obj = installs.filter(software__operating_system='Windows')
            else:
                return HttpResponseBadRequest(f'Installation cannot be found for your operating system.')
            obj = obj[0]
            url = reverse('install:installation', kwargs={'slug': obj.slug})
            return HttpResponseRedirect(url)
        elif installs.count() == 0:
            return HttpResponseBadRequest(f'Installation cannot be found { installs.count() }.')
        else:
            response = f'''Ambivalent request. Did you mean any of these links (that all contain <em>{ kwargs.get("slug") }</em>):<ul>'''
            for install in installs:
                url = reverse('install:installation', kwargs={'slug': install.slug})
                response += f'''<li><a href="{url}">{install.software}</a></li>'''
            response += '</ul>'
            return HttpResponse(response)
