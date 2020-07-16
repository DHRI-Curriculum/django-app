from dhri.utils.loader import Loader
from dhri.utils.parse_lesson import LessonParser
import json
from pathlib import Path


l = Loader('https://github.com/DHRI-Curriculum/git', 'v2.0-kristen-edits')
git_lessons = l._lessons_raw + '\n'
git_lessons = LessonParser(git_lessons)

l = Loader('https://github.com/DHRI-Curriculum/text-analysis', 'v2.0-rafa-edits')
text_lessons = l._lessons_raw + '\n'
text_lessons = LessonParser(text_lessons)

l = Loader('https://github.com/DHRI-Curriculum/python', 'v2.0-filipa-edits')
python_lessons = l._lessons_raw + '\n'
python_lessons = LessonParser(python_lessons)

l = Loader('https://github.com/DHRI-Curriculum/html-css', 'v2.0-param-edits')
html_lessons = l._lessons_raw + '\n'
html_lessons = LessonParser(html_lessons)
