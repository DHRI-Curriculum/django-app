from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings

from insight.models import Insight
from workshop.models import Workshop
from install.models import Instruction


register = template.Library()


def get_all_objects():
    return {
        'insights': Insight.objects.all(),
        'workshops': Workshop.objects.all(),
        'installations': Instruction.objects.all()
    }

@register.simple_tag(takes_context=True)
def main_navigation(context):
    obj = get_all_objects()

    html = f'''
<nav class="navbar navbar-expand-sm navbar-light bg-primary">
  <div class="container-fluid d-none d-sm-flex justify-content-between">
    <a class="navbar-brand" href="{reverse('website:index')}">
        <img src="{settings.STATIC_URL}website/images/logo.png" width="50" height="50" alt="#TODO">
    </a>
    <div class="">
        <div class="ml-auto collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto mb-2 mb-lg-0">
                <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allWorkshops" aria-controls="allWorkshops" aria-expanded="false" aria-label="Toggle all workshop navigation">Workshops</a></li>
                <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInstallations" aria-controls="allInstallations" aria-expanded="false" aria-label="Toggle all installation navigation">Installations</a></li>
                <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInsights" aria-controls="allInsights" aria-expanded="false" aria-label="Toggle all installation navigation">Insights</a></li>
                <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/library/">Library</a></li>
                <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/terms/">Terms</a></li>
            </ul>
        </div>
    </div>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
  </div>

  <div class="container-fluid d-flex d-sm-none align-items-start">
      <a class="navbar-brand" href="{reverse('website:index')}">
          <img src="{settings.STATIC_URL}website/images/logo.png" width="150" height="150" alt="#TODO">
      </a>
      <div class="">
          <ul class="navbar-nav flex-column">
              <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/library/">Library</a></li>
              <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/terms/">Terms</a></li>
          </ul>
      </div>
  </div>
  <div class="container-fluid d-flex flex-row d-sm-none mt-4 border-top pt-2 border-dark">
      <ul class="navbar-nav flex-row">
          <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allWorkshops" aria-controls="allWorkshops" aria-expanded="false" aria-label="Toggle all workshop navigation">Workshops</a></li>
          <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInstallations" aria-controls="allInstallations" aria-expanded="false" aria-label="Toggle all installation navigation">Installations</a></li>
          <li><a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInsights" aria-controls="allInsights" aria-expanded="false" aria-label="Toggle all installation navigation">Insights</a></li>
      </ul>
  </div>
</nav>
    '''
    #return mark_safe(html)
    """
    html = f'''
    <div class="d-flex flex-row align-items-center p-3 px-4 bg-primary text-light">
        <p class="my-0 mb-0 mr-auto font-weight-normal no-touch">
            <a href="{reverse('website:index')}" class="text-light text-decoration-none">
                <img src="{settings.STATIC_URL}website/images/logo.png" width="50" height="50" alt="" class="mr-2">
                <span class="d-inline-block"><strong>Curriculum</strong> | DHRI</span>
            </a>
        </p>
        <nav class="my-md-0 zen-hideaway navbar navbar-expand-md" id="website-wide-nav">
            <a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allWorkshops" data-parent="#website-wide-nav" aria-controls="allWorkshops" aria-expanded="false" aria-label="Toggle all workshop navigation">Workshops</a>
            <a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInstallations" data-parent="#website-wide-nav" aria-controls="allInstallations" aria-expanded="false" aria-label="Toggle all installation navigation">Installations</a>
            <a class="d-inline-flex align-items-center p-2 text-light text-decoration-none workshop-button collapsed" style="cursor:pointer;" data-toggle="collapse" data-target="#allInsights" data-parent="#website-wide-nav" aria-controls="allInsights" aria-expanded="false" aria-label="Toggle all installation navigation">Insights</a>
            <a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/library/">Library</a>
            <a class="d-inline-flex align-items-center p-2 text-light text-decoration-none" href="/terms/">Terms</a>
            <!--<a class="text-nowrap p-2 text-light text-decoration-none" href="http://www.dhinstitutes.org">Digital Humanities Research Institute</a>-->
        </nav>
    </div>'''

    """
    #### Start mini menus
    # html += '<div id="mini-menus">'

    # Workshops mini menu
    html += '''<div class="collapse row pt-0 pb-5 px-4 bg-primary" id="allWorkshops"><div class="col-12 my-3"><h5 class="text-white h4">Workshops</h5></div>'''
    for workshop in obj['workshops']:
        html += '<div class="col-12 col-sm-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
        if workshop.image:
            html += f'''<a href="{ reverse('workshop:frontmatter', kwargs={'slug':workshop.slug}) }" class="stretched-link"><img src="/{ workshop.image }" class="card-img-top" alt="{ workshop.name }"></a>'''
        else:
            html += f'''<div class="card-body">
                            <h5 class="card-title m-0 bolder"><a href="{ reverse('workshop:frontmatter', kwargs={'slug':workshop.slug}) }" class="stretched-link">{ workshop.name }</a></h5>
                        </div>'''
        html += '</div></div>'
    html += '</div>'

    # Installations mini menu
    html += '''<div class="collapse row pt-0 pb-5 px-4 bg-primary" id="allInstallations"><div class="col-12 my-3"><h5 class="text-white h4">Installations</h5></div>'''
    for installation in obj['installations']:
        html += '<div class="col-12 col-sm-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
        if installation.image:
            html += f'''<a href="{ reverse('install:installation', kwargs={'slug':installation.slug}) }" class="stretched-link"><img src="/{ installation.image }" class="card-img-top" alt="{ installation.software.software }"></a>'''
        else:
            html += f'''<div class="card-body">
                            <h5 class="card-title m-0 bolder"><a href="{ reverse('install:installation', kwargs={'slug':installation.slug}) }" class="stretched-link">{ installation.software.software }</a></h5>
                        </div>'''
        html += '</div></div>'
    html += '</div>'

    # Insights mini menu
    html += '''<div class="collapse row pt-0 pb-5 px-4 bg-primary" id="allInsights"><div class="col-12 my-3"><h5 class="text-white h4">Insights</h5></div>'''
    for insight in obj['insights']:
        html += '<div class="col-12 col-sm-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
        html += f'''<div class="card-body">
                        <h5 class="card-title m-0 bolder"><a href="{ reverse('insight:insight', kwargs={'slug':insight.slug}) }" class="stretched-link">{ insight.title }</a></h5>
                    </div>'''
        html += '</div></div>'
        pass
    html += '</div>'

    #### End mini menus
    # html += '</div>'

    return mark_safe(html)