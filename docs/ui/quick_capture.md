# Quick Command Capture & Learning - UI/UX Design Specification

**Version:** 1.0
**Date:** 2025-11-05
**Status:** Design Proposal
**Designer:** TrayRunner UI Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Flows & Scenarios](#2-user-flows--scenarios)
3. [UI Mockups & Wireframes](#3-ui-mockups--wireframes)
4. [Component Specifications](#4-component-specifications)
5. [Smart Detection Rules](#5-smart-detection-rules)
6. [Learning System Design](#6-learning-system-design)
7. [Design Decisions & Rationale](#7-design-decisions--rationale)
8. [Accessibility & UX](#8-accessibility--ux)
9. [Technical Architecture Notes](#9-technical-architecture-notes)
10. [Implementation Phases](#10-implementation-phases)
11. [Open Questions & Future Enhancements](#11-open-questions--future-enhancements)

---

## 1. Executive Summary

### 1.1 Feature Overview

The **Quick Command Capture & Learning** feature transforms TrayRunner from a static menu editor into an intelligent command assistant that learns from user behavior. It consists of two core capabilities:

1. **Quick Capture Overlay** - A lightweight, hotkey-triggered window that instantly converts terminal commands into tray menu items
2. **Command Learning System** - Passive monitoring that suggests frequently-run commands as menu item candidates

### 1.2 Core Value Proposition

**Problem Solved:**
Users repeatedly type complex commands in terminals but forget them later, leading to inefficient command retrieval through history searches or documentation diving.

**Solution:**
One-hotkey workflow: Run command → Hit `Ctrl+Alt+T` → Paste → Enter name → Done. Command is now permanently in tray menu.

### 1.3 Design Goals

- **Speed**: Capture workflow completes in under 10 seconds
- **Intelligence**: Smart defaults eliminate 80% of manual configuration
- **Non-intrusive**: Overlay appears instantly but never blocks work
- **Privacy-first**: All learning is opt-in and locally stored
- **Accessible**: Fully keyboard-navigable with screen reader support

### 1.4 Success Metrics

- Time from hotkey press to saved item: < 8 seconds (target)
- User configuration overrides after save: < 20% (indicates good smart defaults)
- Feature adoption rate: 60% of users use quick capture within first week
- Suggestion acceptance rate: 40% of suggested commands added to menu

---

## 2. User Flows & Scenarios

### 2.1 Primary Flow: Manual Quick Capture

**Scenario:** Sarah runs a complex Docker cleanup command and wants to save it

```
ACTOR: Sarah (DevOps Engineer)
CONTEXT: Just ran `docker system prune -af --volumes` in terminal
GOAL: Add command to tray menu without opening full editor

FLOW:
┌──────────────────────────────────────────────────────────┐
│ 1. Terminal: Execute command                             │
│    $ docker system prune -af --volumes                    │
│    [Output: Deleted containers: 12, Space reclaimed: 2GB] │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 2. Sarah: Copy command (Ctrl+Shift+C) or rely on auto-  │
│           clipboard detection                             │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 3. Sarah: Press global hotkey (Ctrl+Alt+T)              │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 4. SYSTEM: Quick Capture overlay appears (200ms fade-in) │
│    - Command field auto-filled from clipboard             │
│    - Smart detection runs instantly                       │
│    - Label field focused, ready for typing                │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 5. Sarah: Types label "Clean Docker Space"              │
│    - Sees checkboxes auto-enabled:                        │
│      ☑ Show confirmation (detected: destructive command) │
│      ☐ Run in terminal                                    │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 6. Sarah: Presses Enter (or clicks "Add to Menu")       │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 7. SYSTEM: Success feedback                              │
│    - Green checkmark animation                            │
│    - Toast: "Added 'Clean Docker Space' to Commands"     │
│    - Overlay closes (300ms fade-out)                      │
│    - Menu item appears in tray immediately                │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 8. OPTIONAL: Click "Add Another" to capture more         │
│              OR "Customize..." to open full editor        │
└──────────────────────────────────────────────────────────┘

TIME: 6-8 seconds total
EFFORT: 4 user actions (hotkey, type, enter, done)
```

**Alternative Paths:**

- **Path A - Empty Clipboard**: Command field starts empty, user pastes manually
- **Path B - History Selection**: User picks from dropdown of recent shell history instead of pasting
- **Path C - Cancel**: Press Escape or click outside overlay to dismiss
- **Path D - Advanced Options**: Expand "More Options" section to configure working directory, environment variables

---

### 2.2 Secondary Flow: Suggestion Acceptance

**Scenario:** System suggests a frequently-run command

```
ACTOR: Marcus (Backend Developer)
CONTEXT: Has run `git pull --rebase origin main` 8 times this week
GOAL: System proactively suggests adding it to menu

FLOW:
┌──────────────────────────────────────────────────────────┐
│ 1. SYSTEM: Learning engine detects pattern               │
│    - Command frequency: 8 runs in 7 days                  │
│    - Not currently in menu config                         │
│    - Threshold: 5+ runs in 30 days triggers suggestion    │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 2. SYSTEM: Desktop notification (low priority)           │
│    ┌─────────────────────────────────────────┐           │
│    │ TrayRunner Suggestion                    │           │
│    │ You've run this 8 times:                 │           │
│    │ git pull --rebase origin main            │           │
│    │                                           │           │
│    │ [Add to Menu]  [Dismiss]  [Never Suggest]│           │
│    └─────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 3. Marcus: Clicks "Add to Menu"                          │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 4. SYSTEM: Quick Capture overlay opens (pre-filled)      │
│    - Command: git pull --rebase origin main              │
│    - Label: "Git Pull Rebase" (auto-generated)           │
│    - Smart defaults applied                               │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 5. Marcus: Reviews, optionally edits label, presses Enter│
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│ 6. SYSTEM: Saved with success feedback                   │
└──────────────────────────────────────────────────────────┘

TIME: 3-5 seconds (even faster than manual capture)
EFFORT: 2 user actions (click notification, confirm)
```

**Alternative Paths:**

- **Path A - Suggestions Panel**: Marcus opens TrayRunner GUI → "Suggestions" tab → sees list of all suggested commands → batch-add multiple
- **Path B - Dismiss**: Clicking "Dismiss" removes this suggestion but allows future similar suggestions
- **Path C - Never Suggest**: Adds command pattern to ignore list (e.g., never suggest any `git pull` commands)

---

### 2.3 Edge Case Flows

#### Flow 2.3a: Command Already Exists

```
USER: Tries to add `docker ps -a`
SYSTEM: Detects "Docker List All" already exists in menu
ACTION: Shows warning dialog
  ┌─────────────────────────────────────────────┐
  │ ⚠ Similar Command Exists                    │
  │                                              │
  │ This command might already be in your menu:  │
  │ "Docker List All" → docker ps -a             │
  │                                              │
  │ [Cancel]  [Add Anyway]  [Edit Existing]      │
  └─────────────────────────────────────────────┘
```

#### Flow 2.3b: Dangerous Command Detection

```
USER: Tries to add `rm -rf /`
SYSTEM: Detects dangerous pattern
ACTION: Shows prominent warning
  ┌─────────────────────────────────────────────┐
  │ 🔴 DANGER: Destructive Command Detected      │
  │                                              │
  │ This command can permanently delete files:   │
  │ rm -rf /                                     │
  │                                              │
  │ We strongly recommend NOT adding this.       │
  │                                              │
  │ [Cancel (Recommended)]  [Add with Confirm]   │
  └─────────────────────────────────────────────┘
```

#### Flow 2.3c: Multi-line Command Paste

```
USER: Pastes command with newlines or pipe chains
SYSTEM: Detects multi-line structure
ACTION: Auto-formats into single-line or offers alternatives
  ┌─────────────────────────────────────────────┐
  │ Multi-line Command Detected                  │
  │                                              │
  │ Your command spans multiple lines:           │
  │   docker ps -a |                             │
  │   grep mysql |                               │
  │   awk '{print $1}'                           │
  │                                              │
  │ How should we save this?                     │
  │ ○ Single line with semicolons                │
  │ ● Pipe chain (recommended)                   │
  │ ○ Shell script (create .sh file)             │
  │                                              │
  │ Result: docker ps -a | grep mysql | awk...   │
  │                                              │
  │ [Continue]  [Cancel]                         │
  └─────────────────────────────────────────────┘
```

---

## 3. UI Mockups & Wireframes

### 3.1 Quick Capture Overlay - Main View

```
┌─────────────────────────────────────────────────────────────┐
│  Quick Command Capture                              [×]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Command                                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ docker system prune -af --volumes                        ││
│  └─────────────────────────────────────────────────────────┘│
│  [Paste from Clipboard]  [From History ▼]                   │
│                                                               │
│  Label (Menu Name)                                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Clean Docker Space                                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Smart Detection Results:                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ✓ Detected: Destructive operation (prune, delete)        ││
│  │ ✓ Recommended: Enable confirmation dialog                ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Options                                                      │
│  ☑ Show confirmation before running                          │
│  ☐ Run in terminal window                                    │
│  ☐ Notify when complete                                      │
│                                                               │
│  [▼ More Options]                                            │
│                                                               │
│                                   [Cancel]  [Add to Menu]    │
└─────────────────────────────────────────────────────────────┘

DIMENSIONS: 600px wide × 400px tall (compact)
POSITION: Center of screen (or near mouse cursor if configured)
BACKDROP: 40% opacity dark overlay (click to cancel)
ANIMATION: 200ms ease-out fade + scale (0.95 → 1.0)
FONT: System default, 11pt body, 13pt headings
```

**Visual Design Details:**

- **Window Style**: Frameless with rounded corners (12px radius), subtle drop shadow
- **Color Scheme**:
  - Background: `#FFFFFF` (light mode) / `#2D2D30` (dark mode)
  - Accent: TrayRunner blue `#007ACC`
  - Success: `#28A745`
  - Warning: `#FFC107`
  - Danger: `#DC3545`
- **Input Fields**: 2px border, 6px padding, 4px border-radius, focus state with blue glow
- **Smart Detection Box**: Light blue background `#E3F2FD`, blue left border (3px), info icon
- **Buttons**: Primary action (Add to Menu) uses accent color, secondary uses gray

---

### 3.2 Quick Capture Overlay - Expanded View

```
┌─────────────────────────────────────────────────────────────┐
│  Quick Command Capture                              [×]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Command                                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ git pull --rebase origin main                            ││
│  └─────────────────────────────────────────────────────────┘│
│  [Paste from Clipboard]  [From History ▼]                   │
│                                                               │
│  Label (Menu Name)                                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Git Pull Rebase                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Smart Detection Results:                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ✓ Detected: Git command (working directory aware)        ││
│  │ ⓘ Tip: This command works best when run in a git repo    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Options                                                      │
│  ☐ Show confirmation before running                          │
│  ☐ Run in terminal window                                    │
│  ☐ Notify when complete                                      │
│                                                               │
│  [▲ More Options]                                            │
│  ├─────────────────────────────────────────────────────────┤│
│  │ Working Directory (Optional)                             ││
│  │ ┌─────────────────────────────────────────────────┐     ││
│  │ │ ~/projects/trayrunner                            │[📁] ││
│  │ └─────────────────────────────────────────────────┘     ││
│  │ Leave empty to run in current directory                  ││
│  │                                                           ││
│  │ Environment Variables                                     ││
│  │ ┌───────────────────┬───────────────────┐               ││
│  │ │ Key               │ Value             │ [+ Add]       ││
│  │ ├───────────────────┼───────────────────┤               ││
│  │ │ GITHUB_TOKEN      │ ghp_xxxxxxxxx     │ [×]           ││
│  │ └───────────────────┴───────────────────┘               ││
│  │                                                           ││
│  │ Save to Group                                            ││
│  │ ┌─────────────────────────────────────────────────────┐ ││
│  │ │ Commands (Root) ▼                                    │ ││
│  │ └─────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│                                   [Cancel]  [Add to Menu]    │
└─────────────────────────────────────────────────────────────┘

DIMENSIONS: 600px wide × 580px tall (expanded)
EXPANSION: Smooth height animation (300ms ease-out)
```

**Interaction Notes:**

- **More Options Toggle**: Clicking expands/collapses advanced section with animation
- **Browse Button**: Opens native file picker for working directory
- **Add Environment Var**: Inserts new row in key/value table
- **Group Dropdown**: Shows existing groups from config, with "New Group..." option
- **Validation**: Real-time validation shows red border + error message for invalid paths

---

### 3.3 Command History Dropdown

```
┌─────────────────────────────────────────────────────────────┐
│  Command                                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                           ││
│  └─────────────────────────────────────────────────────────┘│
│  [Paste from Clipboard]  [From History ▼]  ← CLICKED        │
│                          └──────────────────────────────┐    │
│                                                          │    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Recent Shell Commands                           [×]   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │ 🔍 Search history...                            │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  Last 10 commands:                                     │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │ docker ps -a                          2 min ago│   │  │
│  │  │ git status                             5 min ago│   │  │
│  │  │ docker system prune -af              10 min ago│   │  │
│  │  │ npm run build                         15 min ago│   │  │
│  │  │ systemctl restart nginx              23 min ago│   │  │
│  │  │ kubectl get pods                      1 hour ago│   │  │
│  │  │ ssh user@server.com                   2 hours ago│  │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  │                                                        │  │
│  │  Frequently Used:                                      │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │ git pull --rebase                    (18 times)│   │  │
│  │  │ docker-compose up -d                  (12 times)│   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

DIMENSIONS: Dropdown width matches trigger button, max height 400px
SCROLL: Vertical scroll if content exceeds height
SOURCE: Parses ~/.bash_history, ~/.zsh_history, fish history
```

**Features:**

- **Search Box**: Filters commands in real-time as user types
- **Timestamps**: Relative time display (just now, 2 min ago, 1 hour ago)
- **Frequency Indicator**: Shows run count for frequently used commands
- **Keyboard Navigation**: Arrow keys to select, Enter to choose, Escape to close
- **Privacy**: Only shows commands from current user's shell history
- **Smart Filtering**: Excludes sensitive commands (those containing passwords, API keys)

---

### 3.4 Success Confirmation

```
OPTION A: INLINE SUCCESS (Preferred)
┌─────────────────────────────────────────────────────────────┐
│  Quick Command Capture                              [×]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                         ┌───────┐                             │
│                         │   ✓   │  ← Animated checkmark       │
│                         └───────┘     (scale + fade in)       │
│                                                               │
│                   Successfully Added!                         │
│                "Clean Docker Space"                           │
│                                                               │
│                                                               │
│          [Add Another]  [Customize...]  [Done]               │
│                                                               │
└─────────────────────────────────────────────────────────────┘

ANIMATION:
1. Form fades out (200ms)
2. Checkmark scales in (300ms with bounce easing)
3. Text fades in (200ms)
4. Auto-close after 2 seconds OR user clicks Done

---

OPTION B: TOAST NOTIFICATION (Alternative)
┌────────────────────────────────────────────┐
│ ✓ Added "Clean Docker Space" to Commands   │
│   Click to customize or undo               │
└────────────────────────────────────────────┘
  │
  └─> Appears bottom-right, auto-dismisses in 4 seconds
      Clicking opens full editor for customization
```

**Design Choice Rationale:**

- **Option A (Inline)** is preferred because:
  - Keeps user in capture flow for adding more commands
  - Clear, celebratory success feedback
  - Offers next steps without interrupting workflow

- **Option B (Toast)** is fallback for situations where user might be multitasking

---

### 3.5 Suggestions Panel (in Main GUI)

```
┌─────────────────────────────────────────────────────────────┐
│  TrayRunner Config Editor                   [_] [□] [×]      │
├─────────────────────────────────────────────────────────────┤
│ File  Edit  Tools  Help                                      │
├──────┬──────────────────────────────────────────────────────┤
│ Tree │ Commands   Suggestions (3)   Settings                │
├──────┼──────────────────────────────────────────────────────┤
│      │                                                        │
│ [+]  │  💡 Command Suggestions                               │
│ [+]  │                                                        │
│ [+]  │  These commands appear frequently in your shell       │
│      │  history but aren't in your menu yet.                 │
│      │                                                        │
│      │  ┌────────────────────────────────────────────────┐  │
│      │  │ 🔄 git pull --rebase origin main               │  │
│      │  │                                                 │  │
│      │  │ Run 8 times in last 7 days                     │  │
│      │  │ Last used: 2 hours ago                         │  │
│      │  │                                                 │  │
│      │  │ Smart defaults:                                 │  │
│      │  │ • Label: "Git Pull Rebase"                     │  │
│      │  │ • Group: Git Commands                          │  │
│      │  │ • Terminal: No                                  │  │
│      │  │                                                 │  │
│      │  │           [Ignore] [Customize] [Add to Menu]   │  │
│      │  └────────────────────────────────────────────────┘  │
│      │                                                        │
│      │  ┌────────────────────────────────────────────────┐  │
│      │  │ 🐳 docker system prune -af                     │  │
│      │  │                                                 │  │
│      │  │ Run 5 times in last 14 days                    │  │
│      │  │ Last used: 3 days ago                          │  │
│      │  │                                                 │  │
│      │  │ Smart defaults:                                 │  │
│      │  │ • Label: "Clean Docker Space"                  │  │
│      │  │ • Confirmation: Yes (destructive)              │  │
│      │  │                                                 │  │
│      │  │           [Ignore] [Customize] [Add to Menu]   │  │
│      │  └────────────────────────────────────────────────┘  │
│      │                                                        │
│      │  ┌────────────────────────────────────────────────┐  │
│      │  │ 🔧 systemctl restart nginx                     │  │
│      │  │                                                 │  │
│      │  │ Run 6 times in last 10 days                    │  │
│      │  │ Last used: 1 day ago                           │  │
│      │  │                                                 │  │
│      │  │ Smart defaults:                                 │  │
│      │  │ • Label: "Restart Nginx"                       │  │
│      │  │ • Confirmation: Yes (system service)           │  │
│      │  │                                                 │  │
│      │  │           [Ignore] [Customize] [Add to Menu]   │  │
│      │  └────────────────────────────────────────────────┘  │
│      │                                                        │
│      │  [Clear All Suggestions]                              │
│      │                                                        │
└──────┴──────────────────────────────────────────────────────┘

TAB INDICATOR: Badge shows suggestion count (3)
UPDATE FREQUENCY: Suggestions refresh when GUI opens + every 24 hours
```

**Interaction Details:**

- **Add to Menu Button**: One-click acceptance, adds item with all smart defaults
- **Customize Button**: Opens Quick Capture overlay pre-filled with suggestion for editing
- **Ignore Button**: Removes this specific suggestion, won't suggest again
- **Clear All**: Dismisses all current suggestions (can regenerate later)
- **Badge**: Tab label shows "Suggestions (3)" with count, changes to just "Suggestions" when empty

---

### 3.6 Desktop Notification

```
┌─────────────────────────────────────────────────────┐
│  TrayRunner                                   [×]   │
├─────────────────────────────────────────────────────┤
│  💡 Frequently Used Command Detected                │
│                                                      │
│  You've run this 8 times:                           │
│                                                      │
│  git pull --rebase origin main                      │
│                                                      │
│  Would you like to add it to your menu?             │
│                                                      │
│  [Add to Menu]  [Dismiss]  [Never Suggest]          │
└─────────────────────────────────────────────────────┘

TIMING: Appears after threshold met (5+ runs in 30 days)
FREQUENCY: Max 1 notification per day (avoid spam)
PRIORITY: Low (doesn't override other notifications)
SOUND: Optional subtle chime (user configurable)
ACTION: Clicking "Add to Menu" opens Quick Capture overlay
```

**Notification Strategy:**

- **Throttling**: Maximum 1 suggestion notification per 24 hours
- **Smart Timing**: Only show when system is idle (not during active typing/clicking)
- **Persistence**: Notification stays visible for 10 seconds, then auto-dismisses
- **Memory**: Dismissed suggestions remembered, won't re-notify for same command
- **Never Suggest**: Adds pattern to global ignore list (e.g., all `git pull*` commands)

---

## 4. Component Specifications

### 4.1 Quick Capture Overlay Window

**Technology:** PySide6 QDialog with frameless window hints

**Properties:**
```python
class QuickCaptureDialog(QDialog):
    # Window flags
    - Qt.FramelessWindowHint
    - Qt.WindowStaysOnTopHint (optional, configurable)
    - Qt.Dialog (modal to current desktop, not application-modal)

    # Geometry
    - Fixed width: 600px
    - Dynamic height: 400px (collapsed) / 580px (expanded)
    - Position: Center of active screen

    # Styling
    - Border radius: 12px
    - Drop shadow: QGraphicsDropShadowEffect
      - Blur radius: 20px
      - Color: rgba(0, 0, 0, 0.3)
      - Offset: (0, 4px)

    # Animation
    - Entry: QPropertyAnimation on opacity (0 → 1) + scale (0.95 → 1)
    - Exit: QPropertyAnimation on opacity (1 → 0)
    - Duration: 200ms (entry), 150ms (exit)
    - Easing: QEasingCurve.OutCubic
```

**Layout Hierarchy:**
```
QDialog (QuickCaptureDialog)
└── QVBoxLayout (main_layout)
    ├── QLabel (title_label) "Quick Command Capture"
    ├── QWidget (command_section)
    │   ├── QLabel "Command"
    │   ├── QLineEdit (command_input)
    │   └── QHBoxLayout
    │       ├── QPushButton "Paste from Clipboard"
    │       └── QPushButton "From History ▼"
    ├── QWidget (label_section)
    │   ├── QLabel "Label (Menu Name)"
    │   └── QLineEdit (label_input)
    ├── QFrame (detection_results_frame)
    │   └── QLabel (detection_info) with icon + text
    ├── QWidget (options_section)
    │   ├── QCheckBox (confirm_check) "Show confirmation"
    │   ├── QCheckBox (terminal_check) "Run in terminal"
    │   └── QCheckBox (notify_check) "Notify when complete"
    ├── QWidget (advanced_section) [collapsible]
    │   ├── QPushButton (toggle_advanced) "▼ More Options"
    │   └── QWidget (advanced_content) [hidden by default]
    │       ├── Working directory section
    │       ├── Environment variables section
    │       └── Group selection section
    └── QHBoxLayout (button_layout)
        ├── QSpacerItem (stretch)
        ├── QPushButton (cancel_btn) "Cancel"
        └── QPushButton (add_btn) "Add to Menu" [primary]
```

**Key Behaviors:**

1. **Auto-focus**: Label input receives focus on open (command pre-filled from clipboard)
2. **Enter Key**: Pressing Enter in any field triggers "Add to Menu" action
3. **Escape Key**: Closes overlay without saving
4. **Click Outside**: Clicking backdrop dismisses overlay (configurable)
5. **Validation**: Real-time validation prevents adding empty label/command

---

### 4.2 Command Input Field

**Widget:** QLineEdit with custom validation and placeholder text

**Features:**
- **Placeholder**: "Paste command here or select from history..."
- **Max Length**: 2000 characters (prevent abuse)
- **Multi-line Detection**: Automatically converts newlines to spaces or pipes
- **Syntax Highlighting**: Optional light gray background for detected command parts
  - Example: `docker` (command) `ps -a` (arguments) in different weights

**Validation Rules:**
```python
def validate_command(command: str) -> tuple[bool, str]:
    """
    Returns: (is_valid, error_message)
    """
    if not command.strip():
        return (False, "Command cannot be empty")

    if len(command) > 2000:
        return (False, "Command too long (max 2000 characters)")

    # Check for dangerous patterns
    dangerous_patterns = [
        r'rm\s+-rf\s+/',  # Root deletion
        r'dd\s+.*of=/dev/',  # Disk overwrite
        r':(){ :|:& };:',  # Fork bomb
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return (False, f"Dangerous command detected: {pattern}")

    return (True, "")
```

**Smart Paste Handling:**
```python
def on_paste(self):
    """Handle paste event with smart formatting"""
    text = QApplication.clipboard().text()

    # Remove leading prompt symbols ($ > %)
    text = re.sub(r'^[\$\>\%]\s*', '', text)

    # Handle multi-line: convert to single line
    if '\n' in text:
        # Preserve pipe chains and logical operators
        text = text.replace('\\\n', ' ')  # Line continuations
        text = text.replace('\n', ' ')    # Regular newlines
        text = re.sub(r'\s+', ' ', text)  # Collapse whitespace

    self.command_input.setText(text.strip())
```

---

### 4.3 History Dropdown Component

**Widget:** Custom QComboBox with custom popup containing QListWidget

**Data Source:**
```python
class ShellHistoryParser:
    """Parse shell history from various shells"""

    HISTORY_FILES = {
        'bash': '~/.bash_history',
        'zsh': '~/.zsh_history',
        'fish': '~/.local/share/fish/fish_history',
    }

    def get_recent_commands(self, limit: int = 50) -> list[HistoryEntry]:
        """
        Returns list of recent commands with metadata

        HistoryEntry:
          - command: str
          - timestamp: datetime
          - frequency: int (run count)
        """
        pass

    def filter_sensitive(self, commands: list[str]) -> list[str]:
        """Remove commands containing passwords, API keys"""
        patterns = [
            r'password\s*=',
            r'apikey\s*=',
            r'token\s*=',
            r'secret\s*=',
        ]
        return [cmd for cmd in commands if not any(re.search(p, cmd, re.I) for p in patterns)]
```

**UI Features:**
- **Search**: Real-time filter as user types in search box
- **Grouping**: "Recent" section (chronological) + "Frequently Used" section
- **Keyboard Nav**: Arrow keys, Enter to select, Escape to close
- **Empty State**: Shows "No command history found" if history files don't exist

---

### 4.4 Smart Detection Results Panel

**Widget:** QFrame with info icon + text label

**Visual Style:**
```css
QFrame#detection_results {
    background-color: #E3F2FD; /* Light blue */
    border-left: 3px solid #2196F3; /* Blue accent */
    border-radius: 4px;
    padding: 12px;
    margin: 8px 0;
}

QLabel#detection_info {
    color: #1565C0; /* Dark blue text */
    font-size: 11pt;
}
```

**Content Examples:**

```
✓ Detected: Destructive operation (prune, delete)
✓ Recommended: Enable confirmation dialog

✓ Detected: Interactive command (vim, htop)
✓ Recommended: Run in terminal window

✓ Detected: Git command (working directory aware)
ⓘ Tip: This command works best when run in a git repo

✓ Detected: System service management (systemctl)
✓ Recommended: Enable confirmation (root permissions required)

⚠ No suggestions available
ⓘ Review options below and configure manually
```

**Dynamic Updates:**
- Content updates in real-time as command text changes
- Icon changes based on detection confidence (✓ = high, ⓘ = info, ⚠ = warning)
- Panel hides if no detections found (keeps UI clean)

---

### 4.5 Suggestion Card Component

**Widget:** Custom QFrame container with embedded controls

**Layout:**
```
┌────────────────────────────────────────────────┐
│ [Icon] Command Text                             │
│                                                 │
│ Run count + last used metadata                  │
│                                                 │
│ Smart defaults preview                          │
│                                                 │
│ [Action Buttons]                                │
└────────────────────────────────────────────────┘
```

**Styling:**
```css
QFrame.suggestion_card {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

QFrame.suggestion_card:hover {
    border-color: #2196F3;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

**Icons by Command Type:**
- Git commands: 🔄 (git branch icon)
- Docker commands: 🐳 (docker logo)
- System commands: 🔧 (gear icon)
- Network commands: 🌐 (globe icon)
- File operations: 📁 (folder icon)
- Default: ⚡ (lightning bolt)

---

## 5. Smart Detection Rules

### 5.1 Detection Rule Engine

**Architecture:**
```python
class DetectionRule:
    """Base class for command detection rules"""

    def __init__(self, priority: int = 0):
        self.priority = priority  # Higher priority runs first

    def matches(self, command: str) -> bool:
        """Returns True if rule applies to this command"""
        raise NotImplementedError

    def get_recommendations(self, command: str) -> dict:
        """
        Returns recommended settings

        {
            'label': str,           # Suggested menu label
            'terminal': bool,       # Run in terminal?
            'confirm': bool,        # Show confirmation?
            'notify': bool,         # Notify on completion?
            'working_dir': str,     # Suggested working dir
            'group': str,           # Suggested group name
            'confidence': float,    # 0.0-1.0
            'reason': str,          # Human-readable explanation
        }
        """
        raise NotImplementedError

class RuleEngine:
    """Manages and applies detection rules"""

    def __init__(self):
        self.rules = [
            DestructiveCommandRule(),
            InteractiveCommandRule(),
            GitCommandRule(),
            DockerCommandRule(),
            SystemServiceRule(),
            LongRunningCommandRule(),
            NetworkCommandRule(),
        ]
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def analyze(self, command: str) -> dict:
        """Apply all matching rules and aggregate recommendations"""
        results = {
            'label': self._generate_label(command),
            'terminal': False,
            'confirm': False,
            'notify': False,
            'working_dir': None,
            'group': 'Commands',
            'detections': [],
        }

        for rule in self.rules:
            if rule.matches(command):
                rec = rule.get_recommendations(command)
                results['detections'].append(rec['reason'])

                # Aggregate settings (OR logic for booleans)
                results['terminal'] |= rec.get('terminal', False)
                results['confirm'] |= rec.get('confirm', False)
                results['notify'] |= rec.get('notify', False)

                # Override string values if confidence is higher
                if rec.get('confidence', 0) > 0.7:
                    results['label'] = rec.get('label', results['label'])
                    results['group'] = rec.get('group', results['group'])

        return results
```

---

### 5.2 Detection Rules Catalog

#### Rule 1: Destructive Command Detection

**Patterns:**
```python
DESTRUCTIVE_PATTERNS = [
    r'\brm\b.*-[rf]',              # rm with -r or -f flags
    r'\bprune\b',                   # docker/git prune
    r'\bdelete\b',                  # explicit delete
    r'\bdrop\b',                    # SQL drop
    r'\btruncate\b',                # SQL truncate
    r'\bdestroy\b',                 # terraform destroy
    r'\buninstall\b',               # package uninstall
    r'\bclean\b',                   # clean/cleanup operations
]
```

**Recommendations:**
- **Confirm**: ✅ Always enable
- **Terminal**: ❌ Usually no (unless combined with interactive)
- **Label Hint**: Include "Clean" / "Delete" / "Remove" in label
- **Group**: "Maintenance" or "Cleanup"

**Examples:**
```
Command: docker system prune -af
→ Label: "Clean Docker Space"
→ Confirm: Yes
→ Reason: "Detected: Destructive operation (prune)"

Command: rm -rf ~/old_backups
→ Label: "Remove Old Backups"
→ Confirm: Yes
→ Reason: "Detected: File deletion with rm -rf"
```

---

#### Rule 2: Interactive Command Detection

**Patterns:**
```python
INTERACTIVE_COMMANDS = [
    'vim', 'vi', 'nano', 'emacs',   # Editors
    'htop', 'top', 'iotop',         # System monitors
    'less', 'more',                 # Pagers
    'man',                          # Manual pages
    'tmux', 'screen',               # Terminal multiplexers
    'ssh',                          # SSH sessions
    'mysql', 'psql', 'mongo',       # Database shells
]

INTERACTIVE_FLAGS = [
    '-it',  # Docker interactive + TTY
    '-i',   # Interactive mode
]
```

**Recommendations:**
- **Terminal**: ✅ Always enable
- **Confirm**: ❌ No (not dangerous)
- **Label Hint**: Include tool name

**Examples:**
```
Command: htop
→ Label: "System Monitor (htop)"
→ Terminal: Yes
→ Reason: "Detected: Interactive TUI application"

Command: docker exec -it mycontainer bash
→ Label: "Container Shell"
→ Terminal: Yes
→ Reason: "Detected: Interactive container session"
```

---

#### Rule 3: Git Command Detection

**Patterns:**
```python
GIT_COMMANDS = [
    r'^git\s+',
]

GIT_WORKING_DIR_COMMANDS = [
    'pull', 'push', 'status', 'commit', 'checkout', 'merge', 'rebase'
]
```

**Recommendations:**
- **Working Dir**: Suggest current directory (or last used repo path)
- **Terminal**: ✅ Only for interactive commands (rebase, merge with conflicts)
- **Group**: "Git Commands" or "Version Control"
- **Label**: Parse subcommand (e.g., "git pull" → "Git Pull")

**Examples:**
```
Command: git pull --rebase origin main
→ Label: "Git Pull Rebase"
→ Working Dir: (detect from shell context)
→ Group: "Git Commands"
→ Reason: "Detected: Git command (working directory aware)"

Command: git commit -am "message"
→ Label: "Git Commit"
→ Terminal: Yes (to see output)
```

---

#### Rule 4: Docker Command Detection

**Patterns:**
```python
DOCKER_COMMANDS = [
    r'^docker\s+',
    r'^docker-compose\s+',
]

DOCKER_DESTRUCTIVE = ['prune', 'rm', 'rmi', 'down']
DOCKER_LONG_RUNNING = ['build', 'pull', 'push', 'up']
```

**Recommendations:**
- **Group**: "Docker Commands"
- **Confirm**: ✅ For destructive operations
- **Notify**: ✅ For long-running operations (build, pull)
- **Terminal**: ✅ For logs/up commands

**Examples:**
```
Command: docker-compose up -d
→ Label: "Docker Compose Up"
→ Terminal: No (detached mode)
→ Group: "Docker"

Command: docker build -t myapp .
→ Label: "Build Docker Image"
→ Notify: Yes (long-running)
→ Terminal: Yes (to see build output)
```

---

#### Rule 5: System Service Management

**Patterns:**
```python
SERVICE_COMMANDS = [
    r'systemctl\s+(start|stop|restart|reload)',
    r'service\s+\w+\s+(start|stop|restart)',
    r'sudo\s+(systemctl|service)',
]
```

**Recommendations:**
- **Confirm**: ✅ Always (system-wide impact)
- **Group**: "System Services"
- **Label**: Include service name + action

**Examples:**
```
Command: sudo systemctl restart nginx
→ Label: "Restart Nginx"
→ Confirm: Yes
→ Reason: "Detected: System service management (requires root)"

Command: systemctl status docker
→ Label: "Docker Status"
→ Confirm: No (read-only)
```

---

#### Rule 6: Long-Running Commands

**Heuristics:**
```python
LONG_RUNNING_INDICATORS = [
    'build', 'compile', 'test', 'backup', 'sync', 'download', 'upload',
    'rsync', 'scp', 'wget', 'curl' (with -o flag), 'npm install', 'pip install'
]

def estimate_duration(command: str) -> int:
    """Returns estimated seconds (rough heuristic)"""
    if 'build' in command or 'compile' in command:
        return 300  # 5 minutes
    if 'test' in command:
        return 120  # 2 minutes
    if 'backup' in command or 'rsync' in command:
        return 600  # 10 minutes
    return 0
```

**Recommendations:**
- **Notify**: ✅ If estimated duration > 60 seconds
- **Terminal**: ✅ To show progress

**Examples:**
```
Command: npm run build
→ Label: "Build Project"
→ Notify: Yes
→ Reason: "Detected: Long-running build command"

Command: rsync -avz /source /destination
→ Label: "Sync Files"
→ Notify: Yes
→ Terminal: Yes (to see progress)
```

---

#### Rule 7: Network/Remote Commands

**Patterns:**
```python
NETWORK_COMMANDS = [
    r'ssh\s+',
    r'scp\s+',
    r'curl\s+',
    r'wget\s+',
    r'ping\s+',
    r'nc\s+',  # netcat
    r'telnet\s+',
]
```

**Recommendations:**
- **Group**: "Network" or "Remote"
- **Terminal**: ✅ For interactive sessions (SSH)
- **Confirm**: ❌ Usually safe

**Examples:**
```
Command: ssh user@server.com
→ Label: "SSH to Server"
→ Terminal: Yes
→ Group: "Remote Servers"

Command: ping -c 4 google.com
→ Label: "Ping Google"
→ Terminal: Yes (to see output)
```

---

### 5.3 Label Generation Algorithm

**Smart Label Generation:**
```python
def generate_label(command: str) -> str:
    """
    Generate human-friendly label from command

    Examples:
    - "docker ps -a" → "Docker List All"
    - "git pull --rebase origin main" → "Git Pull Rebase"
    - "systemctl restart nginx" → "Restart Nginx"
    """

    # Remove sudo prefix
    cmd = command.replace('sudo ', '')

    # Split into parts
    parts = cmd.split()
    if not parts:
        return "New Command"

    base_command = parts[0]

    # Special handling for common commands
    if base_command == 'docker':
        return _generate_docker_label(parts[1:])
    elif base_command == 'git':
        return _generate_git_label(parts[1:])
    elif base_command == 'systemctl':
        return _generate_systemctl_label(parts[1:])
    elif base_command in ['npm', 'yarn', 'pnpm']:
        return _generate_npm_label(base_command, parts[1:])

    # Default: Title case the command
    return base_command.capitalize()

def _generate_docker_label(args: list[str]) -> str:
    """Docker-specific label generation"""
    if not args:
        return "Docker Command"

    subcommand = args[0]
    mapping = {
        'ps': 'Docker List',
        'build': 'Build Docker Image',
        'run': 'Run Docker Container',
        'exec': 'Execute in Container',
        'logs': 'Docker Logs',
        'system prune': 'Clean Docker Space',
    }

    # Check for multi-word subcommands
    two_word = f"{args[0]} {args[1]}" if len(args) > 1 else None
    if two_word in mapping:
        return mapping[two_word]

    return mapping.get(subcommand, f"Docker {subcommand.capitalize()}")

def _generate_git_label(args: list[str]) -> str:
    """Git-specific label generation"""
    if not args:
        return "Git Command"

    subcommand = args[0]
    mapping = {
        'pull': 'Git Pull',
        'push': 'Git Push',
        'status': 'Git Status',
        'commit': 'Git Commit',
        'checkout': 'Git Checkout',
        'merge': 'Git Merge',
        'rebase': 'Git Rebase',
        'stash': 'Git Stash',
    }

    label = mapping.get(subcommand, f"Git {subcommand.capitalize()}")

    # Add modifiers
    if '--rebase' in args:
        label += ' Rebase'
    if '--force' in args or '-f' in args:
        label += ' (Force)'

    return label
```

---

## 6. Learning System Design

### 6.1 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                 Learning Engine                      │
│                                                      │
│  ┌────────────────┐      ┌────────────────────┐    │
│  │ History Parser │ ───> │ Frequency Analyzer │    │
│  └────────────────┘      └────────────────────┘    │
│         │                         │                 │
│         │                         ▼                 │
│         │              ┌────────────────────┐       │
│         └──────────────>│ Suggestion Engine │       │
│                         └────────────────────┘       │
│                                  │                   │
│                                  ▼                   │
│                         ┌────────────────────┐       │
│                         │  Notification       │       │
│                         │  Scheduler          │       │
│                         └────────────────────┘       │
└─────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   User Interface     │
                    │ - Desktop Notification│
                    │ - Suggestions Panel   │
                    └──────────────────────┘
```

---

### 6.2 Data Collection

**Privacy-First Approach:**

1. **Opt-In**: Learning system is disabled by default, user must explicitly enable
2. **Local Storage**: All data stays on user's machine in `~/.local/state/trayrunner/`
3. **Transparency**: Clear UI showing what's being tracked
4. **Control**: User can view, delete, or disable tracking anytime

**Data Sources:**

```python
class CommandHistoryTracker:
    """Tracks command execution for learning"""

    def __init__(self):
        self.db_path = Path.home() / ".local/state/trayrunner/learned_commands.db"
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        """Create database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS command_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                source TEXT NOT NULL,  -- 'trayrunner' or 'shell_history'
                exit_code INTEGER,
                working_dir TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL UNIQUE,
                first_seen INTEGER NOT NULL,
                last_seen INTEGER NOT NULL,
                run_count INTEGER NOT NULL,
                status TEXT NOT NULL,  -- 'pending', 'accepted', 'dismissed', 'ignored'
                suggested_at INTEGER,
                suggested_label TEXT,
                created_at INTEGER NOT NULL
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ignore_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL UNIQUE,
                added_at INTEGER NOT NULL
            )
        """)

        self.conn.commit()

    def record_shell_history(self):
        """Parse shell history files and record commands"""
        history_parser = ShellHistoryParser()
        commands = history_parser.get_recent_commands(limit=1000)

        for entry in commands:
            # Skip if already in TrayRunner config
            if self._is_in_config(entry.command):
                continue

            # Skip if matches ignore pattern
            if self._matches_ignore_pattern(entry.command):
                continue

            # Record execution
            self.conn.execute("""
                INSERT INTO command_executions (command, timestamp, source)
                VALUES (?, ?, 'shell_history')
            """, (entry.command, entry.timestamp))

        self.conn.commit()

    def record_trayrunner_execution(self, command: str, exit_code: int):
        """Record command executed from TrayRunner"""
        self.conn.execute("""
            INSERT INTO command_executions (command, timestamp, source, exit_code)
            VALUES (?, ?, 'trayrunner', ?)
        """, (command, int(time.time()), exit_code))
        self.conn.commit()
```

---

### 6.3 Frequency Analysis

**Algorithm:**
```python
class FrequencyAnalyzer:
    """Analyze command frequency and patterns"""

    SUGGESTION_THRESHOLD = 5   # Minimum runs to suggest
    TIME_WINDOW = 30 * 86400   # 30 days in seconds

    def analyze(self) -> list[Suggestion]:
        """Find commands worth suggesting"""

        # Query commands from last 30 days
        cutoff = int(time.time()) - self.TIME_WINDOW

        results = self.conn.execute("""
            SELECT
                command,
                COUNT(*) as run_count,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM command_executions
            WHERE timestamp > ? AND source = 'shell_history'
            GROUP BY command
            HAVING run_count >= ?
            ORDER BY run_count DESC, last_seen DESC
            LIMIT 20
        """, (cutoff, self.SUGGESTION_THRESHOLD)).fetchall()

        suggestions = []
        for row in results:
            command, run_count, first_seen, last_seen = row

            # Apply heuristics
            score = self._calculate_score(command, run_count, first_seen, last_seen)

            if score > 0.5:  # Threshold for suggesting
                suggestions.append(Suggestion(
                    command=command,
                    run_count=run_count,
                    last_seen=last_seen,
                    score=score,
                    smart_defaults=self._get_smart_defaults(command)
                ))

        return suggestions

    def _calculate_score(self, command: str, run_count: int,
                        first_seen: int, last_seen: int) -> float:
        """
        Calculate suggestion score (0.0-1.0)

        Factors:
        - Frequency: Higher run_count = higher score
        - Recency: Recent commands score higher
        - Regularity: Commands run consistently over time score higher
        """

        # Frequency score (logarithmic)
        freq_score = min(1.0, math.log(run_count) / math.log(20))

        # Recency score (exponential decay)
        days_since = (time.time() - last_seen) / 86400
        recency_score = math.exp(-days_since / 7)  # Half-life of 7 days

        # Regularity score
        time_span = last_seen - first_seen
        if time_span > 0:
            avg_interval = time_span / run_count
            regularity_score = 1.0 / (1.0 + avg_interval / 86400)  # Prefer daily
        else:
            regularity_score = 0.5

        # Weighted average
        score = (
            0.4 * freq_score +
            0.4 * recency_score +
            0.2 * regularity_score
        )

        return score
```

---

### 6.4 Suggestion Engine

**Notification Strategy:**
```python
class SuggestionScheduler:
    """Manages when and how to notify users about suggestions"""

    MAX_NOTIFICATIONS_PER_DAY = 1
    MIN_IDLE_TIME = 5 * 60  # 5 minutes idle before suggesting

    def should_notify(self, suggestion: Suggestion) -> bool:
        """Determine if we should notify user about this suggestion"""

        # Check daily notification limit
        if self._get_notifications_today() >= self.MAX_NOTIFICATIONS_PER_DAY:
            return False

        # Check if system is idle
        if not self._is_system_idle(self.MIN_IDLE_TIME):
            return False

        # Check if suggestion was already shown
        if self._was_recently_suggested(suggestion):
            return False

        # Check score threshold
        if suggestion.score < 0.7:  # Only notify for high-confidence suggestions
            return False

        return True

    def _is_system_idle(self, seconds: int) -> bool:
        """Check if system has been idle (no keyboard/mouse input)"""
        # Linux-specific: Read /proc/sys/kernel/random/entropy_avail
        # Or use X11 idle detection
        try:
            import subprocess
            result = subprocess.run(
                ['xprintidle'],
                capture_output=True,
                text=True,
                timeout=1
            )
            idle_ms = int(result.stdout.strip())
            return idle_ms >= (seconds * 1000)
        except:
            return False  # Conservative: don't notify if we can't check

    def schedule_background_analysis(self):
        """Run analysis periodically in background"""
        # Run on GUI startup
        # Run every 24 hours
        # Run after shell history file is modified (inotify)
        pass
```

---

### 6.5 User Interface Components

**Preferences Panel:**

```
┌─────────────────────────────────────────────────────┐
│  TrayRunner Preferences                             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Learning & Suggestions                             │
│                                                      │
│  ☑ Enable command learning                          │
│    Learn from your shell history to suggest         │
│    frequently-run commands.                          │
│                                                      │
│  ☑ Show desktop notifications                       │
│    Notify me when new command suggestions are        │
│    available (max 1 per day).                       │
│                                                      │
│  Suggestion Threshold                               │
│  ┌────────────────────────────────────────┐         │
│  │ [■■■■■□□□□□] 5 runs in 30 days          │         │
│  └────────────────────────────────────────┘         │
│  Adjust how frequently a command must be run        │
│  before it's suggested.                             │
│                                                      │
│  ┌────────────────────────────────────────┐         │
│  │ 📊 Learning Statistics                  │         │
│  │                                         │         │
│  │ Commands tracked: 1,247                 │         │
│  │ Suggestions generated: 12               │         │
│  │ Suggestions accepted: 8                 │         │
│  │ Last analysis: 2 hours ago              │         │
│  │                                         │         │
│  │ [View All Data]  [Clear Data]           │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  Privacy Controls                                   │
│  [Manage Ignored Patterns]                          │
│  [Export Learning Data]                             │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Data Viewer:**

```
┌─────────────────────────────────────────────────────┐
│  Command Learning Data                       [×]    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Your most frequently run commands:                 │
│                                                      │
│  ┌────────────────────────────────────────────────┐│
│  │ # │ Command              │ Runs │ Last Used   ││
│  ├───┼──────────────────────┼──────┼─────────────┤│
│  │ 1 │ git status           │  156 │ 5 min ago   ││
│  │ 2 │ docker ps            │   89 │ 1 hour ago  ││
│  │ 3 │ npm run dev          │   67 │ 2 hours ago ││
│  │ 4 │ git pull             │   54 │ 3 hours ago ││
│  │ 5 │ ls -la               │   43 │ 1 day ago   ││
│  │...│                      │      │             ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  Ignored patterns (never suggest):                  │
│  ┌────────────────────────────────────────────────┐│
│  │ • git commit* (any git commit commands)        ││
│  │ • cd * (directory changes)                      ││
│  │ • ls * (listing commands)                       ││
│  │                                                  │
│  │ [Add Pattern]                                   ││
│  └────────────────────────────────────────────────┘│
│                                                      │
│  [Export as CSV]  [Clear All Data]  [Close]        │
└─────────────────────────────────────────────────────┘
```

---

## 7. Design Decisions & Rationale

### 7.1 Hotkey Choice: Ctrl+Alt+T

**Decision:** Use `Ctrl+Alt+T` as default global hotkey

**Rationale:**
- **Mnemonic**: "T" for TrayRunner
- **Conflict Check**: `Ctrl+Alt+T` commonly opens terminal, but our overlay doesn't conflict (different context)
- **Configurable**: Users can change if it conflicts with their setup
- **Accessibility**: Three-key combo is reachable without hand repositioning

**Alternatives Considered:**
- `Ctrl+Space`: Conflicts with many IDEs (autocomplete)
- `Ctrl+Shift+T`: Used for "reopen closed tab" in browsers
- `Win+T`: Reserved by some desktop environments

---

### 7.2 Overlay Position: Center Screen

**Decision:** Show overlay in center of active screen

**Rationale:**
- **Visibility**: Center position is hard to miss
- **Neutral**: Works regardless of screen layout or tiling WM
- **Context**: User's focus is likely near center when working

**Alternatives Considered:**
- **Near Cursor**: More contextual but can be disorienting if cursor is at edge
- **Top-Right Corner**: Common for notifications but feels too passive
- **Bottom-Center**: Works but less prominent

**Implementation:**
```python
def show_centered(self):
    """Show dialog centered on active screen"""
    screen = QApplication.screenAt(QCursor.pos())
    if screen is None:
        screen = QApplication.primaryScreen()

    screen_geometry = screen.geometry()
    dialog_geometry = self.geometry()

    x = screen_geometry.center().x() - dialog_geometry.width() // 2
    y = screen_geometry.center().y() - dialog_geometry.height() // 2

    self.move(x, y)
```

---

### 7.3 Auto-Fill from Clipboard vs. Empty Field

**Decision:** Auto-fill command field from clipboard if it contains valid text

**Rationale:**
- **Speed**: Saves a paste action (2 seconds)
- **User Expectation**: Common workflow is copy → trigger → name
- **Fallback**: If clipboard is empty/invalid, field starts empty

**Implementation:**
```python
def populate_from_clipboard(self):
    """Try to populate command from clipboard"""
    clipboard = QApplication.clipboard()
    text = clipboard.text().strip()

    # Validate clipboard content
    if not text:
        return False

    if len(text) > 2000:  # Too long
        return False

    if '\n' in text and text.count('\n') > 10:  # Multi-line script
        return False

    # Looks valid, populate
    self.command_input.setText(text)
    return True
```

---

### 7.4 Smart Defaults: Auto-Enable vs. Suggestions Only

**Decision:** Auto-enable checkboxes based on detection, but allow easy override

**Rationale:**
- **Efficiency**: 80/20 rule - get it right most of the time
- **Transparency**: Show detection results box explaining why
- **User Control**: Checkboxes are immediately visible and toggleable
- **No Surprises**: User reviews settings before saving

**Alternative Rejected:** Just suggest without applying
- Pro: User feels more in control
- Con: Adds extra clicks for common cases (user must enable confirm for dangerous commands)

---

### 7.5 Suggestions: Notifications vs. Panel Only

**Decision:** Implement both - low-frequency notifications + always-available panel

**Rationale:**
- **Notifications**: Proactive discovery for high-value suggestions
- **Panel**: User-initiated browsing for batch processing
- **Throttling**: Max 1 notification/day prevents annoyance
- **Control**: User can disable notifications, panel always available

**Notification Timing:**
```python
# Only notify when:
# 1. System idle for 5+ minutes (user not actively working)
# 2. No notification in last 24 hours
# 3. High-confidence suggestion (score > 0.7)
# 4. User has learning enabled in preferences
```

---

### 7.6 Label Generation: Auto vs. User-Provided

**Decision:** Generate smart label but keep editable, with focus on label field

**Rationale:**
- **Speed**: For obvious commands (git pull), generated label is fine
- **Flexibility**: User can quickly edit for personalization
- **Learning**: Generated labels teach users the pattern
- **Fallback**: If generation fails, user must provide

**Label Quality:**
- Good: "Git Pull Rebase", "Clean Docker Space", "Restart Nginx"
- Avoid: "Command 1", "New Item", "Run"

---

## 8. Accessibility & UX

### 8.1 Keyboard Navigation

**Complete Keyboard Workflow:**
```
1. Press Ctrl+Alt+T (global hotkey)
   → Overlay appears, label field focused

2. Type label name
   → As you type, command field shows preview below

3. Tab to command field (if not auto-filled)
   → Type or paste command

4. Tab through checkboxes
   → Space to toggle each option

5. Tab to "More Options"
   → Enter to expand advanced section
   → Tab through additional fields

6. Tab to "Add to Menu" button
   → Enter to save

7. OR press Escape at any time to cancel
```

**Tab Order:**
1. Label input
2. Command input
3. "Paste from Clipboard" button
4. "From History" button
5. Confirm checkbox
6. Terminal checkbox
7. Notify checkbox
8. "More Options" toggle
9. [If expanded] Working directory input
10. [If expanded] Browse button
11. [If expanded] Add environment var button
12. "Cancel" button
13. "Add to Menu" button

**Shortcuts:**
- `Ctrl+Enter`: Save (from any field)
- `Escape`: Cancel and close
- `Ctrl+H`: Open history dropdown
- `Ctrl+V`: Paste into command field (standard)

---

### 8.2 Screen Reader Support

**ARIA Labels:**
```python
# Label input
self.label_input.setAccessibleName("Menu item label")
self.label_input.setAccessibleDescription(
    "Enter a friendly name for this command as it will appear in your tray menu"
)

# Command input
self.command_input.setAccessibleName("Shell command")
self.command_input.setAccessibleDescription(
    "Enter the command to execute when this menu item is clicked"
)

# Checkboxes
self.confirm_check.setAccessibleName("Show confirmation dialog")
self.confirm_check.setAccessibleDescription(
    "When enabled, a confirmation dialog will appear before running this command"
)

# Detection results
self.detection_frame.setAccessibleName("Smart detection results")
self.detection_info.setAccessibleDescription(
    "Automatically detected properties based on command analysis"
)
```

**Screen Reader Announcements:**
```python
def on_detection_complete(self, results: dict):
    """Announce detection results to screen reader"""
    if results['detections']:
        announcement = "Detected: " + ", ".join(results['detections'])
        # Use QAccessible to announce
        QAccessible.updateAccessibility(
            QAccessibleEvent(QAccessible.Alert, self.detection_frame, announcement)
        )
```

---

### 8.3 Visual Accessibility

**High Contrast Mode:**
```python
def apply_high_contrast_theme(self):
    """Apply high contrast theme for visual accessibility"""
    self.setStyleSheet("""
        QDialog {
            background-color: #000000;
            color: #FFFFFF;
        }
        QLineEdit {
            background-color: #1A1A1A;
            color: #FFFFFF;
            border: 2px solid #FFFFFF;
        }
        QPushButton#primary {
            background-color: #FFFF00;
            color: #000000;
            border: 3px solid #FFFFFF;
            font-weight: bold;
        }
        QCheckBox::indicator {
            border: 2px solid #FFFFFF;
            width: 20px;
            height: 20px;
        }
    """)
```

**Font Scaling:**
- Respect system font size settings
- Minimum font size: 10pt (readable at standard DPI)
- Scale with DPI for HiDPI displays

**Color Contrast:**
- Background/Text: 7:1 ratio (WCAG AAA)
- Accent/Background: 4.5:1 ratio (WCAG AA)
- Error Text: 7:1 ratio with red background

**Focus Indicators:**
```python
# Prominent focus ring for keyboard navigation
QLineEdit:focus {
    border: 2px solid #007ACC;
    outline: 2px solid #FFA500;  # Additional orange outline
    outline-offset: 2px;
}

QPushButton:focus {
    border: 3px solid #007ACC;
    box-shadow: 0 0 8px #007ACC;
}
```

---

### 8.4 Reduced Motion

**Respect System Preferences:**
```python
def should_animate(self) -> bool:
    """Check if animations should be enabled"""
    # Check system preference for reduced motion
    # Qt doesn't expose this directly, read from system
    try:
        import subprocess
        result = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'enable-animations'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == 'true'
    except:
        return True  # Default to animations enabled

def show(self):
    """Show dialog with optional animation"""
    if self.should_animate():
        # Fade in animation
        self.setWindowOpacity(0.0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(200)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()
    else:
        # Instant appearance
        self.setWindowOpacity(1.0)

    super().show()
```

---

### 8.5 Error Handling & Feedback

**Validation Errors:**
```
Empty label:
┌────────────────────────────────────┐
│ Label (Menu Name)                   │
│ ┌────────────────────────────────┐ │
│ │                                 │ │ ← Red border
│ └────────────────────────────────┘ │
│ ⚠ Label cannot be empty             │ ← Error message
└────────────────────────────────────┘

Invalid working directory:
┌────────────────────────────────────┐
│ Working Directory                   │
│ ┌────────────────────────────────┐ │
│ │ /nonexistent/path               │ │ ← Orange border
│ └────────────────────────────────┘ │
│ ⚠ Directory does not exist          │ ← Warning message
│   (Command will run in default dir) │
└────────────────────────────────────┘
```

**Save Failures:**
```python
try:
    self.save_command()
except PermissionError:
    QMessageBox.critical(
        self,
        "Save Failed",
        "Cannot write to configuration file. Check file permissions."
    )
except ConfigSyntaxError as e:
    QMessageBox.critical(
        self,
        "Configuration Error",
        f"Invalid configuration format: {e}\n\nPlease report this bug."
    )
except Exception as e:
    QMessageBox.critical(
        self,
        "Unexpected Error",
        f"An error occurred while saving:\n{e}"
    )
```

---

## 9. Technical Architecture Notes

### 9.1 Global Hotkey Implementation

**Library Choice: pynput**

```python
from pynput import keyboard

class HotkeyListener:
    """Manages global hotkey registration"""

    def __init__(self):
        self.hotkey = '<ctrl>+<alt>+t'  # Default
        self.listener = None
        self.callback = None

    def register(self, callback):
        """Register hotkey handler"""
        self.callback = callback

        # Parse hotkey combination
        hotkey_obj = keyboard.HotKey(
            keyboard.HotKey.parse(self.hotkey),
            self._on_activate
        )

        # Create listener
        self.listener = keyboard.Listener(
            on_press=lambda key: hotkey_obj.press(self.listener.canonical(key)),
            on_release=lambda key: hotkey_obj.release(self.listener.canonical(key))
        )

        self.listener.start()

    def _on_activate(self):
        """Called when hotkey is pressed"""
        if self.callback:
            # Must call from main thread for Qt
            QMetaObject.invokeMethod(
                self.callback,
                Qt.QueuedConnection
            )

    def unregister(self):
        """Stop listening for hotkey"""
        if self.listener:
            self.listener.stop()
```

**Fallback for X11-only environments:**
```python
# If pynput fails (Wayland issues), use xcb-based approach
import xcb
from xcb import xproto

def register_x11_hotkey(keycode, modifiers, callback):
    """Direct X11 hotkey registration"""
    connection = xcb.connect()
    root = connection.get_setup().roots[0].root

    # Grab key
    connection.core.GrabKey(
        1,  # owner_events
        root,
        modifiers,
        keycode,
        xproto.GrabMode.Async,
        xproto.GrabMode.Async
    )

    # Event loop to listen for keypress
    # (Simplified - full implementation more complex)
```

**Configuration:**
```yaml
# In preferences.yaml
quick_capture:
  enabled: true
  hotkey: "Ctrl+Alt+T"
  auto_fill_clipboard: true
  show_history_dropdown: true
```

---

### 9.2 Shell History Parsing

**Multi-Shell Support:**

```python
class ShellHistoryParser:
    """Parse command history from multiple shell types"""

    PARSERS = {
        'bash': '_parse_bash_history',
        'zsh': '_parse_zsh_history',
        'fish': '_parse_fish_history',
    }

    def get_recent_commands(self, limit: int = 50) -> list[HistoryEntry]:
        """Get recent commands from all available shells"""
        all_commands = []

        for shell, parser_method in self.PARSERS.items():
            try:
                parser = getattr(self, parser_method)
                commands = parser(limit)
                all_commands.extend(commands)
            except FileNotFoundError:
                continue  # Shell history doesn't exist
            except Exception as e:
                logger.warning(f"Failed to parse {shell} history: {e}")

        # Sort by timestamp, deduplicate, limit
        all_commands.sort(key=lambda x: x.timestamp, reverse=True)
        seen = set()
        unique_commands = []

        for cmd in all_commands:
            if cmd.command not in seen:
                seen.add(cmd.command)
                unique_commands.append(cmd)

        return unique_commands[:limit]

    def _parse_bash_history(self, limit: int) -> list[HistoryEntry]:
        """
        Parse ~/.bash_history

        Format:
        #1636123456
        git status
        #1636123789
        docker ps
        """
        path = Path.home() / '.bash_history'
        commands = []

        with open(path, 'r', errors='ignore') as f:
            lines = f.readlines()

        timestamp = None
        for line in lines:
            line = line.rstrip('\n')

            # Timestamp line
            if line.startswith('#'):
                try:
                    timestamp = int(line[1:])
                except ValueError:
                    timestamp = None
            else:
                # Command line
                if line.strip():
                    commands.append(HistoryEntry(
                        command=line,
                        timestamp=timestamp or int(time.time()),
                        shell='bash'
                    ))
                timestamp = None

        return commands[-limit:]

    def _parse_zsh_history(self, limit: int) -> list[HistoryEntry]:
        """
        Parse ~/.zsh_history

        Format:
        : 1636123456:0;git status
        : 1636123789:0;docker ps
        """
        path = Path.home() / '.zsh_history'
        commands = []

        with open(path, 'rb') as f:  # Binary mode for encoding issues
            for line in f:
                try:
                    line = line.decode('utf-8', errors='ignore').rstrip('\n')

                    # Parse format: : timestamp:duration;command
                    if line.startswith(': '):
                        parts = line[2:].split(';', 1)
                        if len(parts) == 2:
                            meta, command = parts
                            timestamp = int(meta.split(':')[0])
                            commands.append(HistoryEntry(
                                command=command,
                                timestamp=timestamp,
                                shell='zsh'
                            ))
                except Exception:
                    continue

        return commands[-limit:]

    def _parse_fish_history(self, limit: int) -> list[HistoryEntry]:
        """
        Parse ~/.local/share/fish/fish_history

        Format:
        - cmd: git status
          when: 1636123456
        - cmd: docker ps
          when: 1636123789
        """
        path = Path.home() / '.local/share/fish/fish_history'
        commands = []

        import yaml  # Fish history is YAML format
        with open(path, 'r') as f:
            entries = yaml.safe_load(f)

        for entry in entries:
            commands.append(HistoryEntry(
                command=entry['cmd'],
                timestamp=entry.get('when', int(time.time())),
                shell='fish'
            ))

        return commands[-limit:]
```

---

### 9.3 Integration with Existing GUI

**Service Registration:**
```python
# In gui/trayrunner_gui/app.py

class TrayRunnerGUIApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # ... existing initialization ...

        # Initialize quick capture service
        self.quick_capture_service = QuickCaptureService()
        self.quick_capture_service.hotkey_triggered.connect(
            self.show_quick_capture_dialog
        )

        # Initialize learning service (if enabled)
        prefs = load_prefs()
        if prefs.get('learning_enabled', False):
            self.learning_service = LearningService()
            self.learning_service.start_background_analysis()

    def show_quick_capture_dialog(self):
        """Show quick capture overlay"""
        dialog = QuickCaptureDialog(parent=self.main_window)
        dialog.command_added.connect(self.on_command_added)
        dialog.show()

    def on_command_added(self, command_data: dict):
        """Handle new command added via quick capture"""
        # Add to config
        self.main_window.add_item_from_data(command_data)

        # Save immediately (or mark as dirty)
        if prefs.get('quick_capture_auto_save', True):
            self.main_window.save_config()
```

**New Menu Items:**
```python
# In gui/trayrunner_gui/main_window.py

def setup_menus(self):
    # ... existing menu setup ...

    # Add Quick Capture menu
    tools_menu.addSeparator()

    self.quick_capture_action = QAction("Quick &Capture...", self)
    self.quick_capture_action.setShortcut(QKeySequence("Ctrl+K"))  # In-app shortcut
    self.quick_capture_action.triggered.connect(self.show_quick_capture)
    tools_menu.addAction(self.quick_capture_action)

    self.suggestions_action = QAction("View &Suggestions", self)
    self.suggestions_action.triggered.connect(self.show_suggestions_tab)
    tools_menu.addAction(self.suggestions_action)
```

---

### 9.4 Configuration Storage

**New Config Files:**
```
~/.config/trayrunner/
├── commands.yaml          # Existing: User's menu config
├── preferences.yaml       # Existing: GUI preferences
└── learning.yaml          # NEW: Learning system settings

~/.local/state/trayrunner/
├── reload.sock            # Existing: IPC socket
├── trayrunner.lock        # Existing: Single-instance lock
├── run.log                # Existing: Tray execution log
├── gui-debug.log          # Existing: GUI debug log
├── learned_commands.db    # NEW: Command history database
└── ignore_patterns.txt    # NEW: Ignored command patterns
```

**learning.yaml Schema:**
```yaml
# Learning system configuration
learning:
  enabled: false  # Opt-in by default

  # Suggestion thresholds
  min_frequency: 5          # Minimum runs to suggest
  time_window_days: 30      # Consider last 30 days

  # Notification settings
  notifications_enabled: true
  max_notifications_per_day: 1
  min_idle_seconds: 300     # 5 minutes idle

  # Privacy settings
  track_shell_history: true
  track_trayrunner_executions: false  # Don't track commands run from tray

  # Analysis schedule
  auto_analyze: true
  analyze_interval_hours: 24

# Last run metadata
last_analysis: 2025-11-05T14:30:00Z
last_notification: 2025-11-04T16:45:00Z
```

---

## 10. Implementation Phases

### Phase 1: Quick Capture Overlay (MVP)
**Timeline:** 1-2 weeks
**Priority:** High

**Deliverables:**
1. ✅ Quick Capture dialog UI (QDialog component)
2. ✅ Global hotkey registration (pynput integration)
3. ✅ Clipboard auto-fill functionality
4. ✅ Basic smart detection rules (destructive, interactive, git, docker)
5. ✅ Label generation algorithm
6. ✅ Integration with main GUI (save to config)
7. ✅ Success feedback (inline confirmation)
8. ✅ Basic keyboard navigation

**Testing:**
- Manual testing on different desktop environments (GNOME, KDE, XFCE)
- Hotkey conflict detection
- Multi-monitor positioning
- Performance (overlay appears in < 200ms)

**Success Criteria:**
- User can add command to menu in < 10 seconds
- Smart defaults are correct 70% of the time
- No crashes or hangs on common commands

---

### Phase 2: Advanced Features & Polish
**Timeline:** 1 week
**Priority:** Medium

**Deliverables:**
1. ✅ Shell history dropdown integration
2. ✅ Advanced options section (working dir, env vars, group selection)
3. ✅ Multi-line command handling
4. ✅ Command history parsing (bash, zsh, fish)
5. ✅ Duplicate detection (warn if similar command exists)
6. ✅ Dangerous command warnings
7. ✅ Accessibility improvements (ARIA, screen reader)
8. ✅ High contrast theme support

**Testing:**
- Accessibility audit with screen reader (Orca)
- Shell history parsing edge cases
- Complex command formats (pipes, redirects, multi-line)

**Success Criteria:**
- History dropdown loads in < 1 second
- Accessibility score: WCAG AA compliant
- Zero data loss on edge cases

---

### Phase 3: Learning System Foundation
**Timeline:** 2 weeks
**Priority:** Medium

**Deliverables:**
1. ✅ SQLite database schema for command tracking
2. ✅ History parser background service
3. ✅ Frequency analysis algorithm
4. ✅ Suggestion scoring system
5. ✅ Preferences panel for learning settings
6. ✅ Data viewer UI (show tracked commands)
7. ✅ Privacy controls (ignore patterns, data export)
8. ✅ Opt-in onboarding flow

**Testing:**
- Load testing (parse 10,000+ history entries)
- Privacy verification (no sensitive data leaked)
- Score accuracy (manual validation of suggestions)

**Success Criteria:**
- Analysis completes in < 5 seconds
- Suggestion acceptance rate > 30%
- Zero privacy complaints

---

### Phase 4: Intelligent Suggestions
**Timeline:** 1-2 weeks
**Priority:** Medium

**Deliverables:**
1. ✅ Suggestions panel in main GUI
2. ✅ Desktop notification system
3. ✅ Notification scheduler (throttling, idle detection)
4. ✅ Batch suggestion actions (add multiple at once)
5. ✅ Suggestion statistics dashboard
6. ✅ Background analysis scheduler
7. ✅ One-click suggestion acceptance
8. ✅ Integration testing

**Testing:**
- Long-term usage testing (1 week of real usage)
- Notification timing validation
- False positive rate measurement

**Success Criteria:**
- Notification spam < 1 per day
- Suggestion quality: 40%+ acceptance rate
- No performance impact on main GUI

---

### Phase 5: Polish & Documentation
**Timeline:** 1 week
**Priority:** Low

**Deliverables:**
1. ✅ User documentation (markdown guide)
2. ✅ In-app help tooltips
3. ✅ Video tutorial (optional)
4. ✅ Bug fixes from testing
5. ✅ Performance optimizations
6. ✅ Code review and refactoring
7. ✅ Unit tests (pytest)
8. ✅ Release notes

**Testing:**
- Beta testing with 5-10 users
- Performance profiling
- Code coverage > 80%

**Success Criteria:**
- Documentation completeness: 100%
- Zero known critical bugs
- User satisfaction score > 8/10

---

## 11. Open Questions & Future Enhancements

### 11.1 Open Questions

**Q1: Should we support custom global hotkey configuration in GUI?**
- **Current:** Hardcoded `Ctrl+Alt+T` with manual config file editing
- **Pro:** More user-friendly, avoids conflicts
- **Con:** Adds complexity, need hotkey conflict detection UI
- **Decision:** Phase 2 enhancement, not MVP

**Q2: How aggressive should duplicate detection be?**
- **Current Approach:** Exact match + fuzzy match on command base
- **Alternative:** Similarity scoring (Levenshtein distance)
- **Trade-off:** Too aggressive = false positives, too lenient = duplicates
- **Decision:** Start conservative (exact match only), gather user feedback

**Q3: Should suggestions sync across machines?**
- **Use Case:** User has same workflow on desktop + laptop
- **Technical Challenge:** Need sync backend (Git, cloud storage)
- **Privacy Concern:** Command history contains sensitive info
- **Decision:** Future enhancement (Phase 4+), requires careful design

**Q4: How to handle shell aliases in history?**
- **Problem:** User runs `g st` (alias for `git status`) but suggestion shows `g st`
- **Solution:** Expand aliases before suggesting? Or teach alias resolution?
- **Decision:** Phase 3 enhancement, need alias file parsing

**Q5: Should we show command preview/dry-run before adding?**
- **Use Case:** User wants to test if working directory is correct
- **Implementation:** "Test Run" button that executes in terminal
- **Risk:** User might not want to actually run it yet
- **Decision:** Future enhancement, not MVP

---

### 11.2 Future Enhancements

#### Enhancement 1: Command Palette (Fuzzy Launcher)
**Description:** VSCode-style quick launcher for existing menu items

```
Trigger: Ctrl+Shift+P
┌────────────────────────────────────────┐
│ > docker_                               │  ← Type to filter
├────────────────────────────────────────┤
│ Docker List All Containers             │
│ docker ps -a                            │
├────────────────────────────────────────┤
│ Clean Docker Space                      │
│ docker system prune -af                 │
├────────────────────────────────────────┤
│ Build Docker Image                      │
│ docker build -t myapp .                 │
└────────────────────────────────────────┘
```

**Implementation:**
- Fuzzy search across all menu items (label + command)
- Shows recent items at top
- Press Enter to execute immediately
- Press Tab to edit before executing

---

#### Enhancement 2: Context-Aware Suggestions
**Description:** Suggest commands based on current working directory

**Examples:**
- In git repo: Suggest git commands
- In Node.js project: Suggest npm/yarn commands
- In Docker project: Suggest docker-compose commands

**Implementation:**
- Monitor active terminal window's working directory
- Filter suggestions by context
- Add "Context" badge to suggestions ("Git Repo", "Node Project")

---

#### Enhancement 3: Command Templates (Fill-in-the-Blank)
**Description:** Parameterized commands with prompts

**Example:**
```yaml
- label: "SSH to Server"
  cmd: "ssh {username}@{server}"
  parameters:
    username:
      prompt: "Username:"
      default: "admin"
    server:
      prompt: "Server address:"
      type: "text"
```

**When clicked, shows dialog:**
```
┌────────────────────────────────────┐
│ SSH to Server                       │
├────────────────────────────────────┤
│ Username:                           │
│ ┌────────────────────────────────┐ │
│ │ admin                           │ │
│ └────────────────────────────────┘ │
│                                     │
│ Server address:                     │
│ ┌────────────────────────────────┐ │
│ │                                 │ │
│ └────────────────────────────────┘ │
│                                     │
│           [Cancel]  [Connect]       │
└────────────────────────────────────┘
```

---

#### Enhancement 4: Command Chaining
**Description:** Run multiple commands in sequence

**UI:**
```
┌────────────────────────────────────────┐
│ Command Chain: "Deploy to Production"  │
├────────────────────────────────────────┤
│ 1. ✓ git pull                          │
│ 2. ✓ npm run build                     │
│ 3. ⟳ npm run test         [Running...] │
│ 4. ○ ssh deploy@prod "restart app"    │
├────────────────────────────────────────┤
│ Progress: 2/4 complete                  │
│ [Cancel Chain]                          │
└────────────────────────────────────────┘
```

**Features:**
- Stop on first failure (exit code != 0)
- Continue on error (optional)
- Parallel execution (advanced)

---

#### Enhancement 5: AI-Powered Command Generation
**Description:** Natural language → command generation using LLM

**Example:**
```
User types: "list all docker containers including stopped ones"
AI suggests: docker ps -a

User types: "find all files larger than 100MB modified in last week"
AI suggests: find . -type f -size +100M -mtime -7
```

**Implementation:**
- Local LLM (Ollama) or cloud API (OpenAI)
- Opt-in feature (requires API key or local model)
- Safety checks (never auto-execute AI commands)

---

#### Enhancement 6: Visual Command Builder
**Description:** GUI form for constructing commands without memorizing syntax

**Example for rsync:**
```
┌────────────────────────────────────────┐
│ Backup Files (rsync)                   │
├────────────────────────────────────────┤
│ Source Directory:                       │
│ ┌────────────────────────────────────┐ │
│ │ /home/user/documents           [📁]│ │
│ └────────────────────────────────────┘ │
│                                         │
│ Destination Directory:                  │
│ ┌────────────────────────────────────┐ │
│ │ /media/backup                  [📁]│ │
│ └────────────────────────────────────┘ │
│                                         │
│ Options:                                │
│ ☑ Archive mode (-a)                    │
│ ☑ Compress (-z)                        │
│ ☑ Verbose (-v)                         │
│ ☐ Dry run (--dry-run)                  │
│                                         │
│ Exclude patterns:                       │
│ ┌────────────────────────────────────┐ │
│ │ *.tmp                               │ │
│ │ node_modules/                       │ │
│ └────────────────────────────────────┘ │
│                                         │
│ Preview:                                │
│ rsync -avz --exclude='*.tmp' \          │
│   --exclude='node_modules/' \           │
│   /home/user/documents /media/backup    │
│                                         │
│           [Cancel]  [Add to Menu]       │
└────────────────────────────────────────┘
```

---

#### Enhancement 7: Command Output Parsing & Actions
**Description:** Parse command output and offer follow-up actions

**Example:**
```
User runs: docker ps
Output shows container "myapp" with status "Exited(1)"

System offers:
┌────────────────────────────────────────┐
│ Container "myapp" is not running        │
│                                         │
│ [View Logs]  [Start Container]  [OK]   │
└────────────────────────────────────────┘
```

**Implementation:**
- Define output patterns in config
- Regex-based matching
- Templated follow-up commands

---

### 11.3 Community Feedback Collection

**Beta Testing Plan:**
1. Release MVP to 10-20 beta users
2. Collect feedback via:
   - In-app feedback form (optional)
   - GitHub issues/discussions
   - User interviews (1-on-1)
3. Metrics to track:
   - Quick capture usage frequency
   - Smart default accuracy (% changed)
   - Suggestion acceptance rate
   - Time saved vs. manual config editing

**Survey Questions:**
1. How often do you use Quick Capture? (Daily / Weekly / Rarely)
2. How accurate are the smart defaults? (1-5 scale)
3. Did you enable the learning system? Why or why not?
4. What command types are missing from smart detection?
5. Would you pay for premium features (AI, templates, sync)? How much?

---

## 12. Appendix

### A. Glossary

**Quick Capture Overlay** - The floating dialog window triggered by global hotkey for fast command addition

**Smart Detection** - Automated analysis of command text to recommend appropriate settings

**Learning System** - Background service that analyzes shell history to suggest frequently-run commands

**Suggestion** - A command identified by the learning system as a candidate for menu addition

**Detection Rule** - A pattern-matching algorithm that identifies command characteristics

**History Entry** - A record of a command executed in the shell, including timestamp and metadata

**Working Directory Context** - The file system path where a command should be executed

---

### B. References

**Qt/PySide6 Documentation:**
- QDialog: https://doc.qt.io/qtforpython/PySide6/QtWidgets/QDialog.html
- QKeySequence: https://doc.qt.io/qtforpython/PySide6/QtGui/QKeySequence.html
- Accessibility: https://doc.qt.io/qt-6/accessible.html

**Desktop Integration:**
- freedesktop.org notifications: https://specifications.freedesktop.org/notification-spec/
- X11 key grabbing: https://tronche.com/gui/x/xlib/input/XGrabKey.html
- Wayland global shortcuts: https://wayland.freedesktop.org/

**Shell History Formats:**
- Bash history: https://www.gnu.org/software/bash/manual/html_node/Bash-History-Facilities.html
- Zsh history: http://zsh.sourceforge.net/Doc/Release/Options.html#History
- Fish history: https://fishshell.com/docs/current/cmds/history.html

**WCAG Accessibility:**
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- Color contrast checker: https://webaim.org/resources/contrastchecker/

---

### C. Mockup Assets

**Icons to Source:**
- Quick capture icon: Lightning bolt (⚡) or keyboard (⌨)
- Suggestion icon: Light bulb (💡)
- Detection icons: Checkmark (✓), info (ⓘ), warning (⚠)
- Command type icons: Git (🔄), Docker (🐳), System (🔧), Network (🌐)

**Color Palette:**
```
Primary Blue:    #007ACC
Success Green:   #28A745
Warning Yellow:  #FFC107
Danger Red:      #DC3545
Info Blue:       #2196F3
Gray:            #6C757D
Light Gray:      #E0E0E0
Background:      #FFFFFF / #2D2D30 (dark)
Text:            #212529 / #CCCCCC (dark)
```

---

### D. Code Examples

**Quick Capture Dialog Skeleton:**
```python
# gui/trayrunner_gui/quick_capture_dialog.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QShortcut, QKeySequence

class QuickCaptureDialog(QDialog):
    """Quick command capture overlay"""

    command_added = Signal(dict)  # Emits command data when saved

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.apply_styling()

        # Initialize services
        self.detection_engine = DetectionRuleEngine()
        self.history_parser = ShellHistoryParser()

    def setup_ui(self):
        """Build UI components"""
        self.setWindowTitle("Quick Command Capture")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(False)
        self.setFixedWidth(600)

        layout = QVBoxLayout()

        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Paste command here...")
        layout.addWidget(self.command_input)

        # Label input
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Menu item name...")
        layout.addWidget(self.label_input)

        # Add button
        self.add_button = QPushButton("Add to Menu")
        self.add_button.setDefault(True)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def setup_connections(self):
        """Connect signals"""
        self.command_input.textChanged.connect(self.on_command_changed)
        self.add_button.clicked.connect(self.on_add_clicked)

        # Escape to close
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.close)

    def on_command_changed(self, text):
        """Run smart detection when command changes"""
        results = self.detection_engine.analyze(text)
        # Update UI with results...

    def on_add_clicked(self):
        """Save command to config"""
        command_data = {
            'label': self.label_input.text(),
            'cmd': self.command_input.text(),
            # ... other fields
        }
        self.command_added.emit(command_data)
        self.close()

    def showEvent(self, event):
        """Called when dialog is shown"""
        super().showEvent(event)

        # Auto-fill from clipboard
        clipboard = QApplication.clipboard()
        if clipboard.text():
            self.command_input.setText(clipboard.text())

        # Focus label input
        self.label_input.setFocus()
```

---

**Detection Rule Example:**
```python
# gui/trayrunner_gui/detection_rules.py

import re
from abc import ABC, abstractmethod

class DetectionRule(ABC):
    """Base class for command detection rules"""

    @abstractmethod
    def matches(self, command: str) -> bool:
        """Returns True if rule applies"""
        pass

    @abstractmethod
    def get_recommendations(self, command: str) -> dict:
        """Returns recommended settings"""
        pass

class DestructiveCommandRule(DetectionRule):
    """Detect destructive operations"""

    PATTERNS = [
        r'\brm\b.*-[rf]',
        r'\bprune\b',
        r'\bdelete\b',
        r'\bdrop\b',
    ]

    def matches(self, command: str) -> bool:
        return any(re.search(p, command) for p in self.PATTERNS)

    def get_recommendations(self, command: str) -> dict:
        return {
            'confirm': True,
            'reason': "Detected: Destructive operation",
            'confidence': 0.9,
        }

class GitCommandRule(DetectionRule):
    """Detect git commands"""

    def matches(self, command: str) -> bool:
        return command.strip().startswith('git ')

    def get_recommendations(self, command: str) -> dict:
        # Parse subcommand
        parts = command.split()
        subcommand = parts[1] if len(parts) > 1 else ''

        label = f"Git {subcommand.capitalize()}"

        return {
            'label': label,
            'group': 'Git Commands',
            'working_dir': '.',  # Current directory
            'reason': "Detected: Git command (working directory aware)",
            'confidence': 0.85,
        }
```

---

## Conclusion

This design specification provides a complete blueprint for implementing TrayRunner's Quick Command Capture & Learning feature. The design prioritizes:

1. **Speed**: Sub-10-second workflow from command execution to menu item
2. **Intelligence**: Smart defaults that are right 80% of the time
3. **Privacy**: Opt-in learning with transparent data practices
4. **Accessibility**: WCAG AA compliant, fully keyboard navigable
5. **User Control**: Easy to customize, override, or disable features

**Next Steps:**
1. Review and approve this design specification
2. Create detailed implementation tickets for Phase 1 (MVP)
3. Set up development environment with PySide6 + pynput
4. Begin UI component implementation
5. Iterate based on user testing feedback

**Contact:**
For questions or feedback on this design, please open an issue in the TrayRunner GitHub repository or contact the maintainers.

---

**Document Version History:**
- v1.0 (2025-11-05): Initial comprehensive design specification
