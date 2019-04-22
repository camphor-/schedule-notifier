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

## Development
Development environment can be created using [pipenv](https://github.com/pypa/pipenv)
* `pipenv install`
* `pipenv shell`
* Run `schedule-notifier`

If any dependencies are added, run `pipenv install -e .` to regenerate `Pipenv.lock`.

## Test
* Install: `pipenv install --dev'`
* Run tests: `pipenv run tox`

## License
MIT License. See [LICENSE](LICENSE).
