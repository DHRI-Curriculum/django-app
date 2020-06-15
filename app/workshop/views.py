from django.shortcuts import render, HttpResponse

def index(request, slug=None):
    try:
      int(slug)
      is_id, is_slug = True, False
    except ValueError:
      is_id, is_slug = False, True

    if is_slug:
      response = f"<br />You have selected workshop slug {slug}."
    elif is_id:
      response = f"<br />You have selected workshop id {slug}."
    else:
      response = f"<br />You have not selected a workshop ID."
    return HttpResponse(response)