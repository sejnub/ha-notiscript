# NotiScript – Custom Notification Platform for Home Assistant

**NotiScript** is a custom `notify` platform for Home Assistant that allows you to route notifications to arbitrary scripts.
This gives you full control over how notifications are handled – logging, forwarding, filtering, conditional actions, or even interacting with other systems.

- [1. 🔧 Features](#1--features)
- [2. 📂 Installation](#2--installation)
  - [2.1. Install manually from repository](#21-install-manually-from-repository)
  - [2.2. Install via HACS (recommended)](#22-install-via-hacs-recommended)
- [3. ⚙️ Configuration](#3-️-configuration)
- [4. 🚀 How It Works](#4--how-it-works)
- [5. 🧪 Example Scripts](#5--example-scripts)
- [6. 🧰 Example Automation](#6--example-automation)
- [7. 🔍 Debugging](#7--debugging)
- [8. 💬 FAQ](#8--faq)
  - [8.1. Why is `notify.my_notify_handler` not visible as an entity?](#81-why-is-notifymy_notify_handler-not-visible-as-an-entity)
- [9. 👨‍💻 Development Notes](#9--development-notes)
- [10. 🏁 Roadmap](#10--roadmap)
- [11. 📝 License](#11--license)

## 1. 🔧 Features

- Acts like any standard `notify` platform
- Forwards `message`, `title`, and `data` to a `script`
- Supports 3 levels of script resolution:
  1. Dynamic at runtime via `data.script_id`
  2. Static via `script:` option in `configuration.yaml`
  3. Fallback to the notifier name (e.g. `script.my_notify_handler`)
- Works with automations, alerts, UI services

## 2. 📂 Installation

You can find all the code at [GitHub / ha-notiscript](https://github.com/sejnub/ha-notiscript)

### 2.1. Install manually from repository

1. Create the folder structure:

   ```sh
   <config_dir>/custom_components/notiscript/
   ```

2. Add file `__init__.py` to that folder

   > [See code in `__init__.py`](custom_components/notiscript/__init__.py) – or copy from the latest version.

3. Add file `manifest.json` to  that folder
   > [See code in `manifest.json`](custom_components/notiscript/manifest.json) – or copy from the latest version.

4. Add file `notify.py` to that folder
    > [See code in `notify.py`](custom_components/notiscript/notify.py) – or copy from the latest version.

5. Restart Home Assistant

### 2.2. Install via HACS (recommended)

To install this integration using [HACS](https://hacs.xyz):

1. Go to **HACS → ⋮ → Custom repositories**

2. Add the repository 

   - Repository:`https://github.com/sejnub/ha-notiscript`
   - Type: `Integration`

3. After adding, search for `NotiScript Notify` in HACS and install it

4. Restart Home Assistant
5. Configure as described in the following text

## 3. ⚙️ Configuration

Add this to your `configuration.yaml`:

```yaml
notify:
  - platform: notiscript
    name: my_notify_handler
    script: fallback_script  # optional
```

| Option   | Required | Description                                            |
| -------- | -------- | ------------------------------------------------------ |
| `name`   | ✅        | The notifier name, becomes `notify.<name>`             |
| `script` | ❌        | Optional fallback script name if none given at runtime |

## 4. 🚀 How It Works

When you call:

```yaml
service: notify.my_notify_handler
data:
  message: "Hello"
  title: "Info"
  data:
    script_id: "custom_script"
```

The integration determines the script to call using this priority:

1. `data.script_id` → `script.custom_script`
2. Configured `script:` → e.g. `script.fallback_script`
3. Notifier name → `script.my_notify_handler`

The selected script receives all fields (`message`, `title`, `data`) as variables.

## 5. 🧪 Example Scripts

```yaml
script:
  fallback_script:
    sequence:
      - service: logbook.log
        data:
          name: "Fallback Script"
          message: "Msg: {{ message }} | Title: {{ title }} | Data: {{ data | to_json }}"
```

```yaml
  custom_script:
    sequence:
      - service: notify.telegram_bot
        data:
          message: "{{ message }}"
```

## 6. 🧰 Example Automation

```yaml
automation:
  - alias: Test Notification
    trigger:
      - platform: time
        at: "12:00:00"
    action:
      - service: notify.my_notify_handler
        data:
          message: "It is noon"
          title: "Time Check"
```

## 7. 🔍 Debugging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.notiscript: debug
```

Check logs via **Developer Tools → Logs**.

## 8. 💬 FAQ

### 8.1. Why is `notify.my_notify_handler` not visible as an entity?

Because notify services are not entities – they are service endpoints only.

## 9. 👨‍💻 Development Notes

- Based on `BaseNotificationService`
- Uses `async_call` to `script` domain
- Accepts all standard `notify` fields: `message`, `title`, `target`, `data`
- `target` is ignored (but can be forwarded if needed)

## 10. 🏁 Roadmap

- Optional: entity registry integration (cosmetic)

## 11. 📝 License

> [See `LICENSE`](./LICENSE)
