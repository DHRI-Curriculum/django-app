from backend.settings import SECRET_KEY
from django.http.request import HttpRequest
from django.views import View
from django.http.response import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render
from glossary.models import Term
from workshop.models import Workshop
from insight.models import Insight
from install.models import Instructions, Software
from django.urls import reverse


class IndexRedirect(View):
    def get(self, request):
        return HttpResponseRedirect("/")


class DebugView(View):
    def get(self, request):
        from backend.settings import environ_has_key

        return_val = ""
        if not environ_has_key(key="SECRET_KEY"):
            return_val += "<p>Warning: SECRET_KEY is not set as an environment variable but is read from a file instead.</p>"
        if not environ_has_key(key="EMAIL_HOST_USER"):
            return_val += "<p>Warning: EMAIL_HOST_USER is not set as an environment variable but is read from a file instead.</p>"
        if not environ_has_key(key="EMAIL_HOST_PASSWORD"):
            return_val += "<p>Warning: EMAIL_HOST_PASSWORD is not set as an environment variable but is read from a file instead.</p>"
        if not environ_has_key(key="GITHUB_TOKEN"):
            return_val += "<p>Warning: GITHUB_TOKEN is not set as an environment variable but is read from a file instead.</p>"

        return HttpResponse(return_val)


def get_options(slug):
    options = []
    for i in range(1, len(slug)):
        options.append(slug[:i])
    options.reverse()
    return options


def find_options(options=[], obj=None):
    for option in options:
        search = obj.objects.filter(slug__icontains=option)
        if search.count():
            return search
    return None


class TermRedirectView(View):
    def get(self, request, *args, **kwargs):
        terms = Term.objects.filter(slug__icontains=kwargs.get("slug"))
        if terms.count() == 1:
            url = reverse("glossary:term", kwargs={"slug": terms[0].slug})
            return HttpResponseRedirect(url)
        elif terms.count() == 0:
            options = get_options(kwargs.get("slug"))
            found_option = find_options(options, Term)
            if found_option:
                if found_option.count() == 1:
                    url = reverse(
                        "glossary:term", kwargs={"slug": found_option[0].slug}
                    )
                    return HttpResponseRedirect(url)
                else:
                    return render(
                        request,
                        "shortcuts/ambivalent-term.html",
                        {"terms": found_option},
                    )
            raise Http404(f"Cannot find term matching {kwargs.get('slug')}.")
        else:
            return render(request, "shortcuts/ambivalent-term.html", {"terms": terms})


class InsightRedirectView(View):
    def get(self, request, *args, **kwargs):
        insights = Insight.objects.filter(slug__icontains=kwargs.get("slug"))
        if insights.count() == 1:
            url = reverse("insight:insight", kwargs={"slug": insights[0].slug})
            return HttpResponseRedirect(url)
        elif insights.count() == 0:
            raise Http404(f"Cannot find insight matching {kwargs.get('slug')}.")
        else:
            return render(
                request, "shortcuts/ambivalent-insight.html", {"insights": insights}
            )


class InstallRedirectView(View):
    def get(self, request, *args, **kwargs):
        software = Software.objects.filter(slug__icontains=kwargs.get("slug").lower())
        if software.count() == 1:
            url = reverse("install:software", kwargs={"slug": software[0].slug})
            return HttpResponseRedirect(url)
        elif software.count() == 0:
            raise Http404(
                f"Cannot find installation instructions for {kwargs.get('slug')}."
            )
        else:
            return render(
                request, "shortcuts/ambivalent-software.html", {"softwares": software}
            )


class WorkshopRedirectView(View):
    def get(self, request, *args, **kwargs):
        workshops = Workshop.objects.filter(slug__icontains=kwargs.get("slug"))
        if workshops.count() == 1:
            if kwargs.get("praxis") == "theory-to-practice":
                pattern = "workshop:praxis"
            else:
                pattern = "workshop:frontmatter"
            url = reverse(pattern, kwargs={"slug": workshops[0].slug})
            return HttpResponseRedirect(url)
        elif workshops.count() == 0:
            raise Http404(f"Cannot find workshop matching {kwargs.get('slug')}.")
        else:
            return render(
                request, "shortcuts/ambivalent-workshop.html", {"workshops": workshops}
            )
