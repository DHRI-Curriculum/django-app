from django.db import models
from django.utils.text import slugify




class Software(models.Model):
    software = models.CharField(max_length=250)
    operating_system = models.CharField(max_length=250)

    def __str__(self):
        return f'Software {self.software} ({self.operating_system})'


class Instruction(models.Model):
    slug = models.CharField(max_length=200, blank=True)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    what = models.TextField(blank=True)
    why = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        slug = self.software.software.replace('-',' ').replace('/',' ') + '-' + self.software.operating_system.replace('-',' ').replace('/',' ')
        self.slug = slugify(slug)
        super(Instruction, self).save()

    def __str__(self):
        return f'Installation instruction for {self.software.software} ({self.software.operating_system})'


class Step(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveSmallIntegerField()
    text = models.TextField(blank=False)
    header = models.TextField(blank=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f'Instruction step {self.order} for {self.instruction.software.software} ({self.instruction.software.operating_system})'


class Screenshot(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='screenshots')
    order = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='installation_screenshots')
    gh_name = models.CharField(max_length=500, blank=False, unique=True)
    alt_text = models.TextField(blank=False, default="No alt text")

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f'Screenshot {self.order} for step {self.step.order} ({self.step.instruction.software.software}/{self.step.instruction.software.operating_system})'