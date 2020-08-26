from django.core.management import BaseCommand
from django.core.files import File
from django.conf import settings
from backend.dhri.log import Logger, log_created
from backend.dhri.install_parser import InstallLoader
from backend.models import Software, Instruction, Step, Screenshot
import re, os


log = Logger(name='loadinstalls')


def _get_order(step):
    g = re.search(r"Step ([0-9]+): ", step)
    if g:
        order = g.groups()[0]
        step = re.sub(r'Step ([0-9]+): ', '', step)
    else:
        order = 0
        log.warning('Found an installation step that does not show the order clearly (see documentation). Cannot determine order: ' + str(step))
    return(order, step)


from pathlib import Path

def create_installations():

    installs = InstallLoader()

    for software in installs.all_software:
        instructions = installs.instructions.get(software)

        operating_systems = {'Windows': instructions.windows, 'macOS': instructions.mac_os}
        for o_s, current_instructions in operating_systems.items():
            if current_instructions:
                soft, created = Software.objects.get_or_create(software=software, operating_system=o_s)
                log.created(created, f'{o_s} Software', soft.software, soft.id)

                instr, created = Instruction.objects.get_or_create(software=soft, what=instructions.what, why=instructions.why)
                log.created(created, f'{o_s} Installation instructions', instr.software, instr.id)

                for _, d in current_instructions.items():
                    html = d.get('html')
                    header = d.get('header')
                    order = d.get('order')
                    s, created = Step.objects.get_or_create(instruction=instr, order=order, text=html, header=header)
                    log.created(created, 'Step', s.order, s.id)

                    i = 1
                    for screenshot in d.get('screenshots'):
                        if screenshot[0] == '' or screenshot[0] == 'None' or screenshot[0] == None or screenshot[1] == 'None' or screenshot[1] == None:
                            if screenshot[1] in [None, 'None']:
                                log.warning(f'Cannot find local cache for screenshot for installation step {s.order} (in {s.instruction}) so skipping: {screenshot}', color='red')
                            else:
                                log.warning(f'Cannot interpret screenshot data so skipping: {screenshot}', color='red')
                            continue

                        # Check existing screenshots
                        for sh in Screenshot.objects.filter(gh_name=screenshot[0]).all():
                            fullname = sh.image.name
                            if not sh.image.storage.exists(fullname):
                                print(f'{sh.id} delete... (file {fullname} does not exist)')
                                sh.delete()

                        sh, created = Screenshot.objects.get_or_create(step=s, gh_name=screenshot[0], defaults={'order': i})
                        log.created(created, f'Screenshot for {sh.step.instruction}', sh.order, sh.id)
                        if created:
                            with open(screenshot[1], 'rb') as f:
                                sh.image = File(f, name=screenshot[0])
                                sh.save()
                                i += 1


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Load all installs'

    def handle(self, *args, **options):
        create_installations()