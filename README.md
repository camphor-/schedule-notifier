# schedule-notifier

## Requirements
* Python 3.3+

## Usage
### Common
* Copy `config.example.json` to `config.json`
* Edit `config.json` (You can obtain Twitter API tokens from https://apps.twitter.com)

### A: Docker
* `docker run -it --rm -v $(pwd)/config.json:/app/config.json:ro camphor/schedule-notifier`

### B: pip
* `pip install -U .`
* Run `schedule-notifier`

For more information, run `schedule-notifier --help`

## License
MIT License. See [LICENSE](LICENSE).
