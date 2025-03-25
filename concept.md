# NotiScript Concept Documentation

## Overview

NotiScript is a notification platform that provides powerful data transformation capabilities when routing notifications to scripts. It allows you to:
1. Dynamically select which script to call
2. Transform notification data before passing it to scripts
3. Preserve original notification data while providing transformed data

## Core Concepts

### 1. Script Selection

NotiScript uses a three-level priority system to determine which script to call:

```mermaid
graph TD
    A[Notification Call] --> B{Has script_suffix in data?}
    B -->|Yes| C[Use script_suffix from data]
    B -->|No| D{Has script_suffix in config?}
    D -->|Yes| E[Use script_suffix from config]
    D -->|No| F[Use notifier name]
    C --> G[Call Selected Script]
    E --> G
    F --> G
```

Example:
```yaml
# Priority 1: From notification data
service: notify.my_notifier
data:
  data:
    script_suffix: urgent_script

# Priority 2: From configuration
notify:
  - platform: notiscript
    name: my_notifier
    script_suffix: normal_script

# Priority 3: From notifier name
notify:
  - platform: notiscript
    name: my_notifier  # Will use script.my_notifier
```

### 2. Data Transformation

The `script_fields` mechanism allows you to transform notification data before it reaches the script:

```mermaid
graph LR
    A[Notification Data] --> B{Has script_fields?}
    B -->|Yes| C[Transform Data]
    B -->|No| D[Pass Original Data]
    C --> E[Move Original Fields to notifier_fields]
    C --> F[Use script_fields Values]
    E --> G[Final Data Structure]
    F --> G
    D --> G
```

Example:
```yaml
# Original Notification
service: notify.my_notifier
data:
  message: "Hello"
  title: "Test"
  data:
    script_fields:
      message: "msg"
      title: "heading"
    custom_field: "value"

# Result Sent to Script
{
    "message": "msg",
    "title": "heading",
    "data": {
        "custom_field": "value",
        "notifier_fields": {
            "message": "Hello",
            "title": "Test"
        }
    }
}
```

## Data Flow

```mermaid
sequenceDiagram
    participant N as Notification
    participant NS as NotiScript
    participant S as Script

    N->>NS: Send Notification
    NS->>NS: Extract Control Parameters
    Note over NS: script_suffix<br/>script_fields
    NS->>NS: Transform Data
    Note over NS: Move fields to notifier_fields<br/>Apply script_fields
    NS->>S: Call Script with Transformed Data
    S-->>NS: Script Execution Complete
```

## Use Cases

### 1. Multiple Scripts with Different Data Structures

```mermaid
graph TD
    A[Notification] --> B{Which Script?}
    B -->|Urgent| C[Urgent Script]
    B -->|Normal| D[Normal Script]
    C --> E[Different Data Structure]
    D --> F[Different Data Structure]
```

Example:
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

### 2. Dynamic Script Selection

```mermaid
graph TD
    A[Notification] --> B{Check Context}
    B -->|Urgent| C[Use Urgent Script]
    B -->|Normal| D[Use Normal Script]
    C --> E[Transform for Urgent]
    D --> F[Transform for Normal]
```

Example:
```yaml
service: notify.my_notifier
data:
  data:
    script_suffix: urgent_script  # Override default script
    script_fields:
      message: alert
      title: warning
```

### 3. Data Preservation with Transformation

```mermaid
graph LR
    A[Original Data] --> B[Split]
    B --> C[Transformed Fields]
    B --> D[Original Fields]
    C --> E[Script Input]
    D --> F[notifier_fields]
```

Example:
```yaml
service: notify.my_notifier
data:
  message: "Hello"
  title: "Test"
  data:
    script_fields:
      message: "msg"
    custom_field: "value"
```

## Data Structures

### Input Structure
```mermaid
classDiagram
    class Notification {
        +String message
        +String title
        +Object data
        +Object data.script_suffix
        +Object data.script_fields
    }
```

### Output Structure
```mermaid
classDiagram
    class ScriptInput {
        +String message
        +String title
        +Object data
        +Object data.notifier_fields
    }
```

## Priority System

### Script Selection Priority
1. `data.script_suffix` from notification
2. `script_suffix` from configuration
3. Notifier name as fallback

### Data Transformation Priority
1. `data.script_fields` from notification
2. `script_fields` from configuration

## Best Practices

1. **Configuration**
   - Use configuration for default behavior
   - Keep transformation rules consistent
   - Document expected data structures

2. **Notification Calls**
   - Use data overrides for special cases
   - Preserve original data when needed
   - Keep transformation rules simple

3. **Script Design**
   - Expect transformed data structure
   - Handle both transformed and original fields
   - Document expected input format

## Debugging

Enable debug logging to see:
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