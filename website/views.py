from workshop.models import Workshop
from django.views.generic import ListView


class Index(ListView):
    model = Workshop
    template_name = 'website/index.html'
