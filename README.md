# Deliveroo (HK) Statistic Home-Assistant Custom-Component

## Prerequisite

- Deliveroo Subscriber
- Deliveroo session token

## Add to HACS

1. Setup `HACS` https://hacs.xyz/docs/setup/prerequisites
2. In `Home Assistant`, click `HACS` on the menu on the left
3. Select `integrations`
4. Click the menu button in the top right hand corner
5. Choose `custom repositories`
6. Enter `https://github.com/thematrixdev/home-assistant-deliveroo` and choose `Integration`, click `ADD`
7. Find and click on `Deliveroo HK` in the `custom repositories` list
8. Click the `DOWNLOAD` button in the bottom right hand corner
9. Restart Home Assistant

## Install

1. Go to `Settings`, `Devices and Services`
2. Click the `Add Integration` button
3. Search `Deliveroo HK`
4. Go through the configuration flow

## Debug

### Basic

- On Home Assistant, go to `Settigns` -> `Logs`
- Search `Deliveroo HK`

### Advanced

- Add these lines to `configuration.yaml`

```yaml
logger:
  default: info
  logs:
    custom_components.deliveroohk: debug
```

- Restart Home Assistant
- On Home Assistant, go to `Settigns` -> `Logs`
- Search `Deliveroo HK`
- Click the `LOAD FULL LOGS` button

## Support

- Open an issue on GitHub
- Specify:
    - What's wrong
    - Home Assistant version
    - Deliveroo HK custom-integration version
    - Configuration (without sensitive data)
    - Logs

## Unofficial support

- Telegram Group https://t.me/smarthomehk

## Tested on

- Ubuntu 24.10
- Home Assistant Container 2025.01
