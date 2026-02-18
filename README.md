# burnout-buddy

🌙 Burnout Buddy

A structured, adaptive evening companion that helps users transition from work → rest → intentional action.

Burnout Buddy is a React Native application powered by a controlled backend AI planning system. It helps users reduce burnout, avoid doom-scrolling, and build intentional evening habits through structured pre-commitment and gentle accountability.

This is not a generic chat app.
This is a structured behavioral ritual system with a conversational companion layer.

🧠 Core Purpose

Burnout Buddy exists to help users:

Process how they feel after work

Commit to 1–2 intentional evening goals

Take a restorative break

Return to a locked-in plan

Execute with reduced cognitive load

The system combines:

Pre-commitment psychology

Behavioral friction for avoidance

Gentle accountability

Structured AI planning

Conversational emotional support

🗣 Companion Interaction Model (CRITICAL)

The LLM MUST respond conversationally in the UI.

Every time the user:

Clicks a button

Selects a mood

Chooses a rest duration

Speaks via microphone

Types free text

The system must:

Display a cute speech bubble from the buddy

Provide a warm, supportive response

Immediately follow with a structured next step

The user is never left without direction.

🧩 Conversation Pattern

All Companion responses must follow this format:

1️⃣ Speech Bubble Response

The LLM generates a warm, empathetic message:

Example:

“I’m really glad you’re feeling a bit better today. That matters more than you think.”

or

“That sounds heavy. Even noticing it is a step forward.”

Tone guidelines:

Cute but not childish

Supportive, never clinical

Never shaming

Never diagnosing

Calm and grounded

2️⃣ Structured Prompt Under Bubble

Under the same response, the system must ask a follow-up question or provide options.

Example:

“I’d recommend a 30-minute break to help you reset. I challenge you to try that — but you can choose what feels right.”

Then show buttons:

15m

30m

45m

OR include a speech button for custom input.

The structure is always:

[Speech Bubble Response]
        ↓
[Follow-Up Question or Options]

🎙 Voice Input Behavior

The microphone icon may appear on:

Mood screen

Rest selection screen

Companion tab

Plan modification screen

Voice flow:

User audio
    ↓
Transcription
    ↓
Intent classification
    ↓
Speech bubble response
    ↓
Structured next-step options


The LLM response must always:

Interpret emotion

Reflect briefly

Offer one clear recommendation

Provide controlled options

🌙 Evening Flow (With Companion Layer)
Step 1 — Mood Check

User selects mood or speaks.

System response example:

Speech bubble:

“Thanks for telling me. Drained evenings need gentleness.”

Follow-up:

“Would you like to take a short reset before deciding on tonight?”

Buttons:

15m

30m

Skip rest

Step 2 — Rest Recommendation

Speech bubble:

“I’d recommend a 30-minute reset tonight. I think that would really help.”

Follow-up:

“Want to try that?”

Buttons:

15m

30m

45m

User must select one before continuing.

Step 3 — Plan Lock-In (Before Rest)

Speech bubble:

“Before we rest, let’s choose 1–2 things you’d feel proud of tonight.”

Follow-up:

Suggested goals (based on onboarding + today’s input)

Category-based suggestions

Microphone option

Plan is locked once selected.

💤 Step 4 — Rest Mode (Protected Reset Window)

Once the user locks in their evening plan, the system enters Rest Mode.

Rest Mode is a protected decompression period before execution begins.

🌙 Visual State (Evening Tab)

During Rest Mode:

The Evening tab is visually replaced with a single sleeping cloud emoji.

The UI is minimal.

No task planning or editing is visible.

No additional goal prompts appear.

The purpose is to reduce cognitive load and remove decision pressure.

The screen shows:

A countdown timer

Calm supportive messaging

The option to extend once

The option to end rest early

The Evening plan is hidden until Rest Mode completes.

📱 Scroll Behavior During Rest

If the user specified certain scrolling apps during onboarding (e.g., Instagram, TikTok, Twitter), then:

During Rest Mode:

Those apps are temporarily unblocked.

The user is allowed intentional decompression.

The system does not intervene.

This is a permitted decompression window.

🔒 Scroll Blocking After Rest

When Rest Mode ends:

The Evening plan reappears.

Execution Mode begins.

Previously specified scrolling apps are automatically blocked.

Apps remain blocked until sleep time.

This creates a behavioral boundary:

Rest Window → Scroll Allowed
Execution Window → Scroll Blocked


The system enforces this boundary until the user’s configured sleep time.

⏱ Rest Extension Rule

The user may extend rest once via button.

After the first extension:

rest_extended_once = true

If the user attempts to extend again:

They must speak to the Companion and explain why.

The AI classifies the reason:

Genuine fatigue

Overwhelm

Avoidance

Transition difficulty

If healthy rest is appropriate:

Allow additional extension.

If avoidance is detected:

Offer a small transition alternative.

Example speech bubble:

“It sounds like starting feels hard right now. Would a 5-minute warm-up feel easier than extending again?”

Followed by structured options.

🧠 Behavioral Design Principle

Rest Mode exists to:

Reduce emotional overload

Prevent decision fatigue

Create a clean transition

Allow guilt-free decompression

Protect post-rest focus

It is not passive scrolling time.

It is a structured reset window.

🔁 Transition to Execution Mode

When Rest Mode ends:

Evening plan becomes visible again.

Scroll apps are blocked.

Execution Mode begins.

The user completes locked tasks.

No new plan generation occurs unless explicitly requested.

🧠 For AI Contributors

When implementing Rest Mode:

The Evening tab must render only the sleeping cloud state during rest.

Planning UI must be hidden.

Scroll permissions must toggle based on:

rest_active

sleep_time

Only one direct extension is allowed.

Additional extension requires conversational justification.

Scroll blocking must automatically re-enable after rest until sleep time.

Rest Mode is a protected state transition, not just a timer.

🧠 LLM Responsibilities

The LLM is responsible for:

Emotional reflection

Suggesting appropriate rest

Selecting goals from structured inputs

Classifying user intent

Providing gentle accountability

Asking the next guiding question

The LLM is NOT responsible for:

Direct database mutations

Overriding system constraints

Changing sleep time

Creating infinite new tasks

Unbounded freeform conversation

All state changes pass through validation layers.

🏗 Backend Control Layer

Conversation Layer:

Generates speech bubble text

Suggests next step

Decision Layer:

Validates plan constraints

Enforces rest extension rule

Locks plan before rest

Versions plan changes

Enforces sleep time boundary

Conversation is flexible.
System logic is deterministic.

🎯 UX Principles

Every interaction must:

Feel warm

Feel intentional

End with a clear next action

Avoid overwhelming the user

Avoid leaving empty conversational space

The Companion always:

Reflects

Suggests

Asks

Never:

Over-explains

Monologues

Over-analyzes

Diagnoses

🧠 For AI Contributors (Codex Context)

When implementing or modifying LLM calls:

Every user input must trigger a speech bubble response.

The speech bubble must include:

Empathy or reflection

One recommendation (optional)

A follow-up question or options

Structured options must always follow the bubble.

Plan selection must occur before rest begins.

Only one automatic rest extension is allowed.

Further extension requires conversational justification.

LLM output must be schema-validated before affecting system state.

Conversation tone must remain supportive, never clinical.

The Companion is conversational, but the system is structured.

This now clearly defines:

The UI pattern

The emotional tone

The LLM behavior

The structured follow-up requirement

The separation between conversation and control
