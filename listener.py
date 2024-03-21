import subprocess
import sqlite3
import time
import logging
import json
import os

# Configuration
REPO = os.environ.get("REPO", "m-c-frank/posts")
GITHUB_API_URL = f'https://api.github.com/repos/{REPO}/issues'
TOKEN = os.environ["GH_PAT"]
PATH_DB = os.environ.get("PATH_DB", "issues.db")
POLL_INTERVAL = 600  # 10 minutes


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init_db(db_path):
    """Initializes the database and creates the table if it doesn't exist."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS issues (
                issue_id TEXT PRIMARY KEY,
                author TEXT,
                title TEXT,
                body TEXT,
                created_at TEXT,
                origin TEXT
            )
        ''')


def get_stored_issue_ids(db_path):
    """Fetches seen issue IDs from the database and returns them as a set."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f'SELECT issue_id FROM issues')
        seen_issues = {row[0] for row in cursor.fetchall()}
    return seen_issues


def insert_issue(db_path, issue):
    """Adds a new seen issue ID to the database."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f'''
            INSERT INTO issues (
                issue_id,
                author,
                title,
                body,
                created_at,
                origin
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                issue["id"],
                issue["user"]["login"],
                issue["title"],
                issue["body"],
                issue["created_at"],
                issue["url"],
            )
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
    new_issues = []
    for issue in issues:
        issue_id = str(issue['id'])
        if issue_id not in seen_issues:
            logging.info(f"New issue detected: {issue['title']}")
            logging.info(f"Link: {issue['html_url']}")
            insert_issue(db_path, issue)
            seen_issues.add(issue_id)
            new_issues.append(issue)
    return new_issues


def api(callback_fn):
    logging.info("Initializing database...")
    init_db(PATH_DB)

    seen_issues = get_stored_issue_ids(PATH_DB)
    print("seen issues: " + str(seen_issues))
    logging.info("Starting to monitor new issues via GitHub API...")
    while True:
        new_issues = fetch_new_issues(
            GITHUB_API_URL, TOKEN, PATH_DB, seen_issues
        )
        print("new issues: " + str(new_issues))
        if not new_issues:
            logging.info("No new issues found.")
        else:
            callback_fn(new_issues)
        logging.info("Waiting for next check...")
        time.sleep(POLL_INTERVAL)


def main():
    callback_function = print
    api(callback_function)


if __name__ == "__main__":
    main(print)
