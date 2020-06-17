from dhri.markdown_parser import get_raw_content, split_md_into_sections_batch
from dhri.parser import normalize_data
from dhri.backend import *
from dhri.models import Question, Answer, QuestionType
from dhri.meta import reset_all


## Add to dhri.constants

QUESTION_AUTOCHOICE = 'radio' # other choices could be: select, text, range?, checkbox, 



reset_all()


def test_for_auto_label():
    try:
        return QuestionType.objects.get(label=QUESTION_AUTOCHOICE)
    except:
        q = QuestionType(label=QUESTION_AUTOCHOICE)
        q.save()
        return(q)
    

## First make sure that we have our QuestionTypes set up

auto_question_type = test_for_auto_label()
print(auto_question_type)




data = get_raw_content("https://github.com/DHRI-Curriculum/command-line", branch="v2.0-smorello-edits")
data = split_md_into_sections_batch({'frontmatter', 'theory-to-practice', 'assessment'}, data['content'])
data = normalize_data(data['assessment'], 'assessment')

def split_assessment(data):
    return((
        [x for x in data['qualitative_assessment'].splitlines() if x],
        [x for x in data['quantitative_assessment'].splitlines() if x]
    ))

qualitative_lines, quantitative_lines = split_assessment(data)


quantitative_questions = []
for linenumber, line in enumerate(quantitative_lines):
    question, answers = None, None
    if not line.startswith("- "):
        question, answers, skip_ahead = line, [], False
        for order, nextline in enumerate(quantitative_lines[linenumber + 1:]):
            if not nextline.startswith('- '): skip_ahead = True
            if skip_ahead: continue
            answers.append((nextline.split("- ")[1], order+1))
    if question and answers:
        quantitative_questions.append((question, answers))

# do all the queries
for item in quantitative_questions:
    question, answer_labels = item
    print("CREATE Question.question:", question)
    q = Question(question_type=auto_question_type, label=question)
    q.save()
    answers_list = []
    for label_item in answer_labels:
        label, order = label_item
        print("CREATE Answer.label:")
        print("-- label -->", label)
        print("-- order -->", order)
        a = Answer(label=label, order=order, question=q)
        a.save()
        answers_list.append(a)
    q.answer.set(answers_list)
    q.save()

