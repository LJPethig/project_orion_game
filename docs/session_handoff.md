# PROJECT ORION — SESSION HANDOFF
## Current state: see Project_Orion_Design_v26.md and Project_Orion_Future_v4.md

Attached is the complete current codebase as a zip. Read every file before doing anything.
Do not work from memory or assumptions — the code is the authority.

---

## What was completed this session

- Save/load system — fully implemented and tested (Phase 19.5)
- Event resolution — components checked against affected_components list, strip cleared, log written
- Event strip — static (no flash) on load, flashing on live fire, green blink on resolution
- All event strings moved to events.json — no hardcoded strings in logic
- Quit command removed — rest is the only quit point
- New Game deletes save files before starting
- Docs updated: Project_Orion_Design_v26.md, Project_Orion_Future_v4.md
- save_load_design.md deleted — content absorbed into Design v26

---

## Working rules — these are non-negotiable and have been repeatedly violated

These rules exist for good reason. Violations waste time, cause bugs, and erode trust.
The AI must follow them without exception.

### File handling
- **Read every uploaded file completely before touching anything — no exceptions**
- **Ask for files before making any changes — never work from memory or guess at code structure**
- **If a file has not been uploaded this session, ask for it**
- **Never assume the code matches what was written in a previous turn — the uploaded file is authoritative**

### Making changes
- **One change at a time — verify it works before proceeding to the next**
- **Inline find/replace instructions for existing files — complete file downloads only for new files or very extensive rewrites**
- **Minimal targeted changes only — no unrequested improvements, no "while I'm in here" edits**
- **Give explicit, searchable find/replace instructions — exact strings that appear once in the file**

### Code quality
- **No lazy imports — all imports at the top of the file. The only legitimate exception is a genuine circular import risk, which must be explicitly documented**
- **No silent fallbacks — bad data must crash loudly with a clear message, never degrade silently**
- **No hardcoded strings that belong in data files — if it could vary per event/item/room, it goes in JSON**
- **No dead code — if it is not used, remove it**
- **Backend owns all game state — JS is display only**
- **No god files — one concern per file, grouped by domain**

### Constants and configuration
- **All JS timeouts and durations in `constants.js`**
- **All Python durations and timing in `config.py`**
- **All Python player/ship constants in `config.py`**
- **All colours in CSS variables**

### Design
- **Push back on bad design — do not silently implement something that seems wrong**
- **Suggest before adding — flag anything not in the spec before writing code**
- **Never add "type X to fix it" hints — immersive messages only**
- **All JSON fields must have a use — never partially load type definitions**

### What happened when these rules were ignored this session
- Lazy imports caused crashes
- Hardcoded strings had to be refactored out after the fact
- Changes were made without reading the current file, producing instructions for code that didn't match reality
- Multiple rounds of fixes were needed for problems that should not have existed

---

## Session notes

**Door trap — unpowered panel on destination side**
When Jack passes through a closed door, if the destination-side panel is non-functional (broken or unpowered), the door auto-closes and traps him. Correct behaviour given current logic but creates a potential softlock. No decision made on fix.

Possible approaches under consideration:
- Don't auto-close if destination-side panel is non-functional
- Emergency mechanical release (ship regulation, condition reflects Enso VeilTech neglect)
- Cutting equipment for forced entry (later mechanic)
