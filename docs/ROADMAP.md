# TrayRunner Development Roadmap

This roadmap organizes proposed features into three priority tiers based on user value, implementation complexity, architectural fit, and alignment with TrayRunner's core mission as a lightweight system tray command launcher.

**Evaluation Criteria:**
- **User Impact**: Does this solve a real pain point or significantly enhance workflows?
- **Implementation Complexity**: How much effort considering GTK/Qt boundaries, IPC requirements, and AppImage constraints?
- **Architectural Fit**: Does this align with TrayRunner's two-process design and Linux desktop conventions?
- **Risk to Stability**: Will this require major refactoring or introduce backwards compatibility issues?

---

## Now (Next Release - High Priority)

These features deliver immediate value, align with current architecture, and have manageable implementation scope. They enhance TrayRunner's core use case without requiring significant refactoring.

### 1. Quick Command Capture & Learning

**Status:** Ready for Implementation

**Rationale:**
- **Highest ROI feature** - Low complexity, high user delight
- Solves real pain point: bridging the gap between terminal commands and tray menus
- Requires minimal architectural changes (new Qt dialog + log analysis)
- No schema changes needed initially - can generate standard ItemNodes
- Builds user engagement immediately

**Technical Approach:**
- Phase 1: Simple Qt dialog with global hotkey (using `pynput`) to capture command text
- Phase 2: Parse shell history (`~/.bash_history`, `~/.zsh_history`) for suggestions
- Phase 3: Analyze `~/.local/state/trayrunner/run.log` for frequently-used TrayRunner commands
- Store learning data in `~/.local/state/trayrunner/learned_commands.json`
- Opens GUI editor pre-populated with captured command

**Implementation Estimate:** 1-2 weeks

**Dependencies:** None

**Files Affected:**
- New: `gui/trayrunner_gui/quick_capture.py` (capture dialog)
- New: `gui/trayrunner_gui/services/command_learner.py` (history analysis)
- Minor: `gui/trayrunner_gui/main_window.py` (integrate capture dialog)

---

### 2. Output Capture & Result Inspector

**Status:** Ready for Implementation

**Rationale:**
- **Transforms TrayRunner into results-aware tool** instead of fire-and-forget launcher
- Addresses common complaint: "I ran a command but don't know if it worked"
- Natural evolution of existing command execution infrastructure
- Desktop notifications align with Linux desktop best practices
- SQLite storage is straightforward and self-contained

**Technical Approach:**
- Extend `CommandRunner` in `src/trayrunner/app.py` to capture stdout/stderr for non-terminal commands
- Store in SQLite: `~/.local/state/trayrunner/history.db`
- Schema: `(id, timestamp, label, cmd, exit_code, stdout, stderr, duration_ms)`
- Add new GUI panel or standalone viewer app to browse history
- Use `notify-send` or `gi.repository.Notify` for completion notifications
- New item property: `notify_on_completion` (boolean) in schema

**Implementation Estimate:** 2-3 weeks

**Dependencies:** None (but synergizes with Quick Command Capture)

**Files Affected:**
- Modified: `src/trayrunner/app.py` (capture output in `CommandRunner`)
- Modified: `gui/trayrunner_gui/models/schema.py` (add `notify_on_completion` field)
- New: `src/trayrunner/history_db.py` (SQLite management)
- New: `gui/trayrunner_gui/history_panel.py` (history viewer UI)

**Important Constraints:**
- Terminal commands (`terminal: true`) cannot capture output - document this limitation
- Large outputs need truncation (keep first/last 10KB to prevent DB bloat)
- Retention policy: last 1000 runs OR 30 days (user configurable)

---

## Next (Following Release - Important but More Complex)

These features provide significant value but require deeper architectural work, have more dependencies, or need careful UX design to avoid bloating TrayRunner's simplicity.

### 3. Context-Aware Dynamic Menus

**Status:** Needs Design Review

**Rationale:**
- **High innovation value** - makes TrayRunner feel intelligent
- Solves menu clutter by showing only relevant commands
- Requires periodic menu rebuilding - moderate complexity
- Risk of performance impact if not implemented carefully
- Needs caching layer to prevent menu flicker

**Technical Approach:**
- Add schema fields: `visible_when` (shell command returning exit 0/1), `dynamic_label` (command for label text), `update_interval` (seconds)
- Tray app runs evaluation thread checking conditions every 5-10 seconds
- Cache results to avoid excessive system calls
- Use `subprocess.run()` with 500ms timeout for safety
- Visual indicators: prepend checkmark/dot to labels for active states
- Context tracking: monitor active window or allow manual "set context" menu item

**Implementation Estimate:** 3-4 weeks

**Dependencies:**
- Output Capture feature would enhance this (reuse execution infrastructure)
- Requires careful performance testing on older hardware

**Files Affected:**
- Modified: `gui/trayrunner_gui/models/schema.py` (new fields)
- Modified: `src/trayrunner/app.py` (periodic menu rebuild logic)
- New: `src/trayrunner/context_evaluator.py` (condition checking with caching)

**Risks:**
- Menu flicker if rebuild isn't atomic
- Performance on systems with many conditional items
- Shell command injection if not properly sanitized

**Recommendation:** Start with simple proof-of-concept (single `visible_when` field) before full dynamic labels

---

### 4. Visual Command Builder & Template Library (Phase 1)

**Status:** Needs Scoping - Start with Core Templates Only

**Rationale:**
- **Lowers barrier for non-technical users** (expands user base)
- Templates could become community-driven feature (ecosystem building)
- High implementation complexity - requires new schema type and form generator
- Risk of scope creep - template marketplace adds security concerns
- Start small: 15-20 curated built-in templates, no sharing initially

**Technical Approach (Phase 1 - Built-in Templates Only):**
- Ship curated templates as separate YAML files in `config/templates/`
- Template format: field definitions with type, validation, help text
- Add "New from Template" button in GUI that shows template browser
- Form generator creates Qt widgets dynamically based on template schema
- Templates compile to standard ItemNodes (no new node type needed initially)
- Field types: text, file_path, directory_path, dropdown, checkbox

**Example Templates to Include:**
- System: disk usage, memory check, process management
- Docker: cleanup, container logs, restart services
- Git: common workflows (stash, branch, rebase)
- Backup: rsync patterns, tar archives
- Network: diagnostics, SSH tunnels, port checks

**Implementation Estimate:** 4-5 weeks (template library + form builder)

**Dependencies:** None, but benefits from Quick Capture (users can save customized templates)

**Files Affected:**
- New: `config/templates/*.yaml` (15-20 template definitions)
- New: `gui/trayrunner_gui/template_browser.py` (template selection UI)
- New: `gui/trayrunner_gui/form_builder.py` (dynamic form generator)
- Modified: `gui/trayrunner_gui/main_window.py` (add template workflow)

**Future Phases:**
- Phase 2: User-created templates saved to `~/.config/trayrunner/templates/`
- Phase 3: Import/export as `.trt` files
- Phase 4: Community template repository (requires moderation strategy)

---

## Later (Future Consideration)

These features are interesting but either require significant rework, have unclear user demand, or risk adding complexity that conflicts with TrayRunner's lightweight philosophy. Consider after gathering more user feedback.

### 5. Cross-Machine Sync & Profile Switching

**Status:** Defer Until User Demand Confirmed

**Rationale:**
- **Solves niche problem** - most users maintain single primary machine
- High complexity: sync conflicts, credential management, multi-backend support
- Profile switching requires full config reload (impacts UX)
- Git backend is most practical, but requires git knowledge
- Cloud/SSH backends add dependencies and security surface

**Alternative Approach (Simpler):**
- Most users can manually manage configs via Git without TrayRunner integration
- Document best practices: "How to sync TrayRunner configs with Git"
- Add environment variable substitution (`${VAR_NAME}`) to existing schema without full profile system
- Defer full profile/sync implementation until 50+ users request it

**Why Not Now:**
- Unproven user demand (speculative feature)
- Adds significant testing burden (conflict resolution, sync reliability)
- Could be built as external tool/plugin rather than core feature

**Reconsider When:** GitHub issue receives 20+ upvotes requesting this feature

---

### 6. Bonus Features - Evaluate Individually

Several bonus ideas from FEATURE_IDEAS.md deserve standalone evaluation:

**Consider for "Next" Tier:**
- **Command Chaining & Workflows**: Natural extension of existing execution model, moderate complexity
- **Scheduled Commands**: Integrates with systemd timers, aligns with Linux conventions

**Consider for "Later" Tier:**
- **Clipboard Command Palette**: Fuzzy search launcher - competes with rofi/dmenu, unclear fit
- **System Monitor Integration**: Scope creep - dedicated tools do this better
- **Integration Hub**: Too broad - focus on core functionality first
- **Command Analytics Dashboard**: Low priority until TrayRunner has large user base

**Do Not Implement (Out of Scope):**
- **Voice Command Integration**: Hardware dependencies, accessibility concerns, niche use case
- **Mobile Companion App**: Requires network protocol, mobile app development, ongoing maintenance
- **Smart Notifications**: Overlaps with Output Capture feature (include as part of that)

---

## Implementation Strategy

### Recommended Development Order (Next 6 Months)

**Milestone 1 (Weeks 1-2): Foundation**
- Implement Quick Command Capture (core feature only, no learning)
- Add global hotkey support
- Create command capture dialog

**Milestone 2 (Weeks 3-5): Results Infrastructure**
- Implement Output Capture & Result Inspector
- Add SQLite history database
- Create basic history viewer UI
- Add completion notifications

**Milestone 3 (Weeks 6-7): Learning Enhancement**
- Add shell history parsing to Quick Capture
- Implement frequency analysis from TrayRunner logs
- Create "Suggested Commands" panel

**Milestone 4 (Weeks 8-11): Intelligence Layer**
- Implement Context-Aware Dynamic Menus (simplified version)
- Add `visible_when` field to schema
- Create condition evaluator with caching
- Add visual indicators for active states

**Milestone 5 (Weeks 12-16): Template System (If Demand Confirmed)**
- Design template YAML format
- Create 15-20 curated templates
- Build template browser UI
- Implement dynamic form generator

### Testing Requirements

Each feature must include:
- Unit tests for core logic
- Integration tests for IPC interactions
- Manual testing on Ubuntu 20.04 and 22.04
- Performance testing with large configs (100+ items)
- AppImage smoke tests after bundling

### Documentation Requirements

Each feature must include:
- User-facing documentation in README or wiki
- Developer notes in CLAUDE.md if architectural changes
- Example configurations
- Known limitations clearly stated

---

## Feature Dependencies & Risks

### Dependency Graph

```
Quick Command Capture (standalone)
    |
    +-- enables --> Command Learning (uses capture UI)
    |
    +-- synergizes --> Output Capture (share execution insights)
                          |
                          +-- enables --> Context-Aware Menus (reuse evaluation logic)
                                              |
                                              +-- informs --> Template Library (context-aware templates)
```

### Key Risks to Manage

1. **Performance Degradation**: Context-aware features could slow down menu rendering
   - Mitigation: Aggressive caching, background threads, timeout limits

2. **Scope Creep**: Template library could balloon into marketplace/plugin system
   - Mitigation: Ship minimal viable version, iterate based on feedback

3. **IPC Complexity**: New features may strain single reload socket
   - Mitigation: Consider expanding IPC protocol early (version negotiation)

4. **AppImage Bloat**: Adding dependencies increases bundle size
   - Mitigation: Audit dependencies, consider making features optional

5. **Backwards Compatibility**: Schema changes must not break existing configs
   - Mitigation: All new fields must be optional with sensible defaults

---

## Success Metrics

Track these metrics to validate roadmap decisions:

- **Adoption Rate**: Quick Capture usage vs. traditional GUI editing (target: 40% of new items via capture)
- **Command Frequency**: % of commands run more than once (validates History feature value)
- **Template Usage**: % of users who create items from templates (validates builder investment)
- **User Retention**: Active users 30 days after installing new features (target: 60%)
- **GitHub Engagement**: Issues/PRs related to new features (validates community interest)

---

## Conclusion

This roadmap prioritizes features that enhance TrayRunner's core value proposition (quick command access) while respecting its architectural constraints (two-process design, AppImage distribution, Linux conventions). The "Now" tier focuses on immediate productivity wins with minimal risk. The "Next" tier builds intelligence and accessibility for broader adoption. The "Later" tier acknowledges interesting ideas that need validation before investment.

**Recommended Next Steps:**
1. Get community feedback on this roadmap via GitHub Discussion
2. Create detailed implementation specs for Quick Command Capture
3. Set up project board to track milestone progress
4. Begin development on Milestone 1

Last Updated: 2025-11-05
