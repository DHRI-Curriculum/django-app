from django.db import models
from resource.models import Resource
from install.models import Software
from insight.models import Insight
from django.contrib.auth.models import User
from backend.mixins import CurlyQuotesMixin
from backend.dhri.text import dhri_slugify


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
        if not self.id:
            self.slug = dhri_slugify(self.name)
        super(Workshop, self).save()

    def save_slug(self, *args, **kwargs):
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
    from learner.models import Profile

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
        Resource, related_name="frontmatter_projects", blank=True)
    readings = models.ManyToManyField(
        Resource, related_name="frontmatter_readings", blank=True)
    contributors = models.ManyToManyField(
        Contributor, related_name="frontmatters", blank=True, through='Collaboration')

    def __str__(self):
        return f'Frontmatter for {self.workshop.name}'


class Prerequisite(CurlyQuotesMixin, models.Model):
    curly_fields = ['text']
    EXTERNAL_LINK = 'external'
    INSTALL = 'install'
    INSIGHT = 'insight'
    WORKSHOP = 'workshop'
    CATEGORY_CHOICES = [
        (EXTERNAL_LINK, 'External link'),
        (INSIGHT, 'Insight'),
        (INSTALL, 'Installation instructions for software'),
        (WORKSHOP, 'Workshop'),
    ]

    text = models.TextField()
    label = models.TextField(max_length=200, blank=True, null=True)
    url = models.TextField(max_length=200, null=True, blank=True)
    required = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)
    frontmatter = models.ManyToManyField(Frontmatter, related_name="prerequisites")
    linked_workshop = models.ForeignKey(Workshop, related_name="prerequisite_for", on_delete=models.CASCADE, null=True)
    linked_software = models.ManyToManyField(Software, related_name="prerequisite_for", through='PrerequisiteSoftware')
    linked_insight = models.ForeignKey(Insight, related_name="prerequisite_for", on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=8, choices=CATEGORY_CHOICES, default=EXTERNAL_LINK)


class PrerequisiteSoftware(models.Model):
    prerequisite = models.ForeignKey(Prerequisite, on_delete=models.CASCADE)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    required = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)



class Collaboration(models.Model):
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

    class Meta:
        unique_together = ('frontmatter', 'label')


class EthicalConsideration(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    frontmatter = models.ForeignKey(
        Frontmatter, on_delete=models.CASCADE, related_name="ethical_considerations")
    label = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.label}'

    class Meta:
        unique_together = ('frontmatter', 'label')


class Praxis(CurlyQuotesMixin, models.Model):
    curly_fields = ['intro']

    intro = models.TextField(max_length=3000, blank=True, null=True)
    further_readings = models.ManyToManyField(Resource, related_name='praxis_further_readings')
    further_projects = models.ManyToManyField(Resource, related_name='praxis_further_projects')
    tutorials = models.ManyToManyField(Resource, related_name='praxis_tutorials')
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

    class Meta:
        unique_together = ('workshop', 'text', 'user')


class NextStep(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    praxis = models.ForeignKey(
        Praxis, on_delete=models.CASCADE, related_name='next_steps')
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = ('praxis', 'label')


class DiscussionQuestion(CurlyQuotesMixin, models.Model):
    curly_fields = ['label']

    praxis = models.ForeignKey(
        Praxis, on_delete=models.CASCADE, related_name='discussion_questions')
    label = models.TextField(max_length=500)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = ('praxis', 'label')
