import requests
from dotenv import load_dotenv
import inquirer
import os
import io
import psycopg2
import json
import time


load_dotenv()

SLEEP_TIME_BETWEEN_CALLS = 1


def get_env_var(env_var_name, prompt_message):
    env_var = os.getenv(env_var_name)
    if not env_var:
        questions = [inquirer.Text("env_var", message=prompt_message)]
        answers = inquirer.prompt(questions)
        return answers["env_var"]
    return env_var


def get_projecs_and_orgs(db_host, db_name, db_username, db_password, db_port):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )
    query = """
        SELECT proj."id" as proj_id, proj."name" as repo, org."id" as org_id, proj."owner" as owner, org."provider" as provider  FROM "Project" AS proj
        LEFT JOIN "Teams_Organization" AS org ON (proj."organizationId"=org.id)
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    projects = []
    for row in rows:
        row_dict = {
            "proj_id": row[0],
            "repo": row[1],
            "org_id":row[2],
            "owner": row[3],
            "provider": row[4]            
        }
        projects.append(row_dict)
    conn.close()
    return projects


def get_commits_with_coverage(db_host, db_name, db_username, db_password, db_port):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )
    query = """
        SELECT cc."commitId" as commitId, cc."fileId" as fileId, cc."coverage" as coverage,
        c."uuid" as uuid, RFD."projectId", "language",
        "filename", "total"
        FROM "Coverage_Coverage" AS CC
        LEFT JOIN "Result_File" AS RF ON (CC."fileId"=RF.id)
        LEFT JOIN "Result_FileData" AS RFD ON (RF."fileDataId"=RFD.id)
        LEFT JOIN "Commit" AS c on (CC."commitId"=c.id);
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    commits = {}
    for row in rows:
        commitId = row[0]
        coverage = row[2]
        projectId = row[4]
        uuid = row[3]
        language = row[5]
        filename = row[6]
        total = row[7]
        
        if commitId not in commits.keys():
            commits[commitId] = {
                "projectId": projectId,
                "uuid": uuid,
                "languages": {},
            }
        if language not in commits[commitId]["languages"].keys():
            commits[commitId]["languages"][language] = []
        commits[commitId]["languages"][language].append(
            {
                "filename": filename,
                "total": total,
                "coverage": coverage
            }
        )
    conn.close()
    
    return commits


def generate_coverage_payload_for_commit(commit):
    report = {
        "total": 0,
        "fileReports": list(
            map(
                lambda x: {
                    "filename": x["filename"],
                    "total": x["total"],
                    "coverage": json.loads(x["coverage"]),
                },
                commit,
            )
        ),
    }
    return report


def post_coverage_to_codacy(api_token, provider, owner, repo, uuid, language, payload):
    """
    Posts coverage data to Codacy.

    Parameters:
    - api-token (str): Your Codacy API account token
    - commit_uuid (str): The commit UUID for which the coverage data is relevant.
    - coverage_data (str): The coverage data in a format accepted by Codacy (e.g., base64 encoded report).

    Returns:
    - response (requests.Response): The response from the Codacy API.
    """

    url = f"https://api.codacy.com/2.0/{provider}/{owner}/{repo}/commit/{uuid}/coverage/{language}"
    headers = {
        "api-token": api_token,
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    return response


def main():
    api_token = get_env_var("CODACY_API_TOKEN", "Your Codacy API Token")
    db_host = get_env_var("DB_HOST", "Your Postgres DB Host")
    db_username = get_env_var("DB_USERNAME", "Your Postgres DB Password")
    db_password = get_env_var("DB_PASSWORD", "Your Postgres DB Password")
    db_analysis_name = get_env_var("DB_ANALYSIS_NAME", "Your Postgres Analsyis DB Name")
    db_accounts_name = get_env_var("DB_ACCOUNTS_NAME", "Your Postgres Accounts DB Name")
    db_port = get_env_var("DB_PORT", "Your Postgres DB Port")
    
    
    projects = get_projecs_and_orgs(db_host, db_accounts_name, db_username, db_password, db_port)
    commits = get_commits_with_coverage(db_host, db_analysis_name, db_username, db_password, db_port)
    for key in commits.keys():
        project = next((x for x in projects if x["proj_id"] == commits[key]['projectId']), None)
        if project == None:
            print("No project was found for this commit")
            continue # Best Effort Approach
        provider = project['provider']
        owner = project['owner']
        repo = project['repo']
        uuid = commits[key]["uuid"]
        print(f'Processing Coverage for commit {uuid} on repo {repo}')
        for language in commits[key]["languages"].keys():
            report = generate_coverage_payload_for_commit(
                commits[key]["languages"][language]
            )
            post_coverage_to_codacy(
                api_token, provider, owner, repo, uuid, language, report
            )
        print(f'Taking a breath for {SLEEP_TIME_BETWEEN_CALLS} second(s)')
        time.sleep(SLEEP_TIME_BETWEEN_CALLS)


if __name__ == "__main__":
    main()
