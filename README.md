# External GitHub contributors

This is a simple script to get a list of external contributors that authored commits on a
GitHub-hosted project within a range defined by two given Git references.

## Install

This project uses [Poetry](https://python-poetry.org/) to manage its dependencies. Poetry
needs to be installed in order to be able to follow the installation and usage
instructions.

Clone the repository and install the dependencies:

```commandline
git clone https://github.com/babolivier/external-github-contributors.git
cd external-github-contributors
poetry install
```

## Usage

In your local checkout of this repository, run `poetry run external_github_contributors [args]`.

A complete synopsis is available below:

```
usage: external_github_contributors [-h] --team TEAM --repo REPO [--token TOKEN] [--md] oldest_ref most_recent_ref

Simple script to list external contributors to a project who authored contributions between two specific references.

positional arguments:
  oldest_ref       The oldest of the two refs to compare.
  most_recent_ref  The most recent of the two refs to compare.

options:
  -h, --help       show this help message and exit
  --team TEAM      The team listing internal contributors to exclude. In the format ORG_NAME/teams/TEAM_SLUG.
  --repo REPO      The repository to list contributors of. In the format ORG_NAME/REPO_NAME.
  --token TOKEN    The GitHub access token to use when making request to the API. Must have the read:org scope.
                   If not provided as a command-line argument, must be in the GITHUB_TOKEN environment variable.
  --md             If provided, prints the contributors as markdown links. The text for the link is the user's
                   display name (e.g. full name) as configured in their GitHub profile. This option requires an
                   additional API call for each contributor, and therefore introduces additional delay.
```

As an example, here's a run of the script to get the list of external contributors that
committed to the [matrix-org/synapse](https://github.com/matrix-org/synapse) repository
between Synapse 1.68 and Synapse 1.69:

```
poetry run external_github_contributors --team=matrix-org/teams/core-team --repo=matrix-org/synapse v1.68.0 v1.69.0
10 external contributors found after looking at 114 commits:
- ...
```

In this example, the GitHub access token is stored in the environment.

## Contribute

Please report bugs as issues on this repository, although fixing them will be done on a
best-effort basis. Pull requests are welcome.
