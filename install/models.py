from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.db import models
from django.utils.text import slugify
from backend.mixins import CurlyQuotesMixin


class Software(models.Model):
    software = models.CharField(max_length=250)
    operating_system = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.software} ({self.operating_system})'


class InstructionManager(models.Manager):
    def by_software(self):
        l = dict()
        for s in Software.objects.all().order_by('software'):
            if not s.software in l:
                l[s.software] = dict()
            l[s.software][s.operating_system] = Instruction.objects.get(
                software=s)
        return l

    def by_os(self):
        l = dict()
        for s in Software.objects.all().order_by('software'):
            if not s.operating_system in l:
                l[s.operating_system] = dict()
            l[s.operating_system][s.software] = Instruction.objects.get(
                software=s)
        return l


class Instruction(CurlyQuotesMixin, models.Model):
    curly_fields = ['what', 'why']

    slug = models.CharField(max_length=200, blank=True)
    software = models.ForeignKey(
        Software, on_delete=models.CASCADE, related_name='instructions')
    what = models.TextField(blank=True)
    why = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='software_headers/', default='software_headers/default.jpg')
    objects = InstructionManager()

    def save(self, *args, **kwargs):
        slug = self.software.software.replace('-', ' ').replace(
            '/', ' ') + '-' + self.software.operating_system.replace('-', ' ').replace('/', ' ')
        self.slug = slugify(slug)
        super(Instruction, self).save()

    def __str__(self):
        return f'Installation instruction for {self.software.software} ({self.software.operating_system})'


class Step(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    instruction = models.ForeignKey(
        Instruction, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveSmallIntegerField()
    text = models.TextField(blank=False)
    header = models.TextField(blank=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f'Instruction step {self.order} for {self.instruction.software.software} ({self.instruction.software.operating_system})'


class Screenshot(models.Model):
    step = models.ForeignKey(
        Step, on_delete=models.CASCADE, related_name='screenshots')
    order = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='installation_screenshots')
    gh_name = models.CharField(max_length=255, blank=False, unique=True)
    alt_text = models.TextField(blank=False, default="No alt text")

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f'Screenshot {self.order} for step {self.step.order} ({self.step.instruction.software.software}/{self.step.instruction.software.operating_system})'


####### Below, see https://cmljnelson.blog/2020/06/22/delete-files-when-deleting-models-in-django/ ######


@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    """ Whenever ANY model is deleted, if it has a file field on it, delete the associated file too"""
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)


@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    """ Delete the file if something else get uploaded in its place"""
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            # its got a file field. Let's see if it changed
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db, field.name)
            instance_file_field = getattr(instance, field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(
                    sender, instance, field, instance_in_db_file_field)


def delete_file_if_unused(model, instance, field, instance_file_field):
    """ Only delete the file if no other instances of that model are using it"""
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(
        **dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)
