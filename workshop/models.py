from django.db import models
from django.utils.text import slugify
from library.models import Reading, Project, Resource, Tutorial
from learner.models import Profile
from django.contrib.auth.models import User
from backend.mixins import CurlyQuotesMixin
#from backend.dhri.text import dhri_slugify


def dhri_slugify(string: str) -> str: # TODO: Move to backend.dhri.text
    import re
    from django.utils.text import slugify
    # first replace any non-OK characters [/] with space
    string = re.sub(r'[\/\-\–\—\_]', ' ', string)

    # then replace too many spaces with one space
    string = re.sub(r'\s+', ' ', string)

    # then replace space with -
    string = re.sub(r'\s', '-', string)


    # then replace any characters that are not in ALLOWED charset with nothing
    string = re.sub(r'[^a-zA-Z\-\s]', '', string)

    # finally, use Django's slugify
    string = slugify(string)

    return string


class Workshop(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    parent_backend = models.CharField(max_length=100, blank=True, null=True)
    parent_repo = models.CharField(max_length=100, blank=True, null=True)
    parent_branch = models.CharField(max_length=100, blank=True, null=True)
    views = models.PositiveSmallIntegerField(default=0)
    image = models.ImageField(
        upload_to='workshop_headers/', default='workshop_headers/default.jpg')

    def save(self, *args, **kwargs):
        self.slug = dhri_slugify(self.name)
        super(Workshop, self).save()

    def __str__(self):
        return f'{self.name}'

    @property
    def terms(self):
        "Returns all the terms associated with all lessons belonging to workshop."
        _ = list()
        for lesson in self.lessons.all():
            _.extend(lesson.terms.all())
        return(_)

    @property
    def has_terms(self):
        for lesson in self.lessons.all():
            if lesson.terms.count():
                return True
        return False


class Contributor(models.Model):
    first_name = models.TextField(max_length=100)
    last_name = models.TextField(max_length=100)
    # This one is really only used when Contributor's profile is set to null
    url = models.TextField(max_length=200, null=True, blank=True)
    profile = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.CASCADE)

    def _fullname(self):
        return self.first_name + ' ' + self.last_name

    _fullname.short_description = "Full name of contributor"
    _fullname.admin_order_field = 'last_name'

    full_name = property(_fullname)

    def __str__(self):
        return f'{self.full_name}'

    def get_collaboration_by_role(self):
        return [
            {'group': 'Current Author', 'list': self.collaborations.filter(
                role='Au', current=True)},
            {'group': 'Past Author', 'list': self.collaborations.filter(
                role='Au', current=False)},
            {'group': 'Current Reviewer', 'list': self.collaborations.filter(
                role='Re', current=True)},
            {'group': 'Past Reviewer', 'list': self.collaborations.filter(
                role='Re', current=False)},
            {'group': 'Current Editor', 'list': self.collaborations.filter(
                role='Ed', current=True)},
            {'group': 'Past Editor', 'list': self.collaborations.filter(
                role='Ed', current=False)},
        ]


class Frontmatter(CurlyQuotesMixin, models.Model):
    curly_fields = ['abstract']

    workshop = models.OneToOneField(
        Workshop, related_name="frontmatter", on_delete=models.CASCADE)
    abstract = models.TextField()
    estimated_time = models.PositiveSmallIntegerField(
        blank=True, null=True, help_text="assign full minutes")
    projects = models.ManyToManyField(
        'library.Project', related_name="frontmatters", blank=True)
    resources = models.ManyToManyField(
        'library.Resource', related_name="frontmatters", blank=True)
    readings = models.ManyToManyField(
        'library.Reading', related_name="frontmatters", blank=True)
    contributors = models.ManyToManyField(
        Contributor, related_name="frontmatters", blank=True, through='Collaboration')
    prerequisites = models.ManyToManyField(
        Workshop, related_name="prerequisites", blank=True)

    def __str__(self):
        return f'Frontmatter for {self.workshop.name}'


class Collaboration(models.Model):  # TODO: Do we want these ordered?
    AUTHOR = 'Au'
    REVIEWER = 'Re'
    EDITOR = 'Ed'
    ROLE_CHOICES = [
        (AUTHOR, 'Author'),
        (REVIEWER, 'Reviewer'),
        (EDITOR, 'Editor'),
    ]
    frontmatter = models.ForeignKey(Frontmatter, on_delete=models.CASCADE)
    contributor = models.ForeignKey(
        Contributor, on_delete=models.CASCADE, related_name='collaborations')
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default=AUTHOR)
    current = models.BooleanField(default=False)

    def __str__(self):
        return f'''{self.contributor.full_name}'s role in {self.frontmatter.workshop.name} ({self._get_current_text()} {self.get_role_display()})'''

    def is_current(self):
        if self.current:
            return True
        return False

    def _get_current_text(self):
        if self.current:
            return "Current"
        return "Past"

    class Meta:
        ordering = ('current',)


class LearningObjective(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    frontmatter = models.ForeignKey(
        Frontmatter, on_delete=models.CASCADE, related_name="learning_objectives")
    label = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.label}'


class EthicalConsideration(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    frontmatter = models.ForeignKey(
        Frontmatter, on_delete=models.CASCADE, related_name="ethical_considerations")
    label = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.label}'


class Praxis(CurlyQuotesMixin, models.Model):
    curly_fields = ['intro']

    intro = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Reading, related_name='praxis')
    further_projects = models.ManyToManyField(Project, related_name='praxis')
    more_resources = models.ManyToManyField(Resource, related_name='praxis')
    tutorials = models.ManyToManyField(Tutorial, related_name='praxis')
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE)

    def __str__(self):
        return f'Praxis collection for workshop {self.workshop.name}'

    class Meta:
        verbose_name_plural = "praxes"


class Blurb(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']

    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return(f'Blurb for workshop {self.workshop.name} by {self.user}')


class NextStep(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    praxis = models.ForeignKey(
        Praxis, on_delete=models.CASCADE, related_name='next_steps')
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order',)


class DiscussionQuestion(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    praxis = models.ForeignKey(
        Praxis, on_delete=models.CASCADE, related_name='discussion_questions')
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order',)
