# from api.models import *
from assessment.models import *
# from feedback.models import *
from glossary.models import *
from insight.models import *
from install.models import *
from learner.models import *
from lesson.models import *
from library.models import *
from website.models import *
from workshop.models import *


ALL_MODELS = [
    ### app: assessment
    Answer, Question, QuestionType,

    ### app: feedback
    # Issue,

    ### app: learner
    ProfileLink, Progress,
    # Profile,

    ### app: lesson
    Lesson, Challenge, Solution, Evaluation, Question, Answer,

    ### app: library
    Tutorial, Project, Reading,
    # Resource, 

    ### app: website
    Snippet,

    ### app: workshop
    Workshop, Contributor, Frontmatter, Collaboration, LearningObjective, EthicalConsideration, Praxis, Blurb, NextStep, DiscussionQuestion,

    ### app: glossary
    Term,

    ### app: install
    Software, Instruction, Step, Screenshot,

    ### app: insight
    Insight, Section, OperatingSystemSpecificSection,
]
