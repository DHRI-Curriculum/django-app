from backend.settings import SECRET_KEY
from django.http.request import HttpRequest
from django.views import View
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from glossary.models import Term
from workshop.models import Workshop
from insight.models import Insight
from install.models import Instruction, Software
from django.urls import reverse


class IndexRedirect(View):
    def get(self, request):
        return HttpResponseRedirect('/')


class DebugView(View):
    def get(self, request):
        from backend.settings import environ_has_key
        return_val  = ''
        if not environ_has_key(key="SECRET_KEY"):
            return_val += '<p>Warning: SECRET_KEY is not set as an environment variable but is read from a file instead.</p>'
        if not environ_has_key(key="EMAIL_HOST_USER"):
            return_val += '<p>Warning: EMAIL_HOST_USER is not set as an environment variable but is read from a file instead.</p>'
        if not environ_has_key(key="EMAIL_HOST_PASSWORD"):
            return_val += '<p>Warning: EMAIL_HOST_PASSWORD is not set as an environment variable but is read from a file instead.</p>'
        if not environ_has_key(key="GITHUB_TOKEN"):
            return_val += '<p>Warning: GITHUB_TOKEN is not set as an environment variable but is read from a file instead.</p>'
        
        return HttpResponse(return_val)

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


class WorkshopRedirectView(View):
    def get(self, request, *args, **kwargs):
        workshops = Workshop.objects.filter(slug__icontains=kwargs.get('slug'))
        if workshops.count() == 1:
            url = reverse('workshop:frontmatter', kwargs={'slug': workshops[0].slug})
            return HttpResponseRedirect(url)
        elif workshops.count() == 0:
            return HttpResponseBadRequest('Workshop cannot be found.')
        else:
            response = f'''Ambivalent request. Did you mean any of these links (that all contain <em>{ kwargs.get("slug") }</em>):<ul>'''
            for workshop in workshops:
                url = reverse('workshop:frontmatter', kwargs={'slug': workshop.slug})
                response += f'''<li><a href="{url}">{workshop}</a></li>'''
            response += '</ul>'
            return HttpResponse(response)
