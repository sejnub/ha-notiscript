# NotiScript – Custom Notification Platform for Home Assistant

**NotiScript** is a custom `notify` platform for Home Assistant that allows you to route notifications to arbitrary scripts.

This gives you full control over how notifications are handled – logging, forwarding, filtering, conditional actions, or even interacting with other systems.

---

## 🔧 Features

- Acts like any standard `notify` platform
- Forwards `message`, `title`, and `data` to a `script`
- Supports 3 levels of script resolution:
  1. Dynamic at runtime via `data.script_id`
  2. Static via `script:` option in `configuration.yaml`
  3. Fallback to the notifier name (e.g. `script.my_notify_handler`)
- Works with automations, alerts, UI services

---

## 📂 Installation

1. Create the folder structure:

```
<config_dir>/custom_components/notiscript/
```

2. Add these 3 files:

### `__init__.py`
```python
# empty file
```

---

### `manifest.json`
```json
{
  "domain": "notiscript",
  "name": "NotiScript Notify",
  "version": "1.0.0",
  "requirements": [],
  "dependencies": [],
  "codeowners": []
}
```

---

### `notify.py`
> [See code in `notify.py`](./notify.py) – or copy from the latest version.

---

3. Restart Home Assistant

---

## ⚙️ Configuration

Add this to your `configuration.yaml`:

```yaml
notify:
  - platform: notiscript
    name: my_notify_handler
    script: fallback_script  # optional
```

| Option     | Required | Description |
|------------|----------|-------------|
| `name`     | ✅       | The notifier name, becomes `notify.<name>` |
| `script`   | ❌       | Optional fallback script name if none given at runtime |

---

## 🚀 How It Works

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

---

## 🧪 Example Scripts

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

---

## 🧰 Example Automation

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

---

## 🔍 Debugging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.notiscript: debug
```

Check logs via **Developer Tools → Logs**.

---

## 💬 FAQ

### Why is `notify.my_notify_handler` not visible as an entity?

Because notify services are not entities – they are service endpoints only.

---

## 👨‍💻 Development Notes

- Based on `BaseNotificationService`
- Uses `async_call` to `script` domain
- Accepts all standard `notify` fields: `message`, `title`, `target`, `data`
- `target` is ignored (but can be forwarded if needed)

---

## 🏁 Roadmap

- Optional: support for script domains other than `script` (e.g. `automation`)
- Optional: entity registry integration (cosmetic)

---

## 📝 License

MIT – Use freely and customize as needed.
