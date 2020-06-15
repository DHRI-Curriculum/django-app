# parse_json

**`parse_json`** is a pre-processing Python script that runs on the command line and helps set up the data for the second project, the **app** (see below). `parse_json` is designed to integrate with the curriculum transition and quickly populate the Django database.

## Getting started

Because the DHRI workshops are currently in transition, the script does not work in production but can be tested on a "model workshop," which is available here: https://github.com/kallewesterling/dhri-test-repo.

In order to test out the tool, follow these steps:

1. Clone this repository:

   ```
   git clone https://github.com/DHRI-Curriculum/django-app
   ```

2. Navigate into the repository:

   ```
   cd django-app
   ```

3. Run parse_json:

   ```
   python parse_json --download https://github.com/kallewesterling/dhri-test-repo
   ```

   Once we are in production, the point will be to quickly populate the database with the most recent information from a live repository on GitHub but for now we have to work with this sample data.

   **Optionally**, you may add another parameter to the script choosing the filename for the resulting data file. It will default to workshop.json.

   ```
   python parse_json --download https://github.com/kallewesterling/dhri-test-repo --dest workshop.json
   ```

The script is fairly vocal in its output, and will guide you in moving forward. Once the script has downloaded the file, you can choose to continue to work with the same file.

If you choose to exit the script, you can always work with local data by running:

  ```
  python parse_json --file workshop.json
  ```

## Notes

- The script has not yet been tested for compatibility but works in development on Mac OS Catalina (10.15.4) and Python 3.8.0.
