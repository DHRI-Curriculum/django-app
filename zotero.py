from dhri.django import django, Fixture
from dhri.django.models import Workshop, Project, Reading, Resource, Tutorial
from dhri.zotero import LocalZoteroCache, ZoteroItem, log
from dhri.interaction import get_or_default

zotero = LocalZoteroCache()
for collection in zotero.collections:
    for item in collection['items']:
        i = ZoteroItem(item)
        if i.for_website:
            if i.url and i.url_exists == False:
                log.warning(f'URL does not exist (skipping): {i.url}', kill=False)
                continue

            add_to_database = i.get_attributes([
                'url',
                'abstract',
                'title',
            ])

            zotero_url = item.get('links',{'alternate': {'href': ''}}).get('alternate', {'href': ''}).get('href')

            if i.itemType == "journalArticle":
                add_to_database.update({'parent_title': i.publicationTitle})
            elif i.itemType == "blogPost":
                add_to_database.update({'parent_title': i.blogTitle})
            elif i.itemType == "webpage":
                add_to_database.update({'parent_title': i.websiteTitle})
            elif i.itemType == "videoRecording":
                pass
            elif i.itemType == "presentation":
                pass
            else:
                log.warning(f"While trying to add a {i.category} to workshop {i.curriculum}, the script encountered an itemType that is not yet supported (skipping): {i.itemType}", kill=False)
                continue

            workshop = Workshop.objects.filter(slug=i.curriculum).last()
            if workshop == None:
                log.warning(f'Workshop {i.curriculum} does not exist. Did you populate the database before running this script?', kill=False)

            if add_to_database.get('parent_title') != None and add_to_database.get('title') != None:
                title = add_to_database.get('title') + " (from " + add_to_database.get('parent_title') + ")"
            elif add_to_database.get('title') != None:
                title = add_to_database.get('title')
            else:
                log.warning(f'Cannot find a title for the Zotero item (skipping): Visit {zotero_url} to set a title', kill=False)


            if i.category == "project":
                obj = Project
            elif i.category == "reading":
                obj = Reading
            elif i.category == "resource":
                obj = Resource
            elif i.category == "tutorial":
                obj = Tutorial
            else:
                log.warning(f'Cannot interpret category `{i.category}` which has been set for {i.title} (skipping): Visit {zotero_url} to correct it to project/reading/resource', kill=False)
                continue

            replace = "y"
            test = obj.objects.filter(title=title).count()
            if test > 1:
                replace, msg = 'n', f'{i.title} already exists. Do you want to add another? [y/N] '
                replace = get_or_default(msg, replace)
            if replace.lower() != "y":
                continue

            obj = obj()

            if i.category != "tutorial":
                obj.title = title
            elif i.category == "tutorial":
                obj.label = title

            obj.url = add_to_database.get('url')
            obj.comment = add_to_database.get('abstract')
            obj.zotero_item = zotero_url

            obj.save()

            if i.category == "project":
                workshop.praxis.more_projects.add(obj)
            elif i.category == "reading":
                workshop.praxis.further_readings.add(obj)
            elif i.category == "resource":
                workshop.praxis.more_resources.add(obj)

            workshop.praxis.save()

            log.log(f"Added `{i.title}`, a {i.category} to workshop {i.curriculum} from URL: {zotero_url}")