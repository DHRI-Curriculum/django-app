# Adding a new user

## Collecting information

For each user, you will need to collect some information:

-   First name(s)
-   Last name(s)
-   Username
-   Pronouns the person uses
-   Password (this can always be changed)
-   Bio
-   Image in JPEG or PNG format (see below)
-   Any professional or personal websites to add to the profile

## Filling out the YAML file

Once you have all the information collected, you can start working in the file `_preload/user_setup.yml` where you want to add the collected information above, in a format that follows this template:

```yaml
- first_name: <First name>
  last_name: <Last name(s)>
  pronouns: <Which pronouns the person uses>
  username: usernamewithoutspacesorothercharacters
  password: <clear-text password here - which means this file should NOT be shared on the internet>
  bio: <insert bio here and make sure the text block follows YAML linting standard>
  img: _preload/user_setup/<firstname-lastname.jpg> <Also don't forget to add this file to the directory -- see below>
  groups:
      - Team <see the dhri_settings.py file and the dictionary AUTO_GROUPS to find the available groups to add here>
  blurb:
      workshop: <slug to the workshop>
      text: <blurb for the workshop>
  links:
      - text: <whatever text you want to show for the link>
        url: <a valid full URL>
        cat: <project OR personal>
```

This section needs to be added to whichever category of user you wish to add:

-   **SUPER**: Has _full_ access to the site and all the database models
-   **STAFF**: Has _backend_ access to the admin interface, but not necessarily to all the database models.
-   **USER**: Has _no_ acccess to the admin interface but is a normal "learner" on the site.

See below for an example of how the YAML file needs to be structured.

## Adding an image

**Note:** It is important to not forget to add the image file that you list in the `user_setup.yml` file to the correct directory.

## Full example of YAML file

<!--# due to #376 (see https://github.com/DHRI-Curriculum/django-app/pull/376/commits/b64d244979929d411ac61eed93506bfa48d1ab1f#diff-f82ca1e2c7413b7df7e556b6fdbbb6fee6a3e272bb2345162f567f761e6f0f34), there is a change here-->

```yaml
by_groups:

    SUPER:
        - first_name: Test
        last_name: Superuser
        username: test
        password: test
        groups:
            - Team
        pronouns: "she"

    STAFF:
        - first_name: Test
        last_name: Staffuser
        username: test
        password: test
        groups:
            - Team
        pronouns: "he"

    USER:
        - first_name: Test
        last_name: User
        username: test
        password: test
        groups:
            - Learner
        pronouns: "they"
```
