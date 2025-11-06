# TrayRunner Feature Ideas

This document contains innovative feature ideas to enhance TrayRunner's functionality, usability, and value proposition. Each feature has been carefully considered for technical feasibility within the existing architecture.

---

## 1. Context-Aware Dynamic Menus

**Priority:** Medium Effort

**Description:**
Transform TrayRunner from a static menu launcher into an intelligent context-aware assistant. Menu items can dynamically show/hide or modify their labels based on system context, file presence, or running processes. For example, a "Start Docker" item automatically becomes "Stop Docker" when Docker is running, or Git commands only appear when you're in a git repository.

**Use Case:**
A developer has TrayRunner configured with project-specific commands. When they `cd` into a project directory, their tray menu automatically shows relevant commands for that project (build, test, deploy). When Docker isn't running, they see "Start Docker Desktop", but once it's running, the label changes to "Stop Docker Desktop" with an indicator showing it's active. Git-related commands only appear when the active terminal window is in a git repository.

**Implementation Notes:**
- Add new schema fields: `visible_when` (shell command that returns exit code 0 for visible), `dynamic_label` (command to generate label text), and `update_interval` (how often to check)
- Extend the tray app to periodically evaluate these conditions and rebuild the menu
- Cache results to avoid excessive system calls
- Use a worker thread to avoid blocking the GUI
- Add visual indicators (checkmarks, colors) for active states
- Store "current working directory context" by monitoring active window or allowing users to set it via a special menu item

**Technical Considerations:**
- Requires periodic menu rebuilding (every 5-10 seconds)
- Add caching layer to prevent flickering
- Use `subprocess.run()` with short timeouts for condition checks
- Could leverage existing IPC infrastructure for context updates

---

## 2. Quick Command Capture & Learning

**Priority:** Quick Win

**Description:**
A floating "Record Command" overlay that captures terminal commands you run and instantly converts them into TrayRunner menu items. Hit a hotkey, paste a command you just ran, and it's added to your tray menu with smart defaults. Over time, TrayRunner learns which commands you run frequently from its logs and suggests "Frequently Run Commands" that aren't yet in your menu.

**Use Case:**
Sarah runs `docker system prune -af` to clean up Docker space. Instead of remembering the complex command, she hits `Ctrl+Alt+T`, pastes the command into the quick capture dialog, gives it a friendly name like "Clean Docker Space", and checks "Needs Confirmation". It's instantly added to her tray menu. A week later, TrayRunner notices she's run `git pull --rebase origin main` five times manually and suggests adding it as a menu item.

**Implementation Notes:**
- Create a new lightweight Qt window with hotkey listener (using `pynput` or similar)
- Parse command history from `~/.bash_history`, `~/.zsh_history`
- Analyze command frequency in TrayRunner's execution logs (`~/.local/state/trayrunner/run.log`)
- Smart defaults: detect `sudo` for confirmation, detect interactive commands for terminal flag
- Add "Suggested Items" submenu in Settings that shows learned commands
- One-click "Add to Menu" button that opens the GUI editor with pre-filled values
- Could use simple ML (frequency analysis, time-since-last-run) for suggestions

**Technical Considerations:**
- Global hotkey requires `python-xlib` or `pynput` library
- Parse shell history files safely (handle different shells)
- Privacy consideration: make this opt-in with clear data usage explanation
- Store learning data in `~/.local/state/trayrunner/learned_commands.json`

---

## 3. Visual Command Builder & Template Library

**Priority:** Ambitious

**Description:**
A guided command builder that helps users create complex commands without memorizing syntax. Think of it as "command snippets" meet "form builder". TrayRunner ships with a library of 50+ common Linux task templates (backup, network diagnostics, system monitoring, Docker operations, etc.) that users can customize through visual forms. Users can also share their own templates via import/export.

**Use Case:**
Alex wants to create a backup command but can't remember `rsync` syntax. They click "Add Item" → "From Template" → "Backup Directory". A form appears asking for source directory, destination, and options (compress? exclude patterns? dry run?). They fill it out visually, and TrayRunner generates `rsync -avz --exclude='*.tmp' /home/alex/documents /media/backup/`. The template library includes: system monitoring (disk, memory, network), Docker operations (cleanup, logs, restart containers), Git workflows (stash, branch, cherry-pick), and file operations (search, batch rename, permissions).

**Implementation Notes:**
- Create new `TemplateNode` schema type with form field definitions
- Templates stored as JSON with field definitions: `{name, type, default, validation, help_text}`
- Ship built-in templates in `config/templates/` directory (separate YAML files)
- Add "Template Browser" tab in GUI editor with search/filter
- Form generator dynamically creates Qt widgets based on template field definitions
- Support field types: text, path, dropdown, checkbox, multi-select
- Export command templates as shareable `.trt` (TrayRunner Template) files
- Community template repository (future: GitHub integration to browse/install)

**Technical Considerations:**
- Templates need versioning for compatibility
- Validation of generated commands (dry-run simulation)
- Template marketplace would require moderation (security concern)
- Could use Jinja2 for command template rendering
- Start with 20 high-value templates, expand based on usage

---

## 4. Output Capture & Result Inspector

**Priority:** Medium Effort

**Description:**
Transform TrayRunner from a "fire and forget" launcher into a results-aware dashboard. After running commands, capture their output in a persistent history panel. Get desktop notifications when long-running commands complete (with success/failure indicators). Inspect past command outputs, search through results, and re-run previous commands with one click. It's like having a universal command history for all your tray actions.

**Use Case:**
A DevOps engineer runs "Check Server Status" from their tray. Instead of output disappearing, it's captured in TrayRunner's History panel with a timestamp and exit code. The output shows 3 servers down. They click "Re-run" 5 minutes later and see only 1 server still down. They can search their history for "error" to find all failed command runs from the past week. When their 10-minute backup script finishes, they get a notification showing it completed successfully with file count and size.

**Implementation Notes:**
- Extend `CommandRunner` to capture stdout/stderr for all non-terminal commands
- Store outputs in SQLite database at `~/.local/state/trayrunner/history.db`
- Schema: `(timestamp, command_label, cmd, exit_code, stdout, stderr, duration)`
- Create new "History" panel in GUI editor (or separate History Viewer app)
- Add notification system for command completion (configurable per-item)
- Search functionality with regex support
- Retention policy (keep last 1000 runs, or last 30 days)
- Add toolbar button to main tray menu: "Show Recent Results"
- New item property: `notify_on_completion` (boolean)

**Technical Considerations:**
- Large outputs need truncation (store first/last 10KB)
- Database cleanup/rotation to prevent unbounded growth
- For terminal commands, this won't work (they control their own output)
- Could show real-time output in a floating window for background commands
- Needs careful memory management for concurrent command runs

---

## 5. Cross-Machine Sync & Profile Switching

**Priority:** Ambitious

**Description:**
Sync your TrayRunner configuration across multiple machines and support different profiles for different contexts (work, home, server admin). Sync happens via Git, cloud storage (Dropbox, Nextcloud), or SSH. Switch between profiles with one click - "Work" profile shows work-related commands, "Personal" shows home automation, "Server Admin" shows deployment scripts. Include machine-specific variable substitution so the same config works everywhere.

**Use Case:**
Jordan maintains three machines: work laptop, home desktop, and a Raspberry Pi server. They create a "base" TrayRunner config with common commands, then machine-specific profiles. The config includes variables like `${PROJECTS_DIR}` that resolve to `/home/jordan/work/projects` on the laptop but `/opt/projects` on the server. They edit their config on the laptop, push to their private Git repo, and their home desktop automatically pulls the changes. At work, they use "Work Profile" which shows corporate VPN, deployment, and meeting commands. At home, they switch to "Personal Profile" with home automation, media server, and hobby project commands.

**Implementation Notes:**
- New schema: `profiles` section in YAML with profile-specific item overrides
- Profile file structure: `~/.config/trayrunner/profiles/{profile_name}.yaml`
- Variable substitution using `${VAR_NAME}` syntax, resolved from environment or profile-specific vars
- Sync backends:
  - Git: Initialize git repo in `~/.config/trayrunner/`, auto-commit/push/pull
  - Cloud: Monitor cloud folder for changes (use file watcher)
  - SSH: rsync to/from remote machines on schedule
- Add "Profile" menu in tray with quick switcher
- Machine identification via hostname or custom machine ID
- Conflict resolution: last-write-wins with backup creation
- GUI shows which profile is active and allows editing profile-specific settings

**Technical Considerations:**
- Git backend easiest to implement (use `subprocess` for git commands)
- Conflict handling is complex - start with simple last-write-wins
- Security: SSH requires key management, credentials storage
- Variable substitution needs escaping to avoid shell injection
- Profile switching requires full config reload
- Could use existing `ruamel.yaml` comment preservation for profile metadata
- Future: profile inheritance (base profile + machine-specific overrides)

---

## Feature Comparison Matrix

| Feature | Priority | Complexity | User Impact | Innovation Score |
|---------|----------|------------|-------------|------------------|
| Context-Aware Dynamic Menus | Medium Effort | Medium | High | 9/10 |
| Quick Command Capture | Quick Win | Low | High | 7/10 |
| Visual Command Builder | Ambitious | High | Very High | 8/10 |
| Output Capture & Inspector | Medium Effort | Medium | High | 8/10 |
| Cross-Machine Sync | Ambitious | High | Medium | 7/10 |

---

## Implementation Roadmap Suggestion

**Phase 1 - Quick Wins (1-2 weeks):**
- Quick Command Capture & Learning
  - Gets users immediately productive
  - Generates goodwill and engagement
  - Provides data for future ML features

**Phase 2 - Power User Features (1 month):**
- Output Capture & Result Inspector
  - Huge quality-of-life improvement
  - Differentiates from other launchers
  - Foundation for monitoring/alerting features

**Phase 3 - Intelligence Layer (2 months):**
- Context-Aware Dynamic Menus
  - Makes TrayRunner feel "smart"
  - Reduces menu clutter
  - Opens door to automation workflows

**Phase 4 - Ecosystem Building (3+ months):**
- Visual Command Builder & Template Library
  - Lowers barrier to entry for new users
  - Creates community engagement (template sharing)
  - Potential for marketplace/monetization
- Cross-Machine Sync & Profile Switching
  - Critical for power users with multiple machines
  - Enables team/organization adoption
  - Premium feature potential

---

## Bonus Ideas (Honorable Mentions)

These didn't make the top 5 but are worth considering:

- **Clipboard Command Palette:** Quick fuzzy-search launcher (like VSCode Command Palette) triggered by hotkey
- **Voice Command Integration:** Use speech recognition to trigger menu items hands-free
- **System Monitor Integration:** Show CPU/RAM/Disk as sub-labels on tray icon, with alert thresholds
- **Scheduled Commands:** Cron-like scheduling integrated into menu items
- **Command Chaining & Workflows:** Define multi-step sequences with conditional execution
- **Mobile Companion App:** Trigger commands on your Linux desktop from your phone
- **Integration Hub:** Pre-built integrations with popular tools (GitHub, Docker, systemd, Kubernetes)
- **Smart Notifications:** Detect errors in command output and show actionable alerts
- **Accessibility Features:** Screen reader support, high contrast themes, keyboard-only navigation
- **Command Analytics Dashboard:** Visualize which commands you use most, time spent, success rates

---

## Contributing

Have ideas for TrayRunner features? We'd love to hear them! Please:
1. Check if a similar idea already exists in GitHub Issues
2. Open a new issue with the "enhancement" label
3. Describe the problem you're solving and your proposed solution
4. Include use cases and implementation thoughts if you have them

Let's make TrayRunner the most powerful and delightful command launcher for Linux!
