# App-specific settings

Required files to add for the app to run:

## Super important: Setting environment variables (or using backup solution)

The app requires four environment variables to be set in your environment:

- `SECRET_KEY`: Django's own secret keys, which you can read more about [here](https://humberto.io/blog/tldr-generate-django-secret-key/)
- `EMAIL_HOST_USER`: Username for login to the email host
- `EMAIL_HOST_PASSWORD`: Password for login to the email host
- `GITHUB_TOKEN`: GitHub token to use for Markdown conversion

If you are not able to set environment variables correctly, there is a built-in backup solution.

1. Create a directory called `.secrets` inside the `app` directory.
2. In there, place each of the environment variables as a file, with _only_ the variable in each file. Note: No file ending should exist on these files:
    ```
    app
      |-- secrets
          |-- SECRET_KEY
          |-- EMAIL_HOST_USER
          |-- EMAIL_HOST_PASSWORD
          |-- GITHUB_TOKEN
    ```
