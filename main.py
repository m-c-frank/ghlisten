import subprocess
import sqlite3
import time
import logging
import json
import os

# Configuration
GITHUB_API_URL = 'https://api.github.com/repos/m-c-frank/posts/issues'
TOKEN = os.environ["GH_PAT"]
DB_PATH = 'github_issues.db'
TABLE_NAME = 'seen_issues'
POLL_INTERVAL = 600  # 10 minutes


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init_db(db_path):
    """Initializes the database and creates the table if it doesn't exist."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                issue_id TEXT PRIMARY KEY
            )
        ''')


def fetch_seen_issues(db_path):
    """Fetches seen issue IDs from the database and returns them as a set."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f'SELECT issue_id FROM {TABLE_NAME}')
        seen_issues = {row[0] for row in cursor.fetchall()}
    return seen_issues


def add_seen_issue(db_path, issue_id):
    """Adds a new seen issue ID to the database."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f'INSERT INTO {TABLE_NAME} (issue_id) VALUES (?)', (issue_id,)
        )


def fetch_new_issues(api_url, token, db_path, seen_issues):
    """
    Fetches new issues from the GitHub API and updates the seen issues.
    """
    command = f'curl -H "Authorization: token {token}" {api_url}'
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        logging.error("Failed to fetch issues from GitHub API")
        return False

    issues = json.loads(result.stdout)
    new_issues = False
    for issue in issues:
        issue_id = str(issue['id'])
        if issue_id not in seen_issues:
            logging.info(f"New issue detected: {issue['title']}")
            logging.info(f"Link: {issue['html_url']}")
            add_seen_issue(db_path, issue_id)
            seen_issues.add(issue_id)
            new_issues = True
    return new_issues


def main():
    logging.info("Initializing database...")
    init_db(DB_PATH)

    seen_issues = fetch_seen_issues(DB_PATH)
    logging.info("Starting to monitor new issues via GitHub API...")
    while True:
        new_issues_found = fetch_new_issues(
            GITHUB_API_URL, TOKEN, DB_PATH, seen_issues
        )
        if not new_issues_found:
            logging.info("No new issues found.")
        logging.info("Waiting for next check...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
