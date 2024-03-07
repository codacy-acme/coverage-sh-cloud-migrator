
# Codacy Coverage SH to Cloud Migrator

This script facilitates the collection and reporting of code coverage data from a PostgreSQL database to Codacy. It uses environment variables for configuration, interacts with databases, and posts data to Codacy via its API.

## Features

- Load necessary configurations from environment variables.
- Query projects and organizations from a PostgreSQL database.
- Generate coverage payload.
- Post coverage data to Codacy API for specific commits and languages.

## Requirements

- Python 3.x
- `requests` library for API calls.
- `dotenv` library for loading environment variables.
- `inquirer` library for interactive prompts.
- `psycopg2` library for PostgreSQL database interaction.
- `json` libraries for file and data handling.

## Setup

1. **Install Dependencies:**

   Ensure you have Python 3.x installed, then install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**

   Create a `.env` file in the root directory of the project and define the following variables:

   - `CODACY_API_TOKEN`: Your Codacy API token.
   - Database credentials (if you are using the database functionality):
     - `DB_ANALYSIS_NAME`: The name of your analysis database.
     - `DB_ACCOUNTS_NAME`: The name of your accounts database.
     - `DB_USERNAME`: Your database username.
     - `DB_PASSWORD`: Your database password.
     - `DB_HOST`: Your database host.
     - `DB_PORT`: Your database port.

   Example:

   ```
   DB_HOST=yourdbserver
   DB_ANALYSIS_NAME=analysis
   DB_ACCOUNTS_NAME=accounts
   DB_USERNAME=codacy
   DB_PASSWORD=db_password
   CODACY_API_TOKEN=aperfectsolidtoken
   DB_PORT=5432
   ```


## Usage

To run the script, navigate to the directory containing the script and execute:

```bash
python main.py
```

Follow any on-screen prompts to provide missing environment variables interactively.

## How It Works

- The script first loads configuration values from environment variables.
- It then optionally queries a PostgreSQL database for projects and organizations.
- Commits and coverage data are read from a specified CSV file.
- For each commit, a coverage payload is generated and posted to the Codacy API for the specified project, repository, and language.

## Contributing

Feel free to fork the repository and submit pull requests.
