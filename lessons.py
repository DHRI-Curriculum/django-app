from dhri.utils.loader import Loader

l = Loader('https://github.com/DHRI-Curriculum/git', 'v2.0-kristen-edits')

import json
from pathlib import Path

lessons_txt = Path('lessons.txt')
lessons_json = Path('lessons.json')
lessons_txt.write_text(l._lessons_raw)
lessons_json.write_text(json.dumps(l.lessons))