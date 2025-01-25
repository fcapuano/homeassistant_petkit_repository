<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/petkit_logo.png" width="512" height="101"></a>

# Petkit integration for Home Assistant

---

[![GitHub Release][releases-shield]][releases] [![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge&color=41BDF5)](https://hacs.xyz/docs/faq/custom_repositories)

### Need help ? Join us :

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Enjoying this integration?

[![Sponsor Jezza34000](https://img.shields.io/badge/sponsor-Jezza34000-blue.svg?style=for-the-badge&logo=githubsponsors&color=EA4AAA)](https://github.com/sponsors/Jezza34000) [![Static Badge](https://img.shields.io/badge/Donate-buy_me_a_coffee-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/jezza)

---

## 📣 Video & Image support is Here!

### Access all your media from Petkit devices directly in Home Assistant!

Easily view and manage all your videos and images of your beloved pets right from the Media tab in Home Assistant.

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/media_video.png" width="650"/></a>
<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/media_image.png" width="650"/></a>

> [!NOTE]
>
> 🖼️ Picture feature is supported for all devices with camera, **does not** require an active subscription to Care+ \
> 🎞️ Video feature is supported for all devices with camera, **REQUIRE** an active subscription to Care+\
> 📹 Real-time video stream is not supported yet.

---

## Supported devices

### 🍗 Feeders :

- [x] Fresh Element
- [x] Fresh Element Mini Pro
- [x] Fresh Element Infinity
- [x] Fresh Element Solo
- [x] Fresh Element Gemini
- [x] YumShare Solo (with camera) ✅📸 ☑️📹
- [x] YumShare Dual-hopper (with camera) ✅📸 ☑️📹

### 🚽 Litters :

- [x] PuraX
- [x] PuraMax
- [x] PuraMax 2
- [x] Purobot Max Pro (with camera) ✅📸 ☑️📹
- [x] Purobot Ultra (with camera) ✅📸 ☑️📹

### ⛲ Fountains :

- [x] Eversweet Solo 2
- [x] Eversweet 3 Pro
- [x] Eversweet 3 Pro UVC
- [x] Eversweet 5 Mini
- [x] Eversweet Max

> [!IMPORTANT]
> Fountain only support reading data, no control is available yet. Control will be added soon !

### 🧴 Purifiers :

- [x] Air Magicube
- [x] Air Smart Spray

> [!NOTE]
> Legend :
>
> - ✅📸 = Still picture feature supported
> - ☑️📹 = Video clip feature supported

## Feeders special features

Add feeding Schedule card for feeders :

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/feed_plan.png"></a>

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
>
> To use both the official Petkit app AND Home Assistant simultaneously, you need two accounts:
>
> - Use your **PRIMARY** account with the official Petkit app to retain full control over device management.
> - Use your **SECONDARY** account for Home Assistant integration.
>
> Add the secondary account to your primary account's family in the Petkit app.
>
> How to create a family and add a member:
>
> 1. Open the Petkit app and log in with your primary account.
> 2. At the top of the screen, click on Family Management, then select Create a Family and follow the prompts.
> 3. Once the family is created, click on the Add Family Member button.
> 4. Add your secondary Petkit account.
> 5. Finally, log into the Home Assistant integration using your secondary account.

## Configuration options

**Basic configuration :**

- Polling interval : The interval in seconds to poll the Petkit API. (default: 60)
- Smart poll : Enable adaptative scan to reduce polling interval when device is active or an event is detected. (default: true)

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/config.png"/></a>

**Advanced configuration (media options) :**

- Media path : The path to store media files. (default: /media)

> [!IMPORTANT]
> It's recommended to use an external storage to store media files. As the device can generate a lot of media files, it can fill up your Home Assistant storage quickly. Specially if you have "Fetch video" option enabled.

- Media refresh interval : The interval in minutes to refresh media list. (default: 5)
- Fetch image : Enable image fetching for feeders/litter with camera. (default: true)
- Fetch video : Enable video fetching for feeders/litter with camera. (default: false)
- Event type for download : The type of event to download media. (default: Eat, Feed, Toileting)
- Delete media after (days) : The number of days to keep media files. (default: 3) Set to 0 to keep all files.

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/media_options.png"/></a>

**Advanced configuration (bluetooth relay options) :**

- Enable bluetooth relay : Enable bluetooth relay for fountain with bluetooth, you need a relay device. (default: true)
- Bluetooth refresh interval : The interval in minutes to scan bluetooth devices. (default: 30)

<a href=""><img src="https://raw.githubusercontent.com/Jezza34000/homeassistant_petkit/refs/heads/main/images/bt_options.png"/></a>

## Available languages

This integration is available in the following languages:

- English
- Polish (thanks to @Chriserus)
- Spanish (thanks to @joasara)
- French
- German
- Italian
- Chinese (thanks to @pujiaxun)

> Some translations was generated by IA and may not be accurate, if you see any mistake, open a pull request with the correction.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Code quality

[![GitHub Activity][commits-shield]][commits] ![Project Maintenance][maintenance-shield] [![License][license-shield]](LICENSE)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=bugs)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Jezza34000_homeassistant_petkit&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Jezza34000_homeassistant_petkit) _**KISS : Keep It Simple, Stupid. Less is More**_

## Petkit API client

This repository is based on the client library for the Petkit API, which can be found here : [Jezza34000/py-petkit-api](https://github.com/Jezza34000/py-petkit-api)

## Credits

Thanks to :

- @ludeeus for the [integration_blueprint](https://github.com/ludeeus/integration_blueprint) template.
- @RobertD502 for the great reverse engineering done in this repository which helped a lot [home-assistant-petkit](https://github.com/RobertD502/home-assistant-petkit)

---

[homeassistant_petkit]: https://github.com/Jezza34000/homeassistant_petkit
[commits-shield]: https://img.shields.io/github/commit-activity/y/Jezza34000/homeassistant_petkit.svg?style=flat
[commits]: https://github.com/Jezza34000/homeassistant_petkit/commits/main
[discord]: https://discord.gg/Va8DrmtweP
[discord-shield]: https://img.shields.io/discord/1318098700379361362.svg?style=for-the-badge&label=Discord&logo=discord&color=5865F2
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge&label=Home%20Assistant%20Community&logo=homeassistant&color=18bcf2
[forum]: https://community.home-assistant.io/t/petkit-integration/834431
[license-shield]: https://img.shields.io/github/license/Jezza34000/homeassistant_petkit.svg??style=flat
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jezza34000-blue.svg?style=flat
[releases-shield]: https://img.shields.io/github/release/Jezza34000/homeassistant_petkit.svg?style=for-the-badge&color=41BDF5
[releases]: https://github.com/Jezza34000/homeassistant_petkit/releases
