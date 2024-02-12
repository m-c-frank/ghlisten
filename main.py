import os
import listener
from comment import create_github_comment

TOKEN_POSTS = os.environ.get('GH_ISSUES_POSTS')


def newissue2md(issue):
    output = ""
    output += "---\n"
    output += f"issue_id: {issue['id']}\n"
    output += f"author: {issue['user']['login']}\n"
    output += f"timestamp: {issue['created_at']}\n"
    output += f"origin: {issue['url']}\n"
    output += "---"
    output += f"\n\n# {issue['title']}\n\n"
    output += issue["body"]
    return output


def process_new_issues(new_issues):
    for new_issue in new_issues:
        md = newissue2md(new_issue)
        create_github_comment(new_issue["url"], md, TOKEN_POSTS)
        print(md)


def main():
    listener.api(process_new_issues)


if __name__ == "__main__":
    main()
