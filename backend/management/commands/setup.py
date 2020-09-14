"""manage.py setup command"""

from django.core.management import BaseCommand


from .imports import *


# Set up logger
LOG = Logger(name='setup')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Download live data from DHRI curriculum repositories'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true')
        parser.add_argument('--structure', action='store_true')
        # parser.add_argument('--verbose', action='store_true') # TODO: Create verbose mode here...
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--repos', nargs='+', type=str)
        group.add_argument('--all', action='store_true')

    def handle(self, *args, **options):
        if options.get('wipe', False):
            wipe()

        if options.get('all', False) or options.get('structure', False):
            LOG.name = 'setup'

            LOG.log("Automatic import activated: Attempting to generate pages", force=True)
            create_pages()

            LOG.log("Automatic import activated: Attempting to generate groups", force=True)
            create_groups()

            LOG.log("Automatic import activated: Attempting to generate users", force=True)
            create_users()

            LOG.log("Automatic import activated: Attempting to generate glossary", force=True)
            create_terms()

            LOG.log("Automatic import activated: Attempting to generate installations", force=True)
            create_installations()

        repos = _get_repos(options)

        if repos:
            for d in repos:
                repo, branch = _test_for_branch(d)

                if not repo:
                    repo = d
                #LOG.error(f"Cannot understand repo {repo}.")

                LOG.log(f"Starting import: {repo} ({branch})", force=True)

                try:
                    l = Loader(f'https://github.com/DHRI-Curriculum/{repo}', branch, force_download=True)
                except MissingRequiredSection as e:
                    LOG.error(f"One or more required section(s) could not be found in {repo}: {e}")

                if options.get('all', False):
                    repo_name = l.meta['repo_name']
                else:
                    repo_name = get_or_default('Repository', l.meta['repo_name'])

                repo_name = get_or_default('Workshop name', auto_replace(repo_name.title()))
                LOG.name = l.repo_name


                workshop, created = Workshop.objects.get_or_create(
                    name = repo_name,
                    defaults = {
                        'parent_backend': l.parent_backend,
                        'parent_repo': l.parent_repo,
                        'parent_branch': l.parent_branch
                    }
                )
                LOG.created(created, 'Workshop', workshop.name, workshop.id)

                #LOG.name = LOG.original_name + "-lessons"
                if l.has_lessons:
                    for lesson_data in l.as_html.lessons:
                        try:
                            order += 1
                        except NameError:
                            order = 1

                        lesson, created = Lesson.objects.get_or_create(
                            workshop = workshop,
                            title = lesson_data['title'],
                            defaults = {
                                'text': lesson_data['text'],
                                'order': order
                            }
                        )
                        LOG.created(created, 'Lesson', lesson.title, lesson.id)

                        if lesson_data['challenge']:
                            challenge, created = Challenge.objects.get_or_create(
                                lesson = lesson,
                                text = lesson_data['challenge']
                            )
                            LOG.created(created, 'Challenge', challenge.text[:20] + '...', challenge.id)

                            if lesson_data['solution']:
                                obj, created = Solution.objects.get_or_create(
                                    challenge = challenge,
                                    text = lesson_data['solution']
                                )
                                LOG.created(created, 'Solution', obj.text[:20] + '...', obj.id)
                                processed_solution = True

                        if lesson_data['solution']:
                            try:
                                processed_solution
                            except NameError:
                                LOG.error(f'Lesson `{lesson.title}` has a solution but no challenge. Will continue but not insert the solution.', kill=False)

                        if lesson_data['evaluation']:
                            eval, created = Evaluation.objects.get_or_create(
                                lesson = lesson
                            )
                            LOG.created(created, 'Evaluation', eval.lesson.title, eval.id)
                            for d in lesson_data['evaluation']:
                                question = d.get('question')
                                if question:
                                    q, created = Question.objects.get_or_create(
                                        evaluation = eval,
                                        label = question
                                    )
                                    LOG.created(created, 'Question', q.label, q.id)

                                    answers = d.get('answers')
                                    if answers:
                                        correct_answers = answers.get('correct', [])
                                        incorrect_answers = answers.get('incorrect', [])
                                        has_answers = len(correct_answers) > 0 or len(incorrect_answers) > 0
                                        if has_answers:
                                            for answer in correct_answers:
                                                obj, created = Answer.objects.get_or_create(
                                                    question = q,
                                                    label = answer,
                                                    is_correct = True
                                                )
                                                LOG.created(created, 'Answer', obj.label, obj.id)
                                            for answer in incorrect_answers:
                                                obj, created = Answer.objects.get_or_create(
                                                    question = q,
                                                    label = answer,
                                                    is_correct = False
                                                )
                                                LOG.created(created, 'Answer', obj.label, obj.id)
                                else:
                                    LOG.warning(f"Question could not be interpreted in lesson {lesson.title}: Raw data — {d}")

                        if lesson_data['keywords']:
                            for d in lesson_data['keywords']:
                                obj = Term.objects.filter(term=d.get('title'))
                                if obj.count() > 1:
                                    obj = obj.last()
                                    LOG.warning(f'Term {d.get("title")} is not unique so will assign the latest added term to lesson {lesson.order} in workshop {lesson.workshop.name}: Preview of explication: {obj.explication[:30]}...')
                                elif obj.count() == 0:
                                    LOG.warning(f'Term {d.get("title")} cannot be found, so it will not be added to lesson {lesson.order} in workshop {lesson.workshop.name}.')
                                if obj.count() == 1:
                                    obj = obj.last()
                                    lesson.terms.add(obj)
                                    LOG.log(f'Term {obj.term} has been added to lesson {lesson.order} for workshop {lesson.workshop.name}.', force=True) # TODO: remove `force=True`

                    del order

                #LOG.name = LOG.original_name + "-frontmatter"
                for model in l.frontmatter_models:

                    if model == Frontmatter:
                        frontmatter, created = model.objects.get_or_create(
                            workshop = workshop,
                            defaults = {
                                'abstract': l.abstract,
                                'estimated_time': l.frontmatter['estimated_time']
                            }
                        )
                        LOG.created(created, 'Frontmatter for', frontmatter.workshop, frontmatter.id)

                    elif model == EthicalConsideration:
                        for label in l.ethical_considerations:
                            obj, created = model.objects.get_or_create(frontmatter = frontmatter, label = label)
                            LOG.created(created, 'Ethical Consideration', obj.label[:20] + '...', obj.id)

                    elif model == LearningObjective:
                        for label in l.learning_objectives:
                            obj, created = model.objects.get_or_create(frontmatter = frontmatter, label = label)
                            LOG.created(created, 'Learning Objective', obj.label[:20] + '...', obj.id)

                    elif model == Project:
                        for annotation in l.projects:
                            title, url = process_links(annotation, 'project')
                            obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                            LOG.created(created, 'Project', obj.title, obj.id)
                            frontmatter.projects.add(obj)

                    elif model == Reading:
                        for annotation in l.readings:
                            title, url = process_links(annotation, 'reading')
                            obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                            LOG.created(created, 'Reading', obj.title, obj.id)
                            frontmatter.readings.add(obj)

                    elif model == Contributor:
                        for contributor in l.contributors:
                            low_role = ''
                            is_author, is_reviewer, is_editor, is_current, is_past = False, False, False, False, False

                            if contributor.get('role'):
                                low_role = contributor.get('role').lower()
                                is_author = 'author' in low_role or 'contributor' in low_role
                                is_reviewer = 'review' in low_role
                                is_editor = 'editor' in low_role
                                is_current = 'current' in low_role
                                is_past = 'original' in low_role or 'past' in low_role

                            user = User.objects.filter(first_name=contributor.get('first_name', ''), last_name=contributor.get('last_name', ''))
                            if user.count() >= 1:
                                user = user.last()
                            else:
                                LOG.warning(f'Unable to find existing user for contributor {contributor.get("first_name", "")} {contributor.get("last_name", "")}')

                            # Create/get Contributor
                            c, created = model.objects.get_or_create(
                                first_name = contributor.get('first_name'),
                                last_name = contributor.get('last_name'),
                                url = contributor.get('url'),
                            )
                            LOG.created(created, 'Contributor', c.full_name, c.id)

                            if user:
                                c.profile = user.profile
                                c.save()

                            if is_author:
                                role = 'Au'
                            elif is_reviewer:
                                role = 'Re'
                            elif is_editor:
                                role = 'Ed'
                            else:
                                LOG.error(f'Cannot find a role for contributor {c.full_name}.', kill=True)

                            if not is_current or is_past:
                                LOG.warning(f'Cannot find whether contributor {c.full_name} is current/past. Will automatically set to past.')

                            # Create/get Collaboration
                            obj, created = Collaboration.objects.get_or_create(
                                contributor = c,
                                frontmatter = frontmatter,
                                role = role,
                                current = is_current
                            )

                            frontmatter.contributors.add(c)

                    else:
                        LOG.error(f'Have no way of processing {model} for app `frontmatter`. The `setup` script must be adjusted accordingly.', kill=False)

                #LOG.name = LOG.original_name + "-praxis"
                for model in l.praxis_models:

                    if model == Praxis:
                        praxis, created = model.objects.get_or_create(
                            workshop = workshop,
                            defaults = {
                                'discussion_questions': l.discussion_questions,
                                'next_steps': l.next_steps
                            }
                        )
                        LOG.created(created, 'Theory-to-practice for', praxis.workshop, praxis.id)

                    elif model == Tutorial:
                        for annotation in l.tutorials:
                            label, url = process_links(annotation, 'tutorial')
                            obj, created = model.objects.get_or_create(annotation = annotation, label = label, url = url)
                            LOG.created(created, 'Tutorial', obj.label, obj.id)
                            praxis.tutorials.add(obj)

                    elif model == Reading:
                        for annotation in l.further_readings:
                            title, url = process_links(annotation, 'reading')
                            obj, created = model.objects.get_or_create(annotation = annotation, title = title, url = url)
                            LOG.created(created, 'Reading', obj.title, obj.id)
                            praxis.further_readings.add(obj)

                    else:
                        LOG.error(f'Have no way of processing {model} for app `praxis`. The `setup` script must be adjusted accordingly.', kill=False)

        if options.get('all', False) or repos or options.get('structure', False):
            LOG.name = 'setup'

            LOG.log("Automatic import activated: Attempting to generate blurbs", force=True)
            create_blurbs()

            LOG.log("Automatic import activated: Attempting to generate insights", force=True)
            create_insights()


def _test_for_branch(d=''):
    repo, branch = None, None

    if isinstance(d, tuple):
        repo, branch = d

    if not branch:
        for r in AUTO_REPOS:
            if d == r[0]:
                branch = r[1]

    if not branch:
        while not branch:
            branch = get_or_default(f'What is the branch name you want to import?', '')

    return repo, branch

def _get_repos(options={}):
    repos = []

    if options.get('all', False):
        LOG.log("Automatic import activated.", force=True)
        repos = AUTO_REPOS
    else:
        repos = options.get('repos')

    return repos