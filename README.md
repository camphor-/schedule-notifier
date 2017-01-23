# schedule-notifier
[![Build Status](https://travis-ci.org/camphor-/schedule-notifier.svg?branch=master)](https://travis-ci.org/camphor-/schedule-notifier)

## Requirements
* Python 3.5+

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

## License
MIT License. See [LICENSE](LICENSE).
