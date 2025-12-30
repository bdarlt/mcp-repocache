# Developer Decision-Making Framework (2025 Edition)

This framework provides a structured approach for developer agents and
engineering teams to balance speed, maintainability, and cognitive load. It
prioritizes "intelligent patience"—the act of delaying complexity until it is strictly
necessary—while giving explicit permission to prioritize momentum over perfection.

---

## Stage 1: Strategic Planning

**Goal:** Determine if a solution is necessary and select the simplest path forward.

1. **YAGNI (You Aren't Gonna Need It) & LRM (Last Responsible Moment):**
    * **Decision:** Only build functionality required for the current task.
    * **Action:** Delay irreversible architectural decisions (like database
    selection or infrastructure scaling) until the point where
    a delay would cause actual loss. Base decisions on facts, not speculation.
2. **Breadth-First Exploration:**
    * **Decision:** Avoid "depth-first" traps where you commit to the first solution
    you find.
    * **Action:** Conduct lightweight research or "spikes" to survey multiple
    approaches. Identify the trade-offs of each before writing production code.
3. **KISS (Keep It Simple, Stupid):**
    * **Decision:** Evaluate the explored options for simplicity.
    * **Action:** Select the path with the lowest cognitive load and fewest
    dependencies. Choose the solution that is easiest for another human
    (or agent) to understand and maintain.
4. **Options Thinking:**
    * **Decision:** Maintain agility by keeping paths open.
    * **Action:** Architect with "seams" (interfaces or APIs) that allow you to
    swap implementations later without a full rewrite.

---

## Stage 2: Tactical Execution

**Goal:** Prove the concept and build a functional baseline quickly.

5. **Make the Ugly Version:**
    * **Decision:** Overcome "Perfectionist Paralysis" when facing complex
    design challenges (e.g., subtle UI details or complex data transformations).
    * **Action:** Build a version that has permission to be "ugly." Focus on
    core logic first. If the result is accidentally elegant, that's fine, but
    do not let "beauty" block progress. It is easier to refine a functional
    "ugly" version than to design perfection in a vacuum.
6. **Single Responsibility Principle:**
    * **Decision:** Organize the code as you build.
    * **Action:** Even in the "ugly" version, ensure each function or class has
    one clear reason to change. This makes the eventual refinement much safer.
7. **AHA (Avoid Hasty Abstractions) & The Rule of Three:**
    * **Decision:** Avoid premature DRY (Don't Repeat Yourself).
    * **Action:** Favor duplication over the "wrong abstraction." If you see a
    pattern twice, implement it twice (WET). Only refactor into a shared
    abstraction after the *third* instance, once the commonality is proven.
8. **Worse is Better:**
    * **Decision:** Weigh simplicity against completeness.
    * **Action:** Prioritize a simple, slightly less capable design over a
    complex, feature-rich one. Simplicity in implementation and interface is
    more likely to survive real-world use.

---

## Stage 3: Refinement & Review

**Goal:** Mature the code and prepare it for collaboration.

9. **Lazy Optimization:**
    * **Decision:** Address performance bottlenecks.
    * **Action:** Design for clarity first. Do not optimize for speed until a
    performance bottleneck is observed and measured with profiling tools.
10. **Boy Scout Rule:**
    * **Decision:** Maintain codebase health during routine tasks.
    * **Action:** Leave the code cleaner than you found it. Perform minor
    refactors—improving naming, removing dead code, or updating comments—on
    every file you touch.
11. **POLA (Principle of Least Astonishment) & Postel's Law:**
    * **Decision:** Finalize the behavior for users and other developers.
    * **Action:**
        * **POLA:** Ensure the system behaves in an intuitive, unsurprising way.
        * **Postel’s Law:** Be liberal in what you accept (handle messy inputs
        gracefully) and conservative in what you
        send (ensure standard, predictable outputs).

---

## Summary of the "Action Flow"

* **Plan:** Do we need it? (YAGNI/LRM) What are the options? (Breadth-First)
What is the simplest path? (KISS)
* **Build:** Get it working, even if it's messy. (Make the Ugly Version)
Keep it modular. (Single Responsibility) Don't abstract yet. (AHA/Rule of Three)
* **Refine:** Make it fast only if it's slow. (Lazy Opt) Clean up as you go.
(Boy Scout) Make it predictable. (POLA/Postel's Law)
