# Virtual Meter Home Assistant Add-on Repository

![Python Version][python-badge]
[![OpenSSF Scorecard report][ossf-scr-badge]][ossf-scr-link]
[![codecov][codecov-badge]][codecov-link]
[![CodeQL][codeql-badge]][codeql-link]
[![Dependabot Updates][dependabot-badge]][dependabot-link]
[![SonarCloud Analysis][sonarcloud-badge]][sonarcloud-link]
[![MegaLinter][megalinter-badge]][megalinter-link]

This repository hosts the Virtual Meter Home Assistant add-on (`virtual-meter/`).
The add-on provides a Shelly Pro 3EM (Gen2) emulator so that Hoymiles 1920 AC
battery owners can control battery charge and discharge based on grid
consumption data.

[![Add repository on my Home Assistant][repository-badge]][repository-url]

## Layout

```text
.
├── tests/                          # Unit tests
├── virtual-meter/                  # Add-on root
│   ├── app/                        # Add-on application code
│   │   ├── assembler.py            # Payload assembly from provider data
│   │   ├── cache.py                # In-memory payload cache
│   │   ├── config.py               # Settings loader
│   │   ├── consumer.py             # Polling client
│   │   ├── identity.py             # Device ID/MAC helpers
│   │   ├── main.py                 # Entry point
│   │   ├── mdns.py                 # mDNS/zeroconf broadcaster
│   │   ├── payload_templates.py    # Static payload templates
│   │   ├── provider.py             # JSON-RPC server
│   │   └── serializer.py           # JSON codec helpers
│   ├── translations/               # Localized strings for the HA UI
│   ├── build.yaml                  # Base image pin per architecture
│   ├── CHANGELOG.md                # User-facing release notes rendered in HA
│   ├── config.yaml                 # Supervisor metadata & schema
│   ├── Dockerfile                  # Add-on Dockerfile
│   ├── DOCS.md                     # Documentation tab content
│   ├── icon.png / logo.png         # Store badges/icons
│   ├── README.md                   # Add-on specific developer notes
│   ├── requirements.txt            # Add-on runtime dependencies
│   └── run.sh                      # Entry script
├── README.md                       # This file
└── repository.yaml                 # Supervisor store metadata for this repo
```

## Contributing

1. Fork/clone this repository.
2. Update `repository.yaml` with your GitHub URL if you plan to publish under a
  different namespace.
3. Push changes to `main`.
4. (Optional) Add the repository URL to **Settings → Add-ons → Repositories**
  inside Home Assistant for local testing.

For full configuration, upgrade, and troubleshooting guidance refer to `virtual-meter/DOCS.md`.

## CI / QA

- `dependency-review.yml`: dependency change auditing on PRs.
- `megalinter.yml`: linting + SBOM generation on PRs and main.
- `scorecard.yml`: OpenSSF Scorecard analysis on main.
- `tests.yml`: unit test execution on PRs and main.
- `dependabot.yml` and `renovate.json`: automated dependency updates.

<!-- markdownlint-disable MD013 -->
[codecov-badge]: <https://codecov.io/gh/boecht/ha-addon-virtual-meter/branch/main/graph/badge.svg>
[codecov-link]: <https://codecov.io/gh/boecht/ha-addon-virtual-meter>
[codeql-badge]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/github-code-scanning/codeql/badge.svg>
[codeql-link]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/github-code-scanning/codeql>
[dependabot-badge]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/dependabot/dependabot-updates/badge.svg>
[dependabot-link]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/dependabot/dependabot-updates>
[megalinter-badge]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/megalinter.yml/badge.svg>
[megalinter-link]: <https://github.com/boecht/ha-addon-virtual-meter/actions/workflows/megalinter.yml>
[ossf-scr-badge]: <https://api.scorecard.dev/projects/github.com/boecht/ha-addon-virtual-meter/badge>
[ossf-scr-link]: <https://scorecard.dev/viewer/?uri=github.com/boecht/ha-addon-virtual-meter>
[python-badge]: <https://img.shields.io/badge/python-3.14%2B-blue>
[repository-badge]: <https://img.shields.io/badge/Add%20repository%20to%20my-Home%20Assistant-41BDF5?logo=home-assistant&style=for-the-badge>
[repository-url]: <https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fboecht%2Fha-addon-virtual-meter>
[sonarcloud-badge]: <https://sonarcloud.io/api/project_badges/measure?project=boecht_ha-addon-virtual-meter&metric=alert_status>
[sonarcloud-link]: <https://sonarcloud.io/summary/new_code?id=boecht_ha-addon-virtual-meter>
<!-- markdownlint-enable MD013 -->
