# schedule-notifier
[![Build Status](https://travis-ci.org/camphor-/schedule-notifier.svg?branch=master)](https://travis-ci.org/camphor-/schedule-notifier)
[![Requirements Status](https://requires.io/github/camphor-/schedule-notifier/requirements.svg?branch=master)](https://requires.io/github/camphor-/schedule-notifier/requirements/?branch=master)

## Requirements
* Python 3.6+

## Usage
You must set credential for Twitter:
* By command line options: `--api-key`, `--api-secret`, `--access-token`,
  and `--access-token-secret`
* Or, by environment variables: `CSN_API_KEY`, `CSN_API_SECRET`,
  `CSN_ACCESS_TOKEN`, and `CSN_ACCESS_TOKEN_SECRET`

### A: Docker
* `docker run -it --rm camphor/schedule-notifier`

### B: pip
* `pip install -U .`
* Run `schedule-notifier`

For more information, run `schedule-notifier --help`

## Test
* Install: `pip install -U -e '.[test]'`
* Run tests: `tox`

## Publish image to docker hub

DockerHub automatically builds a new image from source code in this repositry when new commits are pushed to `master` branch.
See https://docs.docker.com/docker-hub/builds/ for more information.

## License
MIT License. See [LICENSE](LICENSE).
