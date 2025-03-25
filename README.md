# NotiScript – Custom Notification Platform for Home Assistant

**NotiScript** is a custom `notify` platform for Home Assistant that provides some data transformation capabilities when routing notifications to scripts.

- [1. 🔧 Features](#1--features)
- [2. 📂 Installation](#2--installation)
  - [2.1. Install manually from repository](#21-install-manually-from-repository)
  - [2.2. Install via HACS (recommended)](#22-install-via-hacs-recommended)
- [3. ⚙️ Configuration](#3-️-configuration)
- [4. 🚀 How It Works](#4--how-it-works)
  - [4.1. Script Selection (script\_suffix)](#41-script-selection-script_suffix)
  - [4.2. Data Transformation (script\_fields)](#42-data-transformation-script_fields)
- [5. 🧪 Examples](#5--examples)
  - [5.1. Basic Usage](#51-basic-usage)
  - [5.2. Multiple Scripts](#52-multiple-scripts)
  - [5.3. Dynamic Script Selection](#53-dynamic-script-selection)
- [6. 🔍 Debugging](#6--debugging)
- [7. 📚 Documentation](#7--documentation)
- [8. License](#8-license)

## 1. 🔧 Features

- Acts like any standard `notify` platform
- Supports dynamic script selection with three priority levels
- Provides data transformation capabilities
- Preserves original notification data
- Works with automations, alerts, UI services

## 2. 📂 Installation

You can find all the code at [GitHub / ha-notiscript](https://github.com/sejnub/ha-notiscript)

### 2.1. Install manually from repository

1. Create the folder structure `<config_dir>/custom_components/notiscript/`

2. Add file `__init__.py` to that folder
   > [See code in `__init__.py`](custom_components/notiscript/__init__.py) – or copy from the latest version.

3. Add file `manifest.json` to that folder
   > [See code in `manifest.json`](custom_components/notiscript/manifest.json) – or copy from the latest version.

4. Add file `notify.py` to that folder
   > [See code in `notify.py`](custom_components/notiscript/notify.py) – or copy from the latest version.

5. Restart Home Assistant

### 2.2. Install via HACS (recommended)

To install this integration using [HACS](https://hacs.xyz):

1. Go to **HACS → ⋮ → Custom repositories**
2. Add the repository:
   - Repository: `https://github.com/sejnub/ha-notiscript`
   - Type: `Integration`
3. After adding, search for `NotiScript Notify` in HACS and install it
4. Restart Home Assistant
5. Configure as described in the following text

## 3. ⚙️ Configuration

Add this to your `configuration.yaml`:

```yaml
notify:
  - platform: notiscript
    name: my_notifier
    script_suffix: my_script  # optional
    script_fields:  # optional
      message: msg
      title: heading
```

| Option          | Required | Description                                           |
| --------------- | -------- | ----------------------------------------------------- |
| `name`          | ✅        | The notifier name, becomes `notify.<name>`            |
| `script_suffix` | ❌        | Optional script name to call `script.<script_suffix>` |
| `script_fields` | ❌        | Optional fields to pass to script                     |

## 4. 🚀 How It Works

NotiScript provides two main transformation mechanisms:

### 4.1. Script Selection (script_suffix)

Determines which script to call, with three priority levels:
1. From notification data
2. From configuration
3. From notifier name (fallback)

### 4.2. Data Transformation (script_fields)
Defines how notification data should be transformed before being passed to the script:
1. From notification data
2. From configuration

When `script_fields` is present:
- The values from `script_fields` are passed directly to the script
- Original notification fields are moved to `data.notifier_fields`
- All other data is preserved in `data`

## 5. 🧪 Examples

### 5.1. Basic Usage
```yaml
service: notify.my_notifier
data:
  message: "Hello"
  title: "Test"
  data:
    script_fields:
      message: "msg"
      title: "heading"
    custom_field: "value"
```

### 5.2. Multiple Scripts
```yaml
notify:
  - platform: notiscript
    name: urgent_notifier
    script_suffix: urgent_script
    script_fields:
      message: alert
      title: warning
  - platform: notiscript
    name: normal_notifier
    script_suffix: normal_script
    script_fields:
      message: info
      title: status
```

### 5.3. Dynamic Script Selection
```yaml
service: notify.my_notifier
data:
  data:
    script_suffix: urgent_script  # Override default script
    script_fields:
      message: alert
      title: warning
```

## 6. 🔍 Debugging

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.notiscript: debug
```

This will show:
- Script selection process
- Data transformation steps
- Final data structure sent to script
- Any errors during execution

## 7. 📚 Documentation

For detailed documentation including diagrams and more examples, see [concept.md](concept.md).

## 8. License

See [LICENSE](./LICENSE)
