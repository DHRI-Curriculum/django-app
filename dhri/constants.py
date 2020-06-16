
BACKEND_AUTO = "Github"
BRANCH_AUTO = "v2.0"


NORMALIZING_SECTIONS = {
    'frontmatter': {
        'name': ['Name'],
        'abstract': ['Abstract'],
        'learning_objectives': ['Learning Objectives'],
        'estimated_time': ['Estimated time'],
        'contributors': ['Acknowledgements', 'Acknowledgement', 'Collaborator', 'Collaborators'],
        'ethical_considerations': ['Ethical consideration', 'Ethical considerations', 'Ethics'],
        'readings': ['Pre-reading suggestions', 'Prereading suggestions', 'Pre reading suggestions', 'Pre-readings', 'Pre readings', 'Prereadings', 'Pre-reading', 'Pre reading', 'Prereading'],
        'projects': ['Project', 'Projects', 'Projects that use these skills', 'Projects which use these skills'],
        'resources': ['Resources (optional)', 'Resource (optional)', 'Resources optional', 'Resource optional'],
        'parent_backend': ['Parent backend', 'Parent (backend)'],
        'parent_repo': ['Parent repo', 'Parent (repo)'],
        'parent_branch': ['Parent branch', 'Parent (brance)'],
    }
}

# Regex setup
MD_LIST_ELEMENTS = r"\- (.*)(\n|$)"
NUMBERS = r"(\d+([\.,][\d+])?)"
URL = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"



def _check_normalizer(dictionary=NORMALIZING_SECTIONS):
    from itertools import chain

    for section in NORMALIZING_SECTIONS:
        all_ = list(chain.from_iterable([x for x in NORMALIZING_SECTIONS[section].values()]))

        if max([all_.count(x) for x in set(all_)]) > 1:
            raise RuntimeError("NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.") from None
        
_check_normalizer()