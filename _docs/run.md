# Run Server

You are now all done. You can run the server by running this command:

```
python manage.py runserver
```

_It will automatically create a development server for you, and you should be able to now navigate to http://localhost:8000 (or its alias http://127.0.0.1:8000) in a browser on your computer._

## Optional: Enable Access on Local Network (Advanced)

If you want to make your development server accessible through your local network, instead of the command in the Run Server section above, run the following command:

```
python manage.py localserver
```

Note that `localserver` is a custom-made script for the `backend` app here, and _not_ a native Django command.

## Optional: Adjust Settings

The script above might give you a warning that notifies you that `'*'` has been added to `ALLOWED_HOSTS`. You can rectify that by following these two steps:

- Edit the file `django-app/app/app/settings.py`

- Find the line that reads:

   ```py
   ALLOWED_HOSTS = []
   ```

   ...and change it to:

   ```py
   ALLOWED_HOSTS = ['*']
   ```

### Continue install track

[<< Previous step](populate.md) | [Back to repo >>](https://github.com/DHRI-Curriculum/django-app/tree/alpha-3)