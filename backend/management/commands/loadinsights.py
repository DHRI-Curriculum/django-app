from django.core.management import BaseCommand
from django.core.files import File
from backend.dhri.log import Logger, log_created
from backend.dhri.insight_parser import InsightLoader
from backend.models import Software, Insight, Section, OperatingSystemSpecificSection
from django.db.models.functions import Lower


log = Logger(name='loadinsights')


def create_insights():

    insights = InsightLoader()

    for _, i in insights.insights.items():

        insight, created = Insight.objects.get_or_create(
            title=i.header,
            text=i.introduction
        )
        log.created(created, 'Insight', insight.title, insight.id)

        software = _.replace('-', ' ').title()
        softwares = Software.objects.annotate(software_lower=Lower('software')).filter(software_lower__icontains=software.lower())
        if not softwares:
            log.warning(f'Warning: Cannot find any software in the installations matching `{software}`.')
        else:
            log.log(f'Found software in the installations matching `{software}` and will link the Insight.', force=True)
            insight.software.add(*softwares)
            insight.save()

        order = 1
        for section, text in i.sections.items():
            obj, created = Section.objects.get_or_create(
                insight=insight,
                title=section,
                text=text,
                defaults={
                    'order': order
                }
            )
            log.created(created, 'Section', obj.title, obj.id)
            order += 1

        for operating_system, d in i.os_specific.items():
            multiple_sections = Section.objects.filter(title=d.get('section')).count() > 1

            try:
                lookup_section = Section.objects.filter(title=d.get('section')).last()
            except:
                log.error(f'Cannot find the section title `{d.get("section")}`. Make sure that the insights file for `{insight.title}` contains a section `{d.get("section")}` that contains the OS-specific instructions.')

            likely_correct = lookup_section.insight.title == insight.title

            if multiple_sections and not likely_correct:
                log.error("Found multiple sections where the OS specific instructions could be placed and was unable to safely pick one.")
            if multiple_sections and likely_correct:
                log.warning("Found multiple sections where the OS specific instructions could be placed. Will go ahead and place them inside the latest created one, which belongs to the same Insight object.")

            obj, created = OperatingSystemSpecificSection.objects.get_or_create(
                section=lookup_section,
                operating_system=operating_system,
                text=d.get('text')
            )
            log.created(created, f'OS Specific instructions for {insight.title}', obj.operating_system, obj.id)

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Load all insights'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true')

    def handle(self, *args, **options):
        if options.get('wipe', False):
            Insight.objects.all().delete()
            log.log(f'All Insights removed.', force=True)

            Section.objects.all().delete()
            log.log(f'All Sections removed.', force=True)

            OperatingSystemSpecificSection.objects.all().delete()
            log.log(f'All Operating System Specific Sections removed.', force=True)

            loader = InsightLoader(force_download=True)
            log.log(f'Install cache removed.', force=True)

        create_insights()