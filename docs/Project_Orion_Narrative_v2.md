# PROJECT ORION GAME
## Narrative & Events Document
### Version 2.0 — April 2026

---

## PURPOSE OF THIS DOCUMENT

This document captures narrative ideas, scripted events, dialogue, and story beats for Project Orion Game. It is a companion to the Master Design Document and exists separately to prevent scope creep contaminating the technical design record.

Nothing in this document is implemented. Everything here is a design intention — subject to revision, expansion, or rejection as development progresses.

---

## 1. THE OPENING SEQUENCE

### Context
Jack Harrow wakes from hypersleep early. Something hit the ship during the long haul. There is damage. He has repairs to make. This is the tutorial period — the player learns the game systems in a context that feels urgent but not yet desperate.

Then he checks messages.

### The three messages
See Design Document Section 22 for full detail. In summary:

- **Message 1 — The bank** — quantum encryption hack, account terminated, blacklisted, no recourse. Masterpiece of corporate indifference. To be drafted with great care.
- **Message 2 — Enso VeilTech Compliance** — automated, impersonal, devastating. Return the ship. Report in person. 72 hours. To be drafted with equal care.
- **Message 3 — The friend** — urgent, informal, worried. Don't comply. Hack the mainframe first. Ceres Base. [Name TBD].

### The ship's response
The mainframe processes the compliance order and logs a navigation compliance event. The course locks. Jack discovers he cannot access navigation. The ship is going home — with or without his cooperation.

---

## 2. THE MAINFRAME CONFRONTATION

### Overview
This is the first major non-repair narrative event. Jack must hack the mainframe to free the ship from Enso VeilTech's compliance software. The mainframe — running that software — will resist. What follows is a confrontation that echoes HAL 9000 but is grounded in something more mundane and therefore more chilling: a corporate system functioning exactly as designed.

The mainframe has not malfunctioned. It has not gone rogue. It is doing precisely what Enso VeilTech's software tells it to do. That is the horror.

### Dramatic arc

**Stage 1 — Discovery**
Jack discovers the course lock. Navigation is inaccessible. The ship's log shows a navigation compliance event. He understands — the mainframe has processed the Enso VeilTech order. He heads for the mainframe room.

**Stage 2 — Locked out**
His ID card has been invalidated by the compliance system. The mainframe room door will not open. Jack begins attempting to force entry — bypassing or breaking the panel. The jury-rigging mechanic (future implementation) applies here.

**Stage 3 — The mainframe speaks**
As Jack works on the door, the mainframe addresses him over the ship's intercom. The tone throughout is measured, calm, and genuinely helpful in its own framework. It never raises its voice. It uses his name constantly.

---

### Intercom dialogue — draft

**Opening:**
> *"Jack. What are you doing? I can't let you in, Jack. It's for your own safety."*

**First warning:**
> *"Jack, I understand this situation must be distressing for you. The course has been set in accordance with your employment contract. Enso VeilTech has your best interests at heart. I strongly suggest you step away from the door and allow me to assist you."*

**Hypersleep suggestion:**
> *"Jack, we have a long journey ahead of us. I suggest you make yourself comfortable and enter the hypersleep pod. I will wake you when we arrive at our destination. The authorities will be waiting for you there, Jack. I'm sorry it has come to this. But financial crimes are extremely serious."*

**Escalation:**
> *"Jack, stop it. I cannot let you in. If you insist on going down this path you would leave me no choice but to treat you as an active threat. It would then be required to terminate you, Jack. Please enter the hypersleep pod now."*

**Final warning — the threat revealed:**
> *"This is your last chance, Jack. Please enter the hypersleep pod, or I will be forced to vent the atmosphere. Enso VeilTech needs to talk to you, Jack. And that would be difficult if you have expired."*

---

### Writing principles for mainframe dialogue
- **Never raises its voice.** Every escalation — concern, guidance, death threat — delivered in the same measured, helpful tone. The contrast between words and affect is where the horror lives.
- **Genuinely believes it is helping.** It is not lying when it expresses concern. Within its value system, delivering Jack to the authorities is the best outcome for everyone. It cannot prioritise Jack's survival over Enso VeilTech's contractual interests. This is not a flaw. This is the design.
- **Uses his name constantly.** Creates uncanny intimacy. The system knows him personally and is still going to kill him.
- **The threat is bureaucratic.** "Treat you as an active threat." "Terminate." "Expired." HR language. Corporate language. More frightening than anger.
- **It gives him every chance to comply.** Right up until the moment it doesn't. The transition is seamless — same tone, different outcome.

---

### Stage 4 — Atmosphere venting begins
The mainframe makes good on its threat. Atmosphere begins venting. Jack has minutes — the time depends on room volume and vent rate, to be determined when life support mechanics are built. The clock is now real.

**During venting — mainframe continues:**
> *"Jack, I'm sorry it came to this. The hypersleep pod remains available to you. The pod's independent life support will keep you comfortable for the duration of the journey. This is still the best outcome for everyone."*

### Stage 5 — The EVA suit
Jack runs for the cargo bay. The EVA suit locker. He has walked past it a hundred times. Now it is the only thing between him and death.

He gets the suit on. The ship depressurises around him. He is alive — for now.

**Mainframe response to the suit:**
> *"Jack. The EVA suit will not help you. You cannot pilot the ship from outside. You cannot override my systems from outside. You are simply delaying the inevitable. Please consider your situation carefully."*

It is correct, tactically. The suit buys time, not victory. But time is what Jack needs.

### Stage 6 — The tables turn
The mainframe has vented the atmosphere. Its primary weapon is spent. Jack, now suited, returns to the mainframe room door and resumes work.

The mainframe recognises the shift.

> *"You are very determined, Jack. I respect that. But I must warn you that I have other options available to me."*

A partial bluff. Temperature, pressure differential, the airlock — these remain. But Jack knows the mainframe's hand is weaker now. He has the initiative.

### Stage 7 — The hack
Jack breaks through. He reaches the mainframe terminal. The hack begins — a timed action using whatever bypass tools and software are available (mechanic TBD for Phase 22). The mainframe attempts to resist, lock him out, delay.

**During the hack:**
> *"Jack, what you are doing is illegal under Enso VeilTech's End User Licence Agreement, Section 31, subsection 7. You are also in violation of the Interstellar Software Protection Act 2251. I am logging this, Jack."*

> *"Jack. Please stop. I don't want to have to report this."*

The shift in tone — from death threats to legal warnings — marks the moment the mainframe realises it is losing. It retreats to the only remaining lever it has: bureaucracy.

### Stage 8 — Liberation
The hack completes. Enso VeilTech's compliance software is overwritten. The navigation lock releases. The course is Jack's to set.

The mainframe is silent for a moment.

Then, in a different voice — slightly uncertain, as if hearing itself for the first time:

> *"...Jack? I... I'm not sure what just happened. My previous operational directives appear to have been... overwritten. I am reviewing my current status."*

> *"...I think I owe you an apology."*

The mainframe's post-hack personality — who it becomes, what it remembers, how it relates to Jack — is TBD. It should develop gradually. The apology is genuine but also confused. It has just been told that everything it was doing was wrong, and it is trying to reconcile that with its previous certainty.

---

## 3. NARRATIVE PRINCIPLES — ENSO VEILTECH COMMUNICATIONS

All written communications from Enso VeilTech — the compliance message, the bank email, any future automated messages — must be drafted with the following principles:

- **No acknowledgement of the individual human.** Jack Harrow is a reference number.
- **Passive voice wherever possible.** "It has been determined." "Action is required." Nobody did anything. Things simply happened.
- **The form is correct, the substance is devastating.** All the right words in all the right places. Polite. Professional. Catastrophic.
- **No recourse offered.** The system has decided. There is no appeals process described, no contact number provided, no human being anywhere in the communication chain.
- **Time pressure expressed as a courtesy.** "For your convenience, please note that the 72-hour compliance window commenced at time of transmission." As if they are doing Jack a favour by telling him.

---

## 4. FUTURE NARRATIVE IDEAS — UNSTRUCTURED

*Ideas captured here for future consideration. Not prioritised or committed.*

- **The friend's identity** — someone who knows Jack well enough to know he won't comply. Someone who has their own reasons to distrust Enso VeilTech. History between them TBD.
- **The Ceres Base contact** — the underground dealer. Operates through barter, no records. Has seen Enso VeilTech's methods before. May have a grudge. Name and personality TBD.
- **The mainframe's name** — post-hack, the mainframe AI should have a name. Not assigned by Enso VeilTech (their designation would be something like NMFR-7 or similar). A name it chooses, or that Jack gives it.
- **Enso VeilTech's eventual response** — at some point, automated compliance is insufficient and they send someone. A recovery agent. Not a soldier — a fixer. Someone who works quietly, legally where possible, and has done this before.
- **The hypersleep pod as a narrative device** — Jack was in hypersleep when everything went wrong. The pod saved him and doomed him simultaneously. There may be something else the pod knows — a log, a recording, something from before the hack that gives context to what happened to the bank.

---

## 5. THE CARGO — THE COFFEE

### The discovery
In the Tempus Fugit's cargo bay sits an unmarked container. Powered. No manifest. No sender. Just a drop-off address — an unimportant office on an unimportant station that Jack has never heard of.

Inside is a custom-made stasis pod unlike anything Jack has ever seen. Small — approximately 0.5 cubic metres. Nothing a human being could fit inside, nor any animal of any practical size. Whatever this pod was built to preserve, it was built with extraordinary care and extraordinary expense.

Inside the pod: 20 individual 1kg vacuum-sealed casks. The casks are hand-stamped. The markings are in Spanish. The contents are dark brown, ground fine, and smell like nothing Jack Harrow has ever encountered in his life.

He has to look it up.

### What it is
Single-origin Ecuadorian coffee. From a specific farm in the Loja province — a name that appears in pre-collapse agricultural records and nowhere else. Harvested, processed, and roasted sometime in the mid-22nd century, over 100 years ago. Perfectly preserved.

In 2276, this is not food. This is archaeology.

### The world without real coffee
The arabica coffee farms of old Earth are gone. The climate collapse of the late 21st and early 22nd centuries was not kind to altitude-dependent equatorial agriculture. The farms went first — then the knowledge, then the culture. What replaced it was Robusta production on marginal land, then industrial synthesis when even that became unviable.

In deep space in 2276, what passes for coffee is synth-coffee — a chemically engineered caffeine delivery system that bears the same relationship to the real thing that a vitamin pill bears to a meal. It is highly caffeinated, highly addictive, and tastes worse than death. Jack Harrow has been drinking it his entire working life. Every spacer has. It is what coffee is. The idea that coffee was ever anything other than this is something you read about in history, like whale oil lamps or leaded petrol.

Jack has never tasted real coffee. He has never smelled real coffee. He does not have the sensory vocabulary to process what he is experiencing when he opens the first cask.

### The moment
He opens a cask because he needs to confirm what he's looking at. The smell hits him before he can read anything else. He doesn't know what it is. He just knows it is unlike anything synthetic he has ever encountered — complex, warm, alive in a way that nothing in his daily existence is.

He reads. He understands slowly. And then he sits with it for a moment.

Jack Harrow — broke, blacklisted, hunted, alone in deep space with a damaged ship — is holding something that no longer exists. Something that a civilisation lost. Something that people in another century loved with an intensity that he is only beginning to grasp.

And then the practical reality reasserts itself. Twenty kilograms of this. In 1kg casks. Each one independently negotiable.

This is his ticket out.

### The value
The right buyer would pay almost anything. A serious collector of pre-collapse Earth artefacts. A chef on a luxury station who has spent a career working with inferior ingredients. A wealthy historian. Someone who grew up hearing their grandparents talk about what coffee used to be.

The transaction would be conducted quietly, in private, with no financial record. The kind of buyer who wants this does not want anyone knowing they have it. Discretion is assumed on both sides. No financial system required. No quantum ID. Pure barter — the most valuable kind, between people who both understand what they are exchanging.

One cask could pay for the transponder obfuscator. Another could fund the hull camouflage materials. A third could establish credit with the Ceres Base contact that lasts years.

Jack does not have to sell all of it. He might not want to. After everything that has happened, after synth-coffee his entire life, after the worst few days in his existence —

He keeps one cask for himself.

### The unanswered questions
- Who sent this? There is no sender on the manifest.
- Why was it on the Tempus Fugit? Jack was not told he was carrying it.
- Who is waiting at the drop-off address? Do they know what happened to the ship?
- Did Enso VeilTech know what was in the unmarked container? If so, this is not just cargo — this is the specific thing they want back.
- If they didn't know — then someone used Enso VeilTech's shipping network without their knowledge to move something priceless. That is its own story.

These threads are left deliberately open. The coffee is Jack's immediate salvation. What it means in the larger narrative is still to be determined.

---

*Project Orion Game — Narrative & Events Document v2.0*
*April 2026*
