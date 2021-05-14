# Digital Humanities Research Institute's curriculum website (Django)

[![Build Status](https://travis-ci.com/DHRI-Curriculum/django-app.svg?token=qsoYACcVqJuqMoXfJy84&branch=v1-dev)](https://travis-ci.com/DHRI-Curriculum/django-app)

This is the version 1.0.0 development branch of the DHRI's Curriculum Website.

See [Documentation](https://github.com/kallewesterling/django-app-documentation/blob/main/django-app-docs/README.md) for documentation.

---

## Roadmap

The app is likely to be a "perpetual beta" app, which means that in its lifespan, it will feed into the public branch.

### [Current backlog: v1.0-dev](https://github.com/DHRI-Curriculum/django-app/milestone/11)

_The features listed here are all being actively worked on right now._

—

### Product backlog: [v1.0-beta1](https://github.com/DHRI-Curriculum/django-app/milestone/10)

_The features listed here are all featured with concrete outcomes and clearly defined scopes. If they do not have outcomes and scopes clearly defined, they should be reclassified as `v1.0` features, which should be considered the [product backlog](https://www.scrum.org/resources/what-is-a-product-backlog) of the "final" version 1.0_.

**[Add new assessment model: ExitSlip (and related models) enhancement (**#364**)](https://github.com/DHRI-Curriculum/django-app/issues/364)**  
Self-assessment is currently automatically generated on the Theory to Practice page, but the idea here is to build out something more like the exit slip system that we have used as part of the DHRI model, which could be generalized and then connected up to the idea of institutes running this site as part of their own instances, which could then be used to consolidate data about the system being run in different locales (#226). That's more for blue skies dev though. In this issue, for v1.0 beta, we had envisioned the idea of being able to automate the exit slip work through, say, the introduction of an `ExitSlip` model that ties in with the `Question` model that we already have set up.

**[Revisit how to send comments / updates (**#330**)](https://github.com/DHRI-Curriculum/django-app/issues/330)**  
This issue was dependent on re-opening registration ability (#348), which has since been closed—thus ready to be tested and updated to have better integrated functionality. Perhaps this should be marked more as a v1.0 feature, but it should be fairly simple to implement and test it.

**[Revisit/redesign image saving in ingestion enhancement (**#316**)](https://github.com/DHRI-Curriculum/django-app/issues/316)**  
This is a continuation of an earlier issue, #291, which was resolved, but "feels patched" and needs some revisit and some more love and care. The image ingestion could be a more elegant solution than it currently is.

**[Set up MySQL database again (**#313**)](https://github.com/DHRI-Curriculum/django-app/issues/313)**  
During an earlier development phase, we test-ran the MySQL to make sure it worked, and it did. Since then, when we went into the first virtual DHRI in Winter 2020, we switched back to a sqlite solution. It would be ideal, especially if the platform grows more, to transition the backend to MySQL.

### Product backlog: [v1.0](https://github.com/DHRI-Curriculum/django-app/milestone/3)

_The features listed here are long-term goals without concrete outcome. They will all need more in-depth work._

**[Make installation instructions more present early in Lessons (**#253**)](https://github.com/DHRI-Curriculum/django-app/issues/253)**  
We might want to make it clearer—more visible and present throughout—in the beginning of each workshop, linking the learner to installation instructions in case they need them. A reminder or a "pre-flight check," of sorts, before a learner embarks on their workshop, that they have installed all the prerequisites, etc. Right now, prerequisites really work as "recommended"—what if it was presented as a checklist that you have to check off before you start?

**[Go over all and ensure that workshops' resources have descriptive elements content enhancement (**#281**)](https://github.com/DHRI-Curriculum/django-app/issues/281)**  
_This is a frontend/editing issue._ All "resources" (readings, tutorials, projects, etc.) that have links, should all have _descriptive text_ as its link text, and preferably have an explanatory text that follows the reference/link, with more information _why_ the learner should click the link. Since it's all pulled into the library page, separate from the workshop, it would be great if this content could live on its own.

**[Build test cases for all models and views (**#225**)](https://github.com/DHRI-Curriculum/django-app/issues/225)**  
For a finished product, v1.0, we would like to have models and views running through the built-in Django `Test` classes, especially if we're thinking about moving ahead with a Docker solution or something similar in a future version.

### Product backlog: [v2.0](https://github.com/DHRI-Curriculum/django-app/milestone/7)

_Currently in blue skies research mode. The features listed here are all potential future modules and/or wishlist items._

**[Build code-runner app (**#89**)](https://github.com/DHRI-Curriculum/django-app/issues/89)**  
We have discussed that, at some point, the Curriculum website should have a "code runner" (like [REPL.it](https://repl.it/)) and perhaps inspired by [Sphinx Thebelab](https://sphinx-thebelab.readthedocs.io). This is a long build process ahead.

**[Difficulty levels (**#90**)](https://github.com/DHRI-Curriculum/django-app/issues/90)**  
At a very early stage of the DHRI development process, we discussed whether to be able to offer learners "difficulty levels." We decided to deal with it in the content/description instead at the time, but left a case open for a potential future case where we could have difficulty levels in the app. (see #25)

**[Tracks app (**#139**)](https://github.com/DHRI-Curriculum/django-app/issues/139)**  
A part of the interface that made sure certain workshops were connected in a "track," that the learner could choose to follow. They could also be "branded" as certain institutes, or parts of the institute (Python/R track, for instance).

**[Humanities Commons integration (**#128**)](https://github.com/DHRI-Curriculum/django-app/issues/128)**  
Started groundwork, but a lot of future development to be done here, to integrate Humanities Commons into our project and our site. A potential way to do so is using the website's integration of `wp-json` which has already been experimented as a collaborating agent with Django. See the issue for more detail.


**[Build admin interface (**#222**)](https://github.com/DHRI-Curriculum/django-app/issues/222)**  
As of v1.0, the admin interface of the Curriculum website uses Django's built-in administration interface. In the future, we likely want to build out our own administrative interface, that allows for different users with different views/access (learners, institute organizers/community leaders, their collaborators, teaching fellows, super admins, etc.).

**[Institutes app (**#223**)](https://github.com/DHRI-Curriculum/django-app/issues/223)**  
Groundwork laid here for an `Institutes` model in an app, that could be used to style the website with certain accent colors, etc. This is also what could connect the `Track` idea (see #139) as well as create new user groups, etc. (see description above for #222 for ideas).

**[Integrate a Slack feature (**#226**)](https://github.com/DHRI-Curriculum/django-app/issues/226)**  
Depending on whether we want to build out the community component based on Slack or on Mattermost, we'll need to think further on this. If we want hooks to tie in with the website, the Mattermost API is likely a better way to go, although the Slack API seems to be pretty OK too. These things can change, especially considering that Slack is for-profit and will likely close down API access in different way.s

**[API app enhancement (**#243**)](https://github.com/DHRI-Curriculum/django-app/issues/243)**  
Using the [Django REST framework](https://www.django-rest-framework.org/), the Curriculum website would likely benefit, speed-wise, from being built as a backend API + frontend ES6 framework, like React. This would entail a lot of re-programming of the site, and rethinking of its infrastructure, but it would be really cool, and could also enable us to move into an [Electron app](https://www.electronjs.org/), which opens a whole lot of other doors.
