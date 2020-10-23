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
        'insights': Insight.objects.all().order_by('title'),
        'workshops': Workshop.objects.all().order_by('name'),
        'installations': Instruction.objects.all().order_by('software__operating_system')
    }

@register.simple_tag(takes_context=True)
def main_navigation(context):
    obj = get_all_objects()

    html = f'''
<nav class="navbar navbar-expand-sm navbar-light bg-primary zen-hideaway">
  <div class="container-fluid d-none d-sm-flex justify-content-between">
    <a class="navbar-brand d-inline-flex flex-row align-items-center" href="{reverse('website:index')}">
        <img src="{settings.STATIC_URL}website/images/logo.png" width="50" height="50" alt="Logotype for Digital Humanities Research Institute">
        <div class="d-inline-flex flex-column">
            <div style="color: #4a6886 !important;" class="ml-3 small d-none d-md-block">Digital Humanities Research Institute</div>
            <div style="color: #4a6886 !important;" class="ml-3 small d-block d-md-none">DHRI</div>
            <div class="text-white ml-3">Curriculum</div>
        </div>
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

    #### Start mini menus
    html += '<div id="mini-menus" class="container-fluid">'
    # Workshops mini menu
    html += '''<div class="collapse row pt-0 pb-5 px-4 bg-primary" id="allWorkshops"><div class="col-12 my-3"><h5 class="text-white h4">Workshops</h5></div>'''
    for workshop in obj['workshops']:
        html += '<div class="col-12 col-sm-6 col-xl-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
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
        html += '<div class="col-12 col-sm-6 col-xl-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
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
        html += '<div class="col-12 col-sm-6 col-xl-4 mb-3"><div class="card h-100" style="box-shadow: 0 1rem 3rem rgba(0,0,0,0.375) !important;">'
        html += f'''<div class="card-body">
                        <h5 class="card-title m-0 bolder"><a href="{ reverse('insight:insight', kwargs={'slug':insight.slug}) }" class="stretched-link">{ insight.title }</a></h5>
                    </div>'''
        html += '</div></div>'
        pass
    html += '</div>'

    #### End mini menus
    html += '</div>'

    return mark_safe(html)