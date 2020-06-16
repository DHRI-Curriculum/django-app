
BACKEND_AUTO = "Github"
BRANCH_AUTO = "v2.0"


REMOVE_EMPTY_HEADINGS = True    # removing empty headings from sectioning of markdown
BULLETPOINTS_TO_LISTS = True    # remakes sections that ONLY contain bulletpoints into python lists


NORMALIZING_SECTIONS = {
    'frontmatter': {
        'abstract': ['Abstract'],
        'learning_objectives': ['Learning Objectives'],
        'estimated_time': ['Estimated time'],
        'contributors': ['Acknowledgements', 'Acknowledgement', 'Collaborator', 'Collaborators'],
        'ethical_considerations': ['Ethical consideration', 'Ethical considerations', 'Ethics'],
        'readings': ['Pre-reading suggestions', 'Prereading suggestions', 'Pre reading suggestions', 'Pre-readings', 'Pre readings', 'Prereadings', 'Pre-reading', 'Pre reading', 'Prereading'],
        'projects': ['Project', 'Projects', 'Projects that use these skills', 'Projects which use these skills'],
        'resources': ['Resources (optional)', 'Resource (optional)', 'Resources optional', 'Resource optional'],
    },
    'theory-to-practice': {
        'section': ['Other', 'Ways', 'Of', 'Spelling', 'Section']
    },
    'assessment': {
        'section_name': ['Yet', 'More', 'Kinds', 'of', 'Spells']
    }
}

# Regex setup
MD_LIST_ELEMENTS = r"\- (.*)(\n|$)"
NUMBERS = r"(\d+([\.,][\d+])?)"
URL = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"



def _check_normalizer(dictionary=NORMALIZING_SECTIONS):
    from itertools import chain

    for section in NORMALIZING_SECTIONS:
        all_ = [x.lower() for x in list(chain.from_iterable([x for x in NORMALIZING_SECTIONS[section].values()]))]

        if max([all_.count(x) for x in set(all_)]) > 1:
            raise RuntimeError("NORMALIZING_SECTIONS is confusing: multiple alternative strings for normalizing.") from None
        
_check_normalizer()