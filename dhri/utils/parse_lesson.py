from dhri.interaction import Logger
from dhri.utils.markdown import split_into_sections

log = Logger(name='lesson-parser')


class LessonParser():

    def __init__(self, markdown:str):
        self.markdown = markdown

        self.data = []

        for title, body in split_into_sections(self.markdown, level_granularity=1).items():
            droplines = []

            challenge = ""
            # test for challenge
            if "challenge" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## challenge"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                challenge += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            solution = ""
            # test for solution
            if "solution" in body.lower():
                for line_num, line in enumerate(body.splitlines()):
                    if line.lower().startswith("## solution"):
                        droplines.append(line_num)
                        startline = line_num + 1
                        nextlines = (item for item in body.splitlines()[startline:])
                        done = False
                        while not done:
                            try:
                                l = next(nextlines)
                                if l.startswith("#"):
                                    done = True
                                    continue
                                solution += l + "\n"
                                droplines.append(startline)
                                startline += 1
                            except StopIteration:
                                done = True

            # fix body
            cleaned_body = ''
            for i, line in enumerate(body.splitlines()):
                if line.strip() == '': continue
                if i not in droplines:
                    cleaned_body += line + '\n'

            # clean up everything
            title = title.strip()
            body = body.strip()
            challenge = challenge.strip()
            solution = solution.strip()

            if challenge == '': challenge = None
            if solution == '': solution = None

            if solution and not challenge:
                log.error(f"The lesson {title} has a solution but no challenge. The program has stopped.")
            elif challenge and not solution:
                log.warning(f'The lesson {title} has a challenge with no solution.')

            data = {
                    'title': title,
                    'text': cleaned_body,
                    'challenge': challenge,
                    'solution': solution
                }

            self.data.append(data)


    def __len__(self):
        return(len(self.data))