# schedule-notifier

## Requirements
* Python 3.3+

## Usage
### A: Docker
* Copy `config.example.json` to `config.json`
* `docker run -it --rm -v $(pwd)/config.json:/app/config.json:ro camphor/schedule-notifier`

### B: pip
* `pip install -U .`
* Copy `config.example.json` to `config.json`
* Edit `config.json` (You can obtain Twitter API tokens from https://apps.twitter.com)
* Run `schedule-notifier`

## License
MIT License. See [LICENSE](LICENSE).
