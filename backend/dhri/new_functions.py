from backend.dhri.log import Logger
from backend.dhri.markdown import as_list, extract_links

log = Logger()

def mini_parse_keywords(markdown:str):
    log.name = 'keywords-parser'

    _ = list()
    for keyword in as_list(markdown):
        for d in extract_links(keyword):
            _.append({
                'title': d[0],
                'url': d[1],
                'slug': d[1].split('/')[-1].replace('.md', '')
            })

    return _


def mini_parse_eval(markdown:str):
    log.name = 'evaluation-parser'

    def reset_dict():
        return {'question': '', 'answers': {'correct': [], 'incorrect': []} }

    dict_collector = list()
    d = reset_dict()
    in_q = False

    for line in markdown.splitlines():
        is_empty = line.strip() == ''
        is_answer = line.startswith('- ')

        if not is_answer and not is_empty:
            in_q = True
            d['question'] += line + '\n'
        elif in_q and is_answer:
            if line.strip().endswith('*'):
                d['answers']['correct'].append(line.strip()[2:-1].strip())
            else:
                d['answers']['incorrect'].append(line.strip()[2:].strip())
        elif is_empty and in_q:
            d['question'] = d['question'].strip()
            dict_collector.append(d)
            in_q = False
            d = reset_dict()
        elif is_answer:
            # stray answer belonging to the latest question so attach it...
            try:
                if line.strip().endswith('*'):
                    dict_collector[len(dict_collector)-1]['answers']['correct'].append(line.strip()[2:-1].strip())
                else:
                    dict_collector[len(dict_collector)-1]['answers']['incorrect'].append(line.strip()[2:].strip())
            except IndexError:
                log.warning(f'Found and skipping a stray answer that cannot be attached to a question: {line.strip()}')


    # add final element
    d['question'] = d['question'].strip()
    dict_collector.append(d)

    # clean up dict_collector
    for i, item in enumerate(dict_collector):
        if not item.get('question') and not len(item.get('answers').get('correct')) and not len(item.get('answers').get('incorrect')):
            del dict_collector[i]
    return(dict_collector)