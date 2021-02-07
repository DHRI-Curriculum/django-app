# Setting up a new workshop

## Step 1: Create the workshop's repository

Inside [DHRI-Curriculum](https://github.com/DHRI-Curriculum/), add whichever repository you need.

If you want to, you can create a new branch inside the repository, specific for the Django data. Make note of the branch where you are building the workshop as you will need it in a future step.

## Step 2: Ensure all files are present

Make sure that all the necessary files are present:

- `frontmatter.md`
- `lessons.md`
- `theory-to-practice.md`
- `assessment.md`

Without those files in the repo (and branch) that you want to use, you will not be able to work with the repository. Also, each of those files have required sections that need to be present inside them. Here is a template for each file:

## Step 3: Ensure `frontmatter.md` is correctly formatted

In `frontmatter.md` you want to add the following sections as separate headings using a double hash before them (`##`): Abstract, Learning Objectives, Estimated Time, Prerequisites, Contexts, Acknowledgments. The "Contexts" section should have subheadings for "Pre-reading Suggestions", "Projects That Use These Skills", and "Ethical Considerations".

An example of the entire file (easy to copy and paste into `frontmatter.md`) is available here:

```md
# Frontmatter

## Abstract

Abstract

## Learning Objectives

- Learning objective 1
- Learning objective 2
- Learning objective 3

## Estimated Time

10 hours.

## Prerequisites

- Title of required previous workshop

## Contexts

### Pre-reading Suggestions

- Book about R with [link](http://www.google.com)

### Projects That Use These Skills

- A project with [link](http://www.google.com)

### Ethical Considerations

- Ethical consideration 1
- Ethical consideration 2
- Ethical consideration 3

## Acknowledgements

- Role: [Firstname Lastname](<personal website>)
- Role: [Firstname Lastname](<personal website>)
- Role: [Firstname Lastname](<personal website>)
```

### `lessons.md`

```md
# Lesson 1

Lesson text

## Challenge

Challenge text

## Solution

Solution text

# Lesson 2

Lesson text

## Challenge

Challenge text

## Solution

Solution text
```

### `theory-to-practice.md`

```md
# Theory to Practice

## Suggested Further Readings

- Use bullet points for each of the sources (in markdown, you use - on a new line to create a bullet point).
- If the reading has a DOI number, make sure to add it. If it does, you do not need to add any additional bibliographic information.

## Other Tutorials

- Use bullet points for each of the sources (in markdown, you use - on a new line to create a bullet point).
- Programming Historian

## Projects or Challenges to Try

- Further exploration, possible little projects to try — can also use [links](<link>)
- Exercises from other open source tutorials

## Discussion Questions

- Discussion question 1
- Discussion question 2
- Discussion question 3
```

### `assessment.md`

```md
# Assessment

## Quantitative Self-Assessment

Add each question as a regular paragraph.

- Each question should have multiple choice answers, added as bullet points under the paragraph.
- Make sure that the questions enable the learner to evaluate their understanding of specific concepts from the workshop.

## Qualitative Self-Assessment

Add each question as a regular paragraph. These qualitative questions (of course) do not need to have answers but should enable the learner to think about what they learned and how it can be used.

- If you think of readings/tutorials/projects/challenges from the "Theory to Practice" section to direct them to, and add a note of that as a bullet point under relevant questions.
```

## Step 3: Download data to Django

```sh
$ python manage.py downloaddata --repos <repo-name>
```

It will ask for the branch name, and load everything from the repository.
