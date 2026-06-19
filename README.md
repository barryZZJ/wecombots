# wecombots

`wecombots` is a collection of small automation tools that send status,
monitoring, RSS, and check-in results to WeCom through
[wecomsan](https://github.com/barryZZJ/wecomsan).

Most folders are standalone scripts with their own `config.py` or
`config_template.json`. Treat live `config.json` files as secrets because they
may contain WeCom app credentials, website account passwords, cookies, internal
hosts, or service URLs.

## Repository layout

| Path | Purpose                                                                                                              |
| --- |----------------------------------------------------------------------------------------------------------------------|
| `checkin_helper/` | Modular website check-in runner with retry/reporting logic and captcha-related helpers (such as order click captcha). |
| `freshrsscrawler/` | FreshRSS Fever API crawler that forwards unread items to WeCom bot and marks successful items as read.               |
| `connectivity_test/` | Minimal WeCom connectivity smoke test via wecomsan.                           |
| `crontab_manager/` | Small CLI package for registering, unregistering, and listing Python scripts in user crontab.                        |
| `frpc_monitor/` | TCP port monitor for an FRP/FRPC-style service endpoint.                                                             |
| `rss_monitor/` | RSS endpoint availability monitor.                                                                                   |
| `rsspush_adapter/` | Flask adapter that receives RSSPush-style webhooks and forwards them to WeCom.                                       |

## Common pattern

Most scripts follow the same structure:

1. Load JSON config with a local `config.py`.
2. Instantiate `wecomsan.WecomSan(**conf['bot'])`.
3. Run one check, crawl, webhook, or adapter task.
4. Send a WeCom message only on useful events, failures, or configured debug
   output.

The common WeCom config shape is:

```json
{
  "bot": {
    "cid": "corp id",
    "aid": "agent id",
    "secret": "app secret"
  }
}
```

## Subprojects

### `checkin_helper`

Automates daily sign-in/check-in flows for supported websites and reports the
result to WeCom.

Main files:

- `main.py`: loads config, chooses enabled modules, and runs checkers in a
  `ThreadPoolExecutor`.
- `checker.py`: defines `BaseChecker`, retry behavior, error handling, and
  WeCom reporting.
- `modules/`: site-specific checkers.
- `OrderClickCaptchaSolver/`: captcha-solving code and model files.
- `run_checker.sh`: Linux helper that activates a virtualenv and runs
  `main.py`.
- `requirements.txt`: key dependencies for this subproject.

Configured modules visible in `config_template.json`:

- `doki8`
- `yuyun`
- `nssctf`
- `ctfhub`

Run from the folder:

```bash
python3 main.py
```

The config supports a `debug` field. When set, `main.py` runs only that named
module instead of all enabled modules.

### `freshrsscrawler`

Polls a FreshRSS Fever API endpoint for unread articles, forwards matching
items to WeCom, and marks successful items as read.

Main files:

- `freshrss_crawler/main.py`: crawler logic, CLI, alert state handling, item
  forwarding, and FreshRSS read-state updates.
- `freshrss_crawler/freshrssapi/`: bundled Fever API wrapper.
- `templates/rss_template.html`: optional HTML template for uploaded temporary
  media.
- `config_template.json`: crawler config template.
- `README.md`: detailed documentation generated for this subproject.

Run with default config:

```bash
python3 -m freshrss_crawler.main
```

Run with a specific config:

```bash
python3 -m freshrss_crawler.main -c config_notifychan.json
```

See `freshrsscrawler/README.md` for the detailed behavior and data-file notes.

### `connectivity_test`

Sends a simple `test` message through WeCom to confirm the `wecomsan`
credential/config path is working.

Main files:

- `main.py`: sends the test message.
- `config_template.json`: minimal bot credential template.
- `run.sh`: shell helper.

Run:

```bash
python3 main.py
```

### `crontab_manager`

Small Python package for managing cron entries for Python scripts.

Main files:

- `crontab_manager/crontab_manager.py`: implementation and CLI argument
  parsing.
- `crontab_manager/__main__.py`: module entry point.
- `setup.py`: package metadata and `python-crontab` dependency.

Examples:

```bash
python3 -m crontab_manager.crontab_manager path/to/script.py --register --interval 20
python3 -m crontab_manager.crontab_manager path/to/script.py --list
python3 -m crontab_manager.crontab_manager path/to/script.py --unregister
```

The registered cron command has the form:

```text
python3 <absolute script path>
```

### `frpc_monitor`

Checks whether a configured TCP host/port is reachable and sends WeCom alerts
when it is down.

Main files:

- `frpc_monitor.py`: loads config, checks the port, and sends WeCom messages.
- `check_port_open.py`: socket-based TCP reachability check.
- `config.py`: JSON config loader.
- `register`, `unregister`, `list`: cron helper wrappers.

Expected config shape from the code:

```json
{
  "bot": {
    "cid": "",
    "aid": "",
    "secret": ""
  },
  "debug": false,
  "check": {
    "host": "example.com",
    "port": 12345,
    "timeout_seconds": 10
  }
}
```

Run:

```bash
python3 frpc_monitor.py
```

Behavior:

- Sends an alert when `host:port` cannot be opened.
- In debug mode, also sends a success message when the port is open.

### `rss_monitor`

Checks a list of RSS-related routes under a configured base URL and sends a
WeCom message when any route is unavailable.

Main files:

- `rss_monitor.py`: status aggregation and WeCom reporting.
- `check_rss_available.py`: HTTP GET availability check.
- `config.py`: JSON config loader.
- `register`, `unregister`, `list`: cron helper wrappers.
- `upload.bat`: Windows helper script.

Expected config shape from the code:

```json
{
  "bot": {
    "cid": "",
    "aid": "",
    "secret": ""
  },
  "debug": false,
  "check_url": "http://example.com",
  "routes": [
    {
      "path": "/rss/path",
      "timeout_seconds": 10
    }
  ]
}
```

Run:

```bash
python3 rss_monitor.py
```

Behavior:

- Sends a WeCom message only when at least one route fails.
- In debug mode, includes available routes in the status output.

### `rsspush_adapter`

Runs a small Flask server that accepts RSSPush-style form posts and forwards
the update to WeCom.

Main files:

- `rsspush_adapter.py`: Flask app and webhook handling.
- `config.py`: JSON config loader.
- `start`: shell helper.

Route:

```text
POST /
```

Expected form fields:

- `title`
- `desp`
- `link`
- `task_id`
- `task_title`

Run:

```bash
python3 rsspush_adapter.py
```

Default server:

```text
http://127.0.0.1:12345/
```

On success, it returns:

```json
{"message": "Success"}
```

## Scheduling

Several folders include `register`, `unregister`, and `list` wrappers intended
to work with `crontab_manager`. The crawler/checker scripts are one-shot jobs,
so they are suitable for cron or systemd timers.

Typical examples:

```bash
python3 -m crontab_manager.crontab_manager rss_monitor/rss_monitor.py --register --interval 20
python3 -m crontab_manager.crontab_manager frpc_monitor/frpc_monitor.py --register --interval 5
```

## Security notes

- Do not commit live `config.json` files.
- Do not commit session cookies, WeCom secrets, FreshRSS API passwords, or
  website account credentials.
- `checkin_helper` contains browser automation, cookies, and model files; keep
  it isolated from public deployment environments.
- Some checks call external websites and APIs directly. Run them only from an
  environment where those credentials and network requests are expected.
