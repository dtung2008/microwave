# Homework design principles

Ported from the optimizations course (`../optimizations/HOMEWORK-PRINCIPLES.md`, itself
ported from robotics) and adapted to this course's format, where **all practice is
homework**: lectures are Hours 1–2 Principles + Hour 3 Tools, so the homework carries the
entire hands-on load. Every homework — and every future Claude session asked to write one —
should follow these principles, or argue explicitly for a change here first.

## The goal (read this before designing anything)

**Students should learn to use a Claude-class AI tool to solve their own RF/microwave
problems.** Not to out-code the AI — nobody will. The lectures give the domain knowledge
that makes steering an AI possible (you cannot evaluate what you do not understand); the
homework practices the steering itself.

Therefore the homework must exercise the parts AI cannot do *for* the student:

- **witnessing** — watching a return-loss curve, a range-Doppler map, or a stability
  circle respond, with something at stake, so that discrepancies itch;
- **question-forming** — turning the itch into a precise question;
- **problem formulation** — deciding what the specification, the topology, and the
  frequency plan are, and what "meets spec" means. In an engineering-design course this
  is the discipline itself;
- **prediction** — committing to an expected outcome before running (which way does the
  match move on the Smith chart? by what factor does detection range shrink when σ drops
  40 dB?);
- **verification** — checking claims against physics (reciprocity, passivity, unitarity,
  closed forms, planted ground truth, the skrf referee), not against vibes;
- **error-catching** — noticing when the tool (or the metric) is lying: a filter that
  "meets spec" only at the plotted points, a link budget that added watts to dBm;
- **reconciliation** — explaining why two numbers that should agree don't.

A student who practices these can delegate every remaining keystroke to an AI and still
be doing engineering. A student who practices only the keystrokes has learned the one
thing the AI already does better.

## The failure mode to design against

The moment a checker defines success, the student's cognition reorganizes into
**make-the-homework-pass mode** and question-forming shuts down — Goodhart's law applied
to curiosity. Symptoms of a homework that induces the mode:

- perfect-specification docstrings (they are Claude prompts; the task becomes
  transcription — by hand or by AI, equally empty);
- an airtight auto-referee that closes the verification loop the student should be
  closing;
- deep dependency chains (module C only testable once A and B work — one bug and the
  week is lost, so the student pastes the whole file into an AI);
- tasks that are trivial (call `skrf.Network(...)` on fully-given data), tedious
  (transcribing a 40-row datasheet table), or mysterious (implement a formula whose
  purpose arrives two lectures later);
- metrics that hide phenomena (grading only the passband ripple silently discards the
  group delay; grading only the detection count discards the false alarms — often the
  interesting physics);
- total honest effort above ~3 hours on a weekly cadence — this does not produce more
  learning, it produces cheating.

## Design rules

1. **One coherent story per homework**, integrating the lectures so far, not a pile of
   disconnected puzzles. (Lecture 1's reference story: *can this radar see the drone?* —
   build a link-budget engine, extend it to the monostatic radar equation, and find out
   which aircraft a given radar can and cannot detect.)
2. **The current lecture's core routine is the meat.** One module the student must own
   deeply enough to *reason about without running*. Everything else is a light refresher
   or provided.
3. **Modules are independently checkable.** The harness feeds each module a known-good
   reference input, so a broken module 1 never cascades into module 2. Every
   accomplishment counts on its own.
4. **Provide tool-like calls for all non-core plumbing** — data loading, reference
   generators, sweep drivers, plotting. Ideally each main concept is one named function
   call (`db`, `friis`, `radar_range`, `smith`, `cascade`, `range_doppler`, `show`), so
   students think in the course's nouns at the abstraction level of the ideas, not the
   syntax.
5. **Prediction before run.** Attach questions that must be answered before executing,
   then verified against the student's own numbers ("σ drops 40 dB from airliner to
   drone — detection range shrinks by what factor, and why not 10⁴?"). This is the
   witnessed-experience engine, and it is cheap to grade.
6. **Leave the solution path underspecified.** State the goal and the contract; do not
   write the pseudo-code. Deciding *how* — including how to direct an AI to help — is
   the exercise. (Clear goal, open path: the opposite of a perfect docstring.)
7. **Assume AI use; never police it.** Design tasks whose value survives full AI
   assistance. If a task is destroyed by AI access, the task was transcription.
8. **Respect the time budget:** ≤ 3 hours including the understanding, every week. Cut
   scope, not depth.
9. **Code style serves legibility of ideas:** small modular functions, no global-soup,
   names that match the lecture vocabulary. A reader should locate each lecture concept
   in the code by name.

## This course's extra lever: physics can certify

Microwave engineering gives homework a verification tool the optimization course got from
duality: **physics invariants and planted ground truth.** A lossless network's S-matrix
must be unitary; any passive network satisfies I − SᴴS ⪰ 0 and reciprocity S = Sᵀ; a
synthetic radar scene has an exact beat frequency f_b = 2Rα/c and Doppler f_d = 2v/λ *by
construction*; a Chebyshev filter has a closed-form table; energy is conserved through an
FFT (Parseval). These let the *student* close the verification loop with physics instead
of trusting a checker. Prefer designs where the student certifies their own answer
(lecture 4 builds the passivity/reciprocity checks and reuses them all course; the radar
lectures grade against scenes whose truth is planted). A planted wrong "solution" the
student must catch is worth more than ten PASS lines. Real vendor Touchstone files add a
second flavor: **measured reality referees the ideal model** — the interesting question is
never "does it match" but "where does it stop matching, and why."

## Grading

- **A computer referee is a tool, not the definition of success.** `--check` prints
  measured facts (|Γ| at f₀, worst in-band return loss, unitarity residual, error vs the
  skrf referee, detection-range error vs closed form) — an instrument the student reads,
  not a gate the student games.
- **TA/human checking is fine and often better** — this is not a programming class.
  Prediction answers, reconciliation explanations, and "what did you ask the AI and how
  did you verify it" are read by a human.
- Never contort a task into machine-checkable shape if that contortion confuses the
  student or lets them route around the core exercise.
- A good end-of-homework test: *can the student say in one sentence what they learned?*
  If the honest answer is "some of here, some of there," the homework failed regardless
  of its pass rate.

## Working with Claude on homework (for future sessions)

- The student's role is to specify, predict, verify, and question; Claude's role is to
  deliver code precisely from what the student says. Design the modules so that this
  division is natural — interfaces a student can state in one sentence.
- Claude sessions designing homework should resist their own strengths: do not
  demonstrate maximal rigor by writing airtight specs and referees — that rigor belongs
  in instructor-side verification (VERIFY.md), not in the student-facing task.
- When in doubt, re-read the failure-mode list and ask: does this design make a student
  watch the physics, or watch the checker?
