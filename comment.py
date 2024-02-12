import requests


def create_github_comment(issue_url, text, token):
    """Post a comment to a GitHub issue.

    Args:
        issue_url: The API URL of the GitHub issue.
        body: The body text of the comment.
        token: GitHub Personal Access Token for authentication.
    """
    # Construct the comment API URL from the issue URL
    comment_url = f"{issue_url}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"body": text}
    try:
        response = requests.post(comment_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Comment posted successfully!")
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    print(f"Failed to post comment. Status code: {response.status_code}")
    print(response.text)
    return False
