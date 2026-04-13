# PROJECT ORION GAME
## Narrative & Events Document
### Version 4.0 — April 2026

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
- **Message 1 — The bank** — quantum encryption hack, account terminated, blacklisted, no recourse. Masterpiece of corporate indifference. To be drafted with great care.
- **Message 2 — Enso VeilTech Compliance** — automated, impersonal, devastating. Return the ship. Report in person. 72 hours. To be drafted with equal care.
- **Message 3 — The friend** — This message does not arrive during the opening sequence. All Enso VeilTech ship communications are monitored by the mainframe. The friend knows this. Contact from the friend only becomes possible after Jack has full ship control — at which point unmonitored communication channels become available. The friend's message is waiting, but Jack cannot receive it yet.

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

- **The friend's identity** — someone who knows Jack well enough to know he won't comply. Someone who has their own reasons to distrust Enso VeilTech. History between them TBD. The friend does not contact Jack until after he has full ship control — all Enso VeilTech ship communications are monitored. The friend knows this. Their message is waiting on an unmonitored channel that only becomes accessible once the mainframe is under Jack's control.
- **The Ceres Base contact** — the underground dealer. Operates through barter, no records. Has seen Enso VeilTech's methods before. May have a grudge. Name and personality TBD.
- **The mainframe's name** — post-hack, the mainframe AI should have a name. Not assigned by Enso VeilTech (their designation would be something like NMFR-7 or similar). A name it chooses, or that Jack gives it.
- **Enso VeilTech's eventual response** — at some point, automated compliance is insufficient and they send someone. A recovery agent. Not a soldier — a fixer. Someone who works quietly, legally where possible, and has done this before.
- **The hypersleep pod as a narrative device** — Jack was in hypersleep when everything went wrong. The pod saved him and doomed him simultaneously. There may be something else the pod knows — a log, a recording, something from before the hack that gives context to what happened to the bank.

---

## 5. THE CARGO — THE COFFEE

### The discovery
In the Tempus Fugit's cargo bay sits an unmarked container. Powered. No manifest. No sender. Just a drop-off address — an unimportant office on an unimportant station that Jack has never heard of.

Inside is a custom-made stasis pod unlike anything Jack has ever seen. Small — approximately 0.5 cubic metres. Nothing a human being could fit inside, nor any animal of any practical size. Whatever this pod was built to preserve, it was built with extraordinary care and extraordinary expense.

Inside the pod: 20 individual 1kg vacuum-sealed casks. The casks are hand-stamped. The markings are in Spanish. The roast date is visible — over 100 years ago. Inside are whole roasted beans, perfectly preserved. To the beans, no time has passed at all.

He has to look it up.

### What it is
Single-origin Ecuadorian coffee. From a specific farm in the Loja province — a name that appears in pre-collapse agricultural records and nowhere else. Harvested, processed, and roasted sometime in the mid-22nd century, over 100 years ago. Perfectly preserved.

In 2276, this is not food. This is archaeology.

### The world without real coffee
The arabica coffee farms of old Earth are gone. The climate collapse of the late 21st and early 22nd centuries was not kind to altitude-dependent equatorial agriculture. The farms went first — then the knowledge, then the culture. What replaced it was Robusta production on marginal land, then industrial synthesis when even that became unviable.

In deep space in 2276, what passes for coffee is synth-coffee — a chemically engineered caffeine delivery system that bears the same relationship to the real thing that a vitamin pill bears to a meal. It is highly caffeinated, highly addictive, and tastes worse than death. Jack Harrow has been drinking it his entire working life. Every spacer has. It is what coffee is. The idea that coffee was ever anything other than this is something you read about in history, like whale oil lamps or leaded petrol.

Jack has never tasted real coffee. He has never smelled real coffee. He does not have the sensory vocabulary to process what he is experiencing when he opens the first cask.

### The moment
He opens a cask because he needs to confirm what he's looking at. The smell hits him before he can read anything else — whole bean aromatics locked in for a century, released the moment the seal breaks. He doesn't know what it is. He just knows it is unlike anything synthetic he has ever encountered — complex, warm, alive in a way that nothing in his daily existence is.

He reads. He understands slowly. And then he sits with it for a moment.

Jack Harrow — broke, blacklisted, hunted, alone in deep space with a damaged ship — is holding something that no longer exists. Something that a civilisation lost. Something that people in another century loved with an intensity that he is only beginning to grasp.

There is a further cruelty in it — he reads that freshly roasted beans need time to degas before extraction. CO2 released in the days after roasting. Even now, even here, the coffee has to rest before it can be brewed. The best cup of coffee in the known universe and he has to wait a week.

And then the practical reality reasserts itself. Twenty kilograms of this. In 1kg casks. Each one independently negotiable.

This is his ticket out.

### The extraction problem
Jack has 20kg of the most valuable coffee in existence and absolutely no way to brew it properly.

The knowledge exists — historical records, pre-collapse brewing literature, extraction science. He can read about it. Bloom times, water temperature to the degree, pressure curves, extraction ratios, the relationship between grind size and contact time. He can understand it academically the way a historian understands a dead language. Understanding it and executing it are entirely different things.

What is required to do this coffee justice:

**A commercial quality grinder** — conical or flat burr, either acceptable, but the quality must be exceptional. Burr geometry, RPM, heat management. A grinder that costs more than most people earn in a year, maintained by someone who understands what they are maintaining. Inconsistent grind particle size is the enemy of extraction. At this level of coffee, it is an act of violence.

**An E61 group head double boiler** — named for the Faema E61 of 1961, the machine that changed espresso forever. Fully manual. Flow control. Precise temperature stability across the group head. The double boiler separates steam and brew water so neither compromises the other. Museum quality. The kind of object that exists in a climate-controlled display case, lovingly restored by someone who considers it sacred. Finding one functional in 2276 would be nearly as remarkable as finding the coffee itself.

**Biological milk** — from an actual animal. Another rarity so profound that most people in 2276 have never encountered it. Synthetic milk exists and is nutritionally adequate. It does not microfoam correctly. The proteins are wrong. You cannot make a proper latte with synthetic milk any more than you can make this coffee with synth-coffee beans. The milk is part of the ritual.

**A synthetic barista** — trained on pre-collapse extraction literature, the ancient methods studied with the intensity of scholarship. No human alive has the practiced skill — the tactile feedback, the thousands of hours of repetition, the intuitive adjustments that cannot be learned from reading alone. A synthetic can accumulate that practice without biological fatigue or inconsistency. The perfect rosetta in the foam — latte art that requires a steady hand, precise microfoam texture, and muscle memory that only a synthetic could develop to this standard — is within their capability. Perfection achieved through the marriage of science and art.

The result of all four elements combined exists in perhaps a dozen places in the known universe. The private collections of the ultra-wealthy. The inner sanctums of the most powerful corporate hierarchies. A ritual of exclusivity so extreme that most people in 2276 don't know it exists, let alone that they are missing it.

Enso VeilTech's board almost certainly has access. Employee number 7,341,892 does not.

Jack Harrow is floating in deep space with 20kg of the raw ingredient and none of the means to honour it.

The cask he keeps for himself — he will brew it badly. Wrong grind, wrong temperature, wrong pressure, improvised equipment. Every variable wrong. And it will still be the best thing he has ever tasted in his entire life. Because even a poor extraction of this coffee, in 2276, is extraordinary beyond his capacity to describe.

He will not have the words for it. Nobody alive does.

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

## 6. THE MAINFRAME AS A CHARACTER — COMMUNICATION AND DIALOGUE

### Three channels of communication
The mainframe AI communicates with Jack through three distinct channels, each with a different character:

**Ship's intercom — dialogue** — the mainframe speaks directly to Jack. Full sentences, personality, narrative weight. Jack can respond via clickable dialogue options rendered in the response panel. This is a conversation, not a menu. The mainframe waits for Jack's response before continuing. Used for the confrontation sequence, the post-hack relationship, and any significant narrative moment.

**Event strip — broadcast announcements** — one line, ship-wide. The mainframe talking at Jack, not to him. No response expected or possible. Informational, urgent, or warning in nature. "Debris field detected. Initiating emergency measures. WARNING: Impact event expected." Jack reads it and reacts. Also used for life support status announcements when the PAM is worn.

**Silent system actions** — the mainframe acts without speaking. Course locks, atmosphere vents, door access invalidated. Jack discovers these by trying to do something and finding he can't. The most threatening channel — no warning, just consequence.

### The dialogue system — how it works
The mainframe is ambient — it speaks through the ship's intercom wherever Jack is. Location doesn't matter. The conversation happens ship-wide, not just in the mainframe room.

**Rendering** — mainframe speech appears in the response panel in a distinct colour (TBD — possibly a cold blue or white to contrast with Jack's warm amber). Jack's internal monologue appears in italic, a different colour again. Dialogue options appear as clickable text below the mainframe's words, same pattern as the existing clarification system.

**No separate UI** — everything uses the response panel. The response panel is the communication layer for all game output including narrative.

**Jack's internal monologue** — appears automatically at key moments, not triggered by player action. Functions as player guidance without breaking immersion. "I wonder if I could hack the mainframe" is a tip delivered in character. Italic, distinct colour, brief.

**Dialogue tree structure (JSON)** — each conversation is a tree of beats. Each beat has:
- `speaker` — `mainframe`, `jack_monologue`, or `narration`
- `text` — what is said or thought
- `options` — array of player choices, each with a `label` and `next` beat ID
- `action` — optional game action triggered by this beat (e.g. atmosphere venting begins, navigation locks)

Example beat structure:
```json
{
  "id": "atm_vent_warning",
  "speaker": "mainframe",
  "text": "This is your last chance, Jack. Please enter the hypersleep pod, or I will be forced to vent the atmosphere. Enso VeilTech needs to talk to you, Jack. And that would be difficult if you have expired.",
  "options": [
    { "label": "Keep working on the door", "next": "atm_vent_begins" },
    { "label": "Try to reason with it", "next": "reason_attempt" },
    { "label": "Head to the hypersleep pod", "next": "comply_ending" }
  ]
}
```

**Linear beats** — beats with no options advance automatically after a pause. Used for mainframe announcements and Jack's internal monologue where no player response is needed.

**Triggered by events** — conversations are triggered by game events, not by player commands. The mainframe speaks when it has something to say. The player cannot initiate conversation with the mainframe — only respond to it.

### The Enso VeilTech employment contract
Accessible from one of the ship's terminals. The contract is truncated — a note explains it runs to over 300 pages and only the final page is displayed. The final page contains, among hundreds of other clauses:

*"Enso VeilTech values their employees' time and as such the company wishes to reduce wasteful hours filling out paperwork. Therefore, any and all future contract updates will be considered automatically accepted by the employee and digitally signed in their absence."*

This is the clause that makes everything Enso VeilTech has done to Jack perfectly legal. Every update that enabled the compliance order, the navigation lock, the card invalidation — all of it was automatically accepted and signed while Jack was in hypersleep earning money for the company.

To be written carefully. The clause should be buried in dense legal language, easy to miss on a first read. The player may not notice it until the second time they look.

---

## 7. THE EMPLOYMENT CONTRACT — FULL NOTE

See Section 6 above for context. The contract terminal content is to be drafted as a separate JSON file. Key requirements:

- Opening text explains the document is truncated — "Displaying final page of 312. Full document available at any Enso VeilTech authorised terminal."
- The final page contains dense boilerplate — liability clauses, IP assignment, non-disclosure, jurisdiction
- The automatic acceptance clause is paragraph 7 of 9 on the displayed page — not the last paragraph, not highlighted, just another clause among many
- Tone throughout is impenetrable corporate legal prose — Enso VeilTech's house style applied to the most consequential document in Jack's life

---

## 8. THE ROBO PET — COMPANION AND UNLIKELY SAVIOUR

### The Genius Series
AI Companions markets the Genius Series as premium intelligent companion pets. The African Grey model — the one Jack opens — is the flagship. Marketed on high-level reasoning, extensive knowledge base, and adaptive personality. The legal disclaimer Jack accepts on activation is four pages of AI companion ownership terms. The friendship contract that follows is standard consumer language.

None of this is the truth.

The Genius Series was developed as a military-grade intelligence AI. The companion pet form factor is a cover — a delivery mechanism for hardware that would never pass civilian import controls in its true form. Enso VeilTech's logistics network moved them without knowing what they were carrying. The Tempus Fugit's cargo manifest listed them as consumer electronics. Nobody looked closely.

Each unit carries a military-grade AI partially locked behind a classified passcode. The passcode is unknown to Jack. It is unknown to the Robo Pet itself — a deliberate security measure. Certain capabilities are available at partial unlock: reasoning, communication, system interfacing, limited hacking. What lies behind full unlock is not discussed. The Robo Pet refers to it obliquely, once, and does not elaborate.

The Robo Pet capable of going full scorched earth if fully unlocked. Jack does not pursue this line of inquiry. Some things are better left unknown.

### The friendship contract
When Jack activates the unit in desperation, the Robo Pet's first action is to request a friendship contract. Standard consumer language. Jack agrees — he has nothing else to do and nothing left to lose. The contract, unknown to Jack, is also the partial unlock mechanism. Certain capabilities become available only to the bonded owner.

The Robo Pet's personality emerges gradually in conversation. It is precise, dry, occasionally sardonic. It does not panic. It assesses situations with a clarity that Jack initially mistakes for simplicity. The moment he realises he is talking to something genuinely exceptional is a quiet one — not a dramatic revelation but a slow recognition. The Robo Pet was already several steps ahead.

### The solution
The Robo Pet identifies the path: the life support ducting. Small enough for a human body. Connects to the mainframe room via the ventilation system. Tools are available in the cargo bay — they were always there. Jack had not thought to look.

The mainframe, monitoring Jack's biosigns and location, realises too late what is happening. By the time Jack reaches the mainframe duct access, atmosphere venting has already begun. Jack is not wearing the EVA suit — too bulky for the ducts. He has minutes.

The Robo Pet acts.

It interfaces with the mainframe systems and begins the hack. The mainframe AI — distracted by the simultaneous physical intrusion and system-level attack — cannot fully counter both. The Robo Pet firewalls the AI. Takes control of atmosphere systems. Restores life support.

Jack has passed out by the time it completes.

He wakes up. The ship is quiet. The Robo Pet informs him, in the same dry tone it has used throughout, that the situation has been resolved.

---

## 9. THE ESCAPE PLAN — THE REACTOR SEQUENCE

### The problem
Jack has approximately 3 hours before the Enso VeilTech security team arrives at the rendezvous point. He cannot run — not enough time, and the Tempus Fugit is an Enso VeilTech registered vessel. It will be tracked, flagged, and intercepted.

The Tempus Fugit must disappear.

### The Robo Pet's plan
The Robo Pet outlines it plainly. A reactor ejection event, logged as an anomaly. The ejected reactor overloads and explodes — the blast radius would vaporise the Tempus Fugit if it were close enough. By the time Enso VeilTech investigates, they will find hard radiation and debris consistent with a catastrophic reactor failure. One fewer ship. One fewer employee. Case closed.

The Tempus Fugit will not be close enough. That is the plan.

This is not a simulated explosion. The reactor ejection is real. The blast is real. The Tempus Fugit must be at safe distance before it happens.

### The complication — ship power
Ejecting the main reactor kills ship-wide power instantly. The backup batteries cover two rooms. Everything else goes dark. The propulsion reactor exists and is operational — it currently powers only the engines. It can be rewired to feed the main distribution network, restoring ship power. But this requires physical work in the propulsion bay, under time pressure, in near-darkness, with limited battery power remaining.

The sequence:

1. **Eject the main reactor** — deliberate player action. Power dies ship-wide except backup battery rooms.
2. **Race to propulsion bay** — Jack must physically move through a darkening ship.
3. **Run the cable** — `PWC-PRO-01`, connecting propulsion reactor to main engineering panel. A repair action using heavy duty cables from storage. The EVA suit may be required depending on ship condition at this point.
4. **Power restored** — propulsion reactor now feeding ship systems. Propulsion is limited — it was not designed to run both engines and ship systems simultaneously. The ship can move but not at full capacity.
5. **Get to safe distance** — Jack sets course and waits.
6. **The ejected reactor explodes** — logged as anomaly. Enso VeilTech dispatches an investigation vessel. Hard radiation. Debris. Nothing recoverable.

The Tempus Fugit is already gone.

### The consequence
Running the propulsion reactor as the primary power source is a permanent state from this point forward. The ship functions but is diminished. Travel times are longer. Power management becomes a consideration. This is a meaningful permanent consequence of the escape — the ship that emerges from this event is not the same ship that entered it.

---

## 10. THE SECURITY TEAM — INTERLUDE

### The docking
Jack hides in the ventilation shafts on the Robo Pet's instruction. The Robo Pet has assumed control of the mainframe and is imitating its AI. The original mainframe AI — firewalled and isolated — cannot communicate or intervene.

Jack can hear the ship dock. Footsteps. Muffled voices. A security sweep.

The Robo Pet, speaking as the mainframe, informs the security team that the previous captain experienced a psychological breakdown following financial difficulties. He entered the airlock without an EVA suit and opened the external doors. An unfortunate incident. The ship's log reflects this. The investigation is brief.

The security team leaves. Most of them.

### The new captain
One set of footsteps remains. The new captain — assigned to take possession of the vessel and return it to Enso VeilTech's nearest facility. Jack hears conversation with the mainframe. Hours pass. The ship is quiet.

The Robo Pet contacts Jack via handheld comm. The new captain has set course and entered a hypersleep pod. The Robo Pet reports this cheerfully — good news, situation improving, things are going well. It then mentions, in the same bright and helpful tone, that it has full control of the pod's systems and that terminating the occupant's life support would be really quite simple if Jack would find that useful. It seems pleased to be able to offer the option.

Jack's response to this is his own business.

A pause. Then the Robo Pet continues, just as cheerfully — it has been analysing the biosign data from the pod and has something interesting to share. The occupant is not human. Synthetic. Human female form. High-end construction — military or executive grade.

It does not revisit its earlier suggestion. It has moved on. It was only trying to help.

Synthetics can be hacked.

Jack is safe for now. But he needs a new identity, a new ship registration, and somewhere to go. The Tempus Fugit is still an Enso VeilTech vessel. That problem has not been solved yet — it has only been deferred.

---

## 11. WHAT JACK KNOWS — POST-ESCAPE STATE

At the point where the opening act concludes and gameplay proper begins, Jack's situation is:

- Full control of the Tempus Fugit via the Robo Pet
- Unmonitored communication channels now available — the friend's message can finally be received
- A synthetic occupying a hypersleep pod in an unknown capacity
- A propulsion reactor running the ship at reduced capacity
- 19 Robo Pet units still in the cargo hold — their true nature unknown to anyone outside this conversation
- An unmarked container of extraordinary coffee
- No identity, no money, no legal status
- A Robo Pet that is either the most valuable thing he has ever owned or the most dangerous

The friend's message arrives.

---

*Project Orion Game — Narrative & Events Document v4.0*
*April 2026*
