# NotiScript – Custom Notification Platform for Home Assistant

**NotiScript** is a custom `notify` platform that that enables you to route notifier calls to scripts and provides some data transformation capabilities along the way.

The main purpose is to be able to use scripts in contexts where normally only notifiers are possible (the alert integration for example).

- [1. Features](#1-features)
- [2. Installation](#2-installation)
  - [2.1. Install via HACS (recommended)](#21-install-via-hacs-recommended)
  - [2.2. Install manually from repository](#22-install-manually-from-repository)
- [3. Most simple use case](#3-most-simple-use-case)
- [4. More advanced configuration](#4-more-advanced-configuration)
- [5. How It Works](#5-how-it-works)
  - [5.1. Script Selection (script\_suffix)](#51-script-selection-script_suffix)
  - [5.2. Data Transformation (script\_fields)](#52-data-transformation-script_fields)
- [6. Examples](#6-examples)
  - [6.1. Basic Usage](#61-basic-usage)
  - [6.2. Multiple Scripts](#62-multiple-scripts)
  - [6.3. Dynamic Script Selection](#63-dynamic-script-selection)
- [7. Debugging](#7-debugging)
- [8. Documentation](#8-documentation)
- [9. License](#9-license)

## 1. State of this software

The integration seems to work fine (at least on my machine 😊).
The documentation is to lengthy and not to the point; i will improve it if anybody shows interest in this software.
I am a programmer but python is new to me and this is my first integration for Home Assistant.

## 2. Features

- Can be used like any other `notify` platform
- Can be used to create notifiers (services of the form `notify.<my name>`) that forward their calls to a configured script.
- Preserves original notification service data
- Supports dynamic script selection with three priority levels
- Provides data transformation capabilities

## 3. Installation

You can find all the code at [GitHub / ha-notiscript](https://github.com/sejnub/ha-notiscript)

### 3.1. Install via HACS (recommended)

To install this integration using [HACS](https://hacs.xyz):

1. Go to **HACS → ⋮ → Custom repositories**
2. Add the repository:
   - Repository: `https://github.com/sejnub/ha-notiscript`
   - Type: `Integration`
3. After adding, search for `NotiScript Notify` in HACS and install it
4. Restart Home Assistant
5. Configure as described in the following text

### 3.2. Install manually from repository

1. Create the folder structure `<config_dir>/custom_components/notiscript/`

2. Add file `__init__.py` to that folder
   > [See code in `__init__.py`](custom_components/notiscript/__init__.py) – or copy from the latest version.

3. Add file `manifest.json` to that folder
   > [See code in `manifest.json`](custom_components/notiscript/manifest.json) – or copy from the latest version.

4. Add file `notify.py` to that folder
   > [See code in `notify.py`](custom_components/notiscript/notify.py) – or copy from the latest version.

5. Restart Home Assistant

## 4. Most simple use case

If you add

```yaml
notify:
  - platform: notiscript
    name: my_notifier
```

to your configuration.yaml then a notifier (*not* an entity, so don't look for it!) `notify.my_notifier` will be created.

This notifier when called will forward that call to `script.my_notifier` with all call parameters unchanged.

## 5. More advanced configuration

Add this to your `configuration.yaml`:

```yaml
notify:
  - platform: notiscript
    name: my_notifier
    script_suffix: my_script  # optional
    script_fields:  # optional
      title: I am a new title
      message: I am a new message
```

| Option          | Required | Description                                                                                                  |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| `name`          | ✅        | The created notifier will now be `notify.<name>`                                                                   |
| `script_suffix` | ❌        | The script called will now be `script.<script_suffix>`                                                            |
| `script_fields` | ❌        | Fields to pass to script. This replaces the original parameters which are moved to `<service data>.data.notifier_fields` |

## 6. How It Works

NotiScript provides two main transformation mechanisms:

### 6.1. Script Selection (script_suffix)

Determines which script to call, with three priority levels:

1. From notification data
2. From configuration
3. From notifier name (fallback)

### 6.2. Data Transformation (script_fields)

Defines how notification data should be transformed before being passed to the script:

1. From notification data
2. From configuration

When `script_fields` is present:

- The values from `script_fields` are passed directly to the script
- Original notification fields are moved to `data.notifier_fields`
- All other data is preserved in `data`

## 7. Examples

### 7.1. Basic Usage

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

### 7.2. Multiple Scripts

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

### 7.3. Dynamic Script Selection

```yaml
service: notify.my_notifier
data:
  data:
    script_suffix: urgent_script  # Override default script
    script_fields:
      message: alert
      title: warning
```

## 8. Debugging

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

## 9. Documentation

For detailed documentation including diagrams and more examples, see [concept.md](concept.md).

## 10. License

See [LICENSE](./LICENSE)
