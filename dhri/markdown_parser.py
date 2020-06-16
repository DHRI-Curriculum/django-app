import json, requests

# This code was originally published at https://github.com/kallewesterling/markdown-interpreter


REMOVE_EMPTY_HEADINGS = True    # removing empty headings from sectioning of markdown
BULLETPOINTS_TO_LISTS = True    # remakes sections that ONLY contain bulletpoints into python lists
# TODO: add a constant FORCE_BULLETPOINTS that uses regex to extract whatever bulletpoints exist in a section and skip other content.

# TODO: remove the explicit reference to the dhri-test-repo

def get_raw_content(repo="https://github.com/kallewesterling/dhri-test-repo", branch="master"):
    """
    Downloads all the raw content from a provided repository on GitHub, and from a particular master.

    The repository must be *public* and must contain the following three files:
    - frontmatter.md
    - theory-to-practice.md
    - assessment.md
    """

    if repo.endswith("/"): repo = repo[:-1]

    if len(repo.split("/")) != 5:
        raise RuntimeError("Cannot interpret repo URL. Are you sure it's a simple https://github.com/user-name/repo link?")

    user = repo.split("/")[3]
    repo_name = repo.split("/")[4]

    raw_url = f"https://raw.githubusercontent.com/{user}/{repo_name}/{branch}"

    raw_meta = {}
    raw_meta['frontmatter'] = f"{raw_url}/frontmatter.md"
    raw_meta['theory-to-practice'] = f"{raw_url}/theory-to-practice.md"
    raw_meta['assessment'] = f"{raw_url}/assessment.md"

    raw_content = {}
    raw_content['frontmatter'] = requests.get(raw_meta['frontmatter']).text
    raw_content['theory-to-practice'] = requests.get(raw_meta['theory-to-practice']).text
    raw_content['assessment'] = requests.get(raw_meta['assessment']).text

    return({
        'repo': repo,
        'branch': branch,
        'meta': raw_meta,
        'content': raw_content,
    })


def section_is_bulletpoints(markdown):
    """ Returns `True` if a section of markdown only contains bullet points. Otherwise returns `False` """
    if not "\n- " in markdown and not markdown.startswith("- "): return False # make sure there ARE lists in there at all
    return len([x for x in markdown.splitlines() if x.startswith("- ")]) == len(markdown.splitlines())


def section_as_list(markdown, shave_off=2):
    """ Returns each line from a markdown section as a list element, with the first `shave_off` letters removed from each element. """
    return [x[shave_off:] for x in markdown.splitlines()]


def split_md_into_sections(markdown, remove_empty_headings=REMOVE_EMPTY_HEADINGS, bulletpoints_to_lists=BULLETPOINTS_TO_LISTS):
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.

    The function accepts two arguments:
    - `remove_empty_headings` (bool) which determines whether empty dictionary keys (headings) should be removed from the dictionary (defaults to REMOVE_EMPTY_HEADINGS, defined on line 3)
    - `bulletpoints_to_lists` (bool) which determines whether sections that contain ONLY bulletpoints should be converted into python lists with each bullet point as an element in the list (defaults to BULLETPOINTS_TO_LISTS, defined on line 4)
    """

    if not isinstance(remove_empty_headings, bool): raise RuntimeError("`remove_empty_headings` provided must be a boolean.")
    if not isinstance(bulletpoints_to_lists, bool): raise RuntimeError("`bulletpoints_to_lists` provided must be a boolean.")

    lines = [x for x in markdown.splitlines() if x]

    sections = {}

    for linenumber, line in enumerate(lines):
        if line.startswith("### ") or line.startswith("## ") or line.startswith("# "):
            header = "".join([x for x in line.split("#") if x]).strip()
            if header not in sections:
                sections[header] = ""
                skip_ahead = False
                for nextline in lines[linenumber + 1:]:
                    if nextline.startswith("#"): skip_ahead = True
                    if skip_ahead: continue
                    sections[header] += "\n" + nextline
                sections[header] = sections[header].strip()

                if bulletpoints_to_lists:
                    if section_is_bulletpoints(sections[header]):
                        sections[header] = section_as_list(sections[header], shave_off=2)

                if remove_empty_headings:
                    if len(sections[header]) == 0: del sections[header]

    return(sections)


def load_data(json_file):
  dhri_log(f"loading {json_file}")

  if not Path(json_file).exists():
    dhri_error(f"Could not find JSON file on path: {json_file}")

  data = json.loads(Path(json_file).read_text())
  return(data)