#  Copyright 2022 Brendan Abolivier
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import argparse
import json
import os
import sys

import requests

# Maximum number of team members to request for a single page. GitHub sets this limit to
# 100, and since we want to get all the team members let's just use the maximum value.
MAX_TEAM_MEMBERS_PER_PAGE = 100


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Simple script to list external contributors to a project who authored"
            " contributions between two specific references."
        ),
    )
    parser.add_argument(
        "oldest_ref",
        help="The oldest of the two refs to compare.",
    )
    parser.add_argument(
        "most_recent_ref",
        help="The most recent of the two refs to compare.",
    )
    parser.add_argument(
        "--team",
        action="store",
        help=(
            "The team listing internal contributors to exclude. In the format"
            " ORG_NAME/teams/TEAM_SLUG."
        ),
        required=True,
    )
    parser.add_argument(
        "--repo",
        action="store",
        help="The repository to list contributors of. In the format ORG_NAME/REPO_NAME.",
        required=True,
    )
    parser.add_argument(
        "--token",
        action="store",
        help=(
            "The GitHub access token to use when making request to the API. Must have the"
            " read:org scope. If not provided as a command-line argument, must be in the"
            " GITHUB_TOKEN environment variable."
        ),
    )

    args = parser.parse_args()

    # Get the GitHub access token
    github_token = args.token
    if github_token is None:
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token is None:
            print(
                "Missing GitHub API token, provide it either with the --token command"
                " line argument or the GITHUB_TOKEN environment variable",
                file=sys.stderr,
            )
            exit(1)

    # Build the URLs we'll need for API requests.
    compare_url = f"https://api.github.com/repos/{args.repo}/compare/{args.oldest_ref}...{args.most_recent_ref}"
    team_members_url = f"https://api.github.com/orgs/{args.team}/members?per_page={MAX_TEAM_MEMBERS_PER_PAGE}&page=%(page)d"

    # Get the list of commits between the two refs.
    res = requests.get(compare_url)
    if res.status_code != 200:
        print(
            "GitHub API responded to /compare request with non-200 status %d and message: %s"
            % (res.status_code, res.content["message"]),
            file=sys.stderr,
        )
        exit(1)

    # Get the author's login for each commit.
    commits = json.loads(res.content)["commits"]
    contributors = {
        commit["author"]["login"]
        for commit in commits
        # Filter out bots.
        if commit["author"]["type"] == "User"
    }

    # Set of members of the given team.
    members = set()

    # Initial conditions for the pagination loop.
    last_count = MAX_TEAM_MEMBERS_PER_PAGE
    page = 1
    # Paginate through team members
    while last_count == MAX_TEAM_MEMBERS_PER_PAGE:
        # Get a new page of the members list for this team.
        url = team_members_url % {"page": page}
        res = requests.get(url, headers={"Authorization": f"Bearer {github_token}"})
        if res.status_code != 200:
            print(
                f"GitHub API responded to /members request with non-200 status"
                f" {res.status_code} and message: {res.content['message']}",
                file=sys.stderr,
            )
            exit(1)

        # Store the members of the team.
        raw_members = json.loads(res.content)
        members.update({member["login"] for member in raw_members})

        page += 1
        last_count = len(raw_members)

    # Figure out which are the external contributors. These are all the contributors who
    # are not a team member.
    external_contributors = contributors - members

    # Print a message if no external contributor could be found.
    if len(external_contributors) == 0:
        print(f"No external contributors found after looking at {len(commits)} commits")
        exit(0)

    # Print external contributors if we could find any.
    print(
        f"{len(external_contributors)} external contributors found after looking at"
        f" {len(commits)} commits:"
    )

    for contributor in external_contributors:
        print(f"- {contributor}")


if __name__ == "__main__":
    main()