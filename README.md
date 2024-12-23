<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/master/images/petkit_logo.png" width="512" height="101"></a>

# Petkit integration for Home Assistant

---
[![GitHub Release][releases-shield]][releases] [![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge&color=41BDF5)](https://hacs.xyz/docs/faq/custom_repositories)

[![GitHub Activity][commits-shield]][commits] ![Project Maintenance][maintenance-shield] [![License][license-shield]](LICENSE)

### Need help ? Join us :

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Enjoying this integration? 
[![Sponsor Jezza34000](https://img.shields.io/badge/sponsor-Jezza34000-blue.svg?style=for-the-badge&logo=githubsponsors&color=EA4AAA)](https://github.com/sponsors/Jezza34000) [![Static Badge](https://img.shields.io/badge/Donate-buy_me_a_coffee-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/jezza)


Picture feature is supported for feeders with camera (does not require an active subscription to Care+) \
Video feature is not supported yet. it's planned for a future release. (REQUIRE an active subscription to Care+)

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/master/images/last_event.png"></a>

## Supported devices

### :poultry_leg: Feeders :

- [x] Fresh Element
- [x] Fresh Element Mini Pro
- [x] Fresh Element Infinity
- [x] Fresh Element Solo
- [x] Fresh Element Gemini
- [x] YumShare Solo with Camera
- [x] YumShare Dual-hopper with Camera

### :toilet: Litters :

- [x] PuraX
- [x] PuraMax
- [x] PuraMax 2
- [ ] Purobot Max Pro with camera (tester needed)
- [x] Purobot Ultra with camera

### :fountain: Fountains :

- [x] Eversweet Solo 2
- [x] Eversweet 3 Pro
- [x] Eversweet 3 Pro UVC
- [x] Eversweet 5 Mini
- [x] Eversweet Max

> [!IMPORTANT]
> Fountain only support reading data, no control is available yet. it's planned for a future release.

## Feeders special features

Add feeding Schedule card for feeders :

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/master/images/feed_plan.png"></a>

Add this card to your HA with HACS : https://github.com/cristianchelu/dispenser-schedule-card (thanks to @cristianchelu)

On config card paste this :

```yaml
type: custom:dispenser-schedule-card
entity: sensor.MY_FEEDER_NAME_raw_distribution_data
editable: never
alternate_unit:
  unit_of_measurement: g
  conversion_factor: 10
  approximate: true
```

## Installation

Via HACS (recommended), click here :

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Jezza34000&repository=homeassistant_petkit&category=integration)

Or follow these steps:

1. Open HACS (Home Assistant Community Store)
2. Click on the three dots in the top right corner
3. Click on `Custom repositories`
4. In the Repository field, enter https://github.com/Jezza34000/homeassistant_petkit/
5. In the Category field, select `Integration`
6. Click on `Add`
7. Search for `Petkit Smart Devices` in the list of integrations
8. Install the integration
9. Restart Home Assistant
10. Go to `settings` -> `integrations` -> `add integration` -> search for `Petkit Smart Devices`
11. Follow the instructions to configure the integration

## Configuration is done in the UI

> [!IMPORTANT]
> Accounts: \
> In order to use the official Petkit official application **AND** HomeAssistant simultaneously, you must have 2 accounts :
>
> - Use the **primary** account with your official Petkit application.
> - Use the **secondary** account for Home Assistant.
>
> Add the secondary account to the primary account's family in the Petkit application. \
>
> **How to create a family:**
>
> 1. Go to the Petkit application, when logged with your primary account.
> 2. At the top, click on `Family Management` and then on the `Create a family` button and follow the instructions.
> 3. Once finished, click the `Add family member` button.
> 4. Add your second Petkit account.
> 5. Now log in to the Home Assistant application with your secondary account.

## Available languages

This integration is available in the following languages:

- English
- Polish (thanks to @Chriserus)
- Spanish (thanks to @joasara)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Code quality

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=bugs)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)

## Petkit API client

This repository is based on the client library for the Petkit API, which can be found here : [Jezza34000/py-petkit-api](https://github.com/Jezza34000/py-petkit-api)

## Credits

Thanks to :

- @Leedeus for the [integration_blueprint](https://github.com/ludeeus/integration_blueprint) template.
- @RobertD502 for the great reverse engineering done in this repository which helped a lot [home-assistant-petkit](https://github.com/RobertD502/home-assistant-petkit)

---

[homeassistant_petkit]: https://github.com/Jezza34000/homeassistant_petkit
[commits-shield]: https://img.shields.io/github/commit-activity/y/Jezza34000/homeassistant_petkit.svg?style=for-the-badge&color=788B95
[commits]: https://github.com/Jezza34000/homeassistant_petkit/commits/main
[discord]: https://discord.gg/bYQWBc9d
[discord-shield]: https://img.shields.io/discord/1318098700379361362.svg?style=for-the-badge&label=Discord&logo=discord&color=5865F2
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge&label=Home%20Assistant%20Community&logo=homeassistant&color=18bcf2
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Jezza34000/homeassistant_petkit.svg?style=for-the-badge&color=788B95
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jezza34000-blue.svg?style=for-the-badge&color=788B95
[releases-shield]: https://img.shields.io/github/release/Jezza34000/homeassistant_petkit.svg?style=for-the-badge&color=41BDF5
[releases]: https://github.com/Jezza34000/homeassistant_petkit/releases
