<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/main/images/petkit_logo.png"></a>

# Petkit integration for Home Assistant

[![GitHub Release][releases-shield]][releases] [![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits] ![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Supported devices

### Feeders :

- [x] Fresh Element
- [x] Fresh Element Mini Pro
- [x] Fresh Element Infinity
- [x] Fresh Element Solo
- [x] Fresh Element Gemini
- [x] YumShare Solo with Camera
- [x] YumShare Dual-hopper with Camera

### Litters :

- [x] PuraX
- [x] PuraMax
- [x] PuraMax 2
- [ ] Purobot Max Pro with camera (tester needed)
- [x] Purobot Ultra with camera

### Fountains :

- [ ] Eversweet Solo 2
- [ ] Eversweet 3 Pro
- [ ] Eversweet 3 Pro UVC
- [ ] Eversweet 5 Mini
- [x] Eversweet Max

> [!IMPORTANT]
> Camera feature is not supported yet. I'm working on it...

## Installation

Via HACS (recommended), click here :

<img src="https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square" alt="Open your Home Assistant instance and open the repository inside the Home Assistant Community Store"></img>

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
> Petkit accounts cannot be logged in two places at the same time. To use the official Petkit application and the Home Assistant integration simultaneously, you must create a second Petkit account and a "Family".
> Follow these steps:
>
> 1. Go to the Petkit application.
> 2. At the top, click on Family Management and then on the Create a family button and follow the instructions.
> 3. Once finished, click the Add family member button.
> 4. Add your second Petkit account that you will have created beforehand and will be used by the Home Assistant Petkit integration.

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
[buymecoffee]: https://www.buymeacoffee.com/
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/Jezza34000/homeassistant_petkit.svg?style=for-the-badge
[commits]: https://github.com/Jezza34000/homeassistant_petkit/commits/main
[discord]: https://discord.gg/bYQWBc9d
[discord-shield]: https://img.shields.io/discord/1318098700379361362.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Jezza34000/homeassistant_petkit.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jezza34000-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Jezza34000/homeassistant_petkit.svg?style=for-the-badge
[releases]: https://github.com/Jezza34000/homeassistant_petkit/releases
