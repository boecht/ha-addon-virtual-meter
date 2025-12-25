# Virtual Meter Home Assistant Add-on Repository

This repository hosts the Virtual Meter Home Assistant add-on (`virtual-meter/`).
The add-on provides a Shelly Pro 3EM (Gen2) emulator so that Hoymiles 1920 AC
battery owners can control battery charge and discharge based on grid
consumption data.

[![Add repository on my Home Assistant][repository-badge]][repository-url]

## Layout

```text
.
├── virtual-meter/
│   ├── app/                        # Add-on application code
│   ├── apparmor.txt                # Add-on AppArmor profile
│   ├── build.yaml                  # Base image pin per architecture
│   ├── CHANGELOG.md                # User-facing release notes rendered in HA
│   ├── config.yaml                 # Supervisor metadata & schema
│   ├── Dockerfile                  # Add-on Dockerfile
│   ├── DOCS.md                     # Documentation tab content
│   ├── icon.png / logo.png         # Store badges/icons
│   ├── README.md                   # Add-on specific developer notes
│   ├── run.sh                      # Entry script
│   └── translations/               # Localized strings for the HA UI
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

<!-- markdownlint-disable MD013 -->
[repository-badge]: <https://img.shields.io/badge/Add%20repository%20to%20my-Home%20Assistant-41BDF5?logo=home-assistant&style=for-the-badge>
[repository-url]: <https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fboecht%2Fha-addon-virtual-meter>
<!-- markdownlint-enable MD013 -->
