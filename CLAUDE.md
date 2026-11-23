# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

A single-purpose Streamlit app: "Task Breakdown Agent". A user types a goal, an LLM (via Groq)
returns a structured JSON plan (steps, priorities, effort, tips, challenges), and the UI renders
it with a follow-up "refine" loop. See [README.md](README.md) for setup/usage — don't duplicate
that here.

## Files

- [agent.py](agent.py) — `create_task_breakdown_agent()` is a closure-based agent factory (no
  class). Returns a dict of functions: `chat(message)`, `reset()`, `get_history()`. Conversation
  history is a plain list of `{role, content}` dicts, captured in the closure and mutated in place
  — a turn is only appended to history *after* a successful API response, so a failed call never
  leaves a dangling unanswered user message that would corrupt the next request's context.
  Model: `openai/gpt-oss-120b` via the Groq client (`groq` SDK, OpenAI-compatible chat completions
  API). The Groq call is wrapped in try/except; failures raise `AgentAPIError` (defined here) with
  the original exception chained as `__cause__`. `PLAN_JSON_SCHEMA_DESCRIPTION` is the single
  source of truth for the expected plan JSON shape — interpolated into the system prompt here and
  reused by `app.py`'s per-call prompt strings, so the schema is defined once, not redescribed
  per call site. Typed with standard `typing` hints (this is a deliberate convention — see
  Conventions below).
- [plan_parser.py](plan_parser.py) — pure module, no Streamlit/Groq dependency. `extract_json_block`
  strips markdown fences and regex-extracts the first `{...}` block; `parse_plan_response` adds
  `json.loads` on top. Both raise `PlanParseError` on failure (JSON decode errors are chained via
  `raise ... from e`). This is the single place JSON-extraction logic lives — `app.py` calls
  `parse_plan_response()` rather than re-implementing fence-stripping/brace-extraction itself.
- [app.py](app.py) — Streamlit UI. Keeps the agent instance in `st.session_state.agent` (created
  once per session). Button-driven flow: Generate Plan → `parse_plan_response()` on the model's raw
  text response → render → Refine (sends another `chat()` call, same conversation history, expects
  the same JSON shape back) → re-render. No backend/API layer; Streamlit callbacks call
  `agent.chat()` directly. Exception handling distinguishes `AgentAPIError` (shown as "API error:
  ...") from `PlanParseError` (shown as a parsing-specific message) from any other exception (a
  final generic `except Exception` safety net) — don't collapse these back into one catch-all.
- [tests/](tests/) — pytest suite. `test_plan_parser.py` covers `plan_parser.py`'s pure functions
  directly (fences, prose, malformed/empty input, cause-chaining). `test_agent.py` mocks
  `agent.client.chat.completions.create` via `unittest.mock.patch` and covers history
  accumulation, `reset()`, and the API-failure/no-dangling-history behavior. Run with `pytest -v`
  from repo root — no `conftest.py`/`pytest.ini` needed, default rootdir-based discovery resolves
  imports fine. Deliberately not covered: Streamlit UI interactions (`st.testing.v1.AppTest` was
  considered and consciously skipped — `app.py` has no extracted functions to test in isolation and
  isn't in scope for a UI-coupled test harness unless asked).
- `.env` — holds `GROQ_API_KEY`, loaded via `python-dotenv` in agent.py. Never commit real keys;
  `.env` should stay gitignored.
- `venv/` — local virtualenv, vendored dependency source lives here (e.g. `venv/Lib/site-packages`).
  Treat it as opaque/generated — never read, edit, or "explore" into it when searching the
  codebase; the actual project is just the root-level `.py`/`.md`/`.txt` files and `tests/`.

## State management

Streamlit reruns the whole script top-to-bottom on every interaction, so persistent state
(`agent`, `plan_data`, `status`, `error`) lives in `st.session_state`, initialized once with an
`if "agent" not in st.session_state` guard. "Reset Everything" calls `agent["reset"]()` (clears
LLM conversation history) and also clears the session-state plan/status/error. "Clear All" only
clears UI state, not the agent's conversation history — intentional distinction, not a bug.

## Running / testing

```bash
streamlit run app.py   # run the app
pytest -v               # run the test suite (agent.py + plan_parser.py logic, mocked API)
```
Automated tests cover `agent.py` and `plan_parser.py` logic. `app.py` itself still has no
automated coverage (by design, see [tests/](tests/) above) — to verify a UI change, run the app and
manually exercise: generate a plan, refine it at least once, and hit Reset — these are the three
code paths most likely to regress.

## Conventions

- No classes — the codebase intentionally stays simple/functional (closures over dicts). Match
  that style rather than introducing OOP abstractions.
- Type hints are used in `agent.py` and `plan_parser.py` (pure/non-UI logic) — this is a
  deliberate, scoped convention. `app.py` stays a plain top-to-bottom Streamlit script with no
  extracted functions, so it isn't type-hinted; that's consistent with how Streamlit scripts are
  normally written, not an inconsistency to fix.
- Single model, single provider (Groq). Don't add provider-abstraction layers unless asked.
- No `TypedDict`/`pydantic` validation of the plan JSON schema — considered but intentionally
  skipped as a feature-ish addition beyond current scope. A plain `dict` return type is fine.
