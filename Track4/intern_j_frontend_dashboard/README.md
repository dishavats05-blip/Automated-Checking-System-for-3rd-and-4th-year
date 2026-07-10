# Intern J - Professor Validation Dashboard

React + Vite split-screen dashboard: left panel is the scanned script with
color-coded bounding boxes over each detected region (diagram / code /
math / prose); right panel lists the AI's extracted structure, marks, and
LLM justification per question, with an editable mark field.

## Design

- **Palette:** ink navy (`#171b23`) chrome around a neutral paper
  background (`#eef1f4`); confidence states use muted forest-green /
  ochre / brick-red rather than stoplight neon, since this is a grading
  tool a professor stares at for an hour, not a marketing page.
- **Type:** Source Serif 4 for headings/question IDs/LLM feedback (gives
  the "reading a graded exam" register), Inter for UI chrome, JetBrains
  Mono for scores, confidence percentages, and the raw extracted-structure
  JSON.
- **Signature interaction:** clicking a bounding box on the script *or*
  its matching card on the right both set the same `activeQuestionId`
  state — the box outline thickens and its card gets an accent border.
  That link between "what the AI saw" and "what the AI concluded" is the
  actual point of the tool, so it's the one thing given visual weight;
  everything else is kept quiet.

## Setup

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173`. `/api/*` requests are proxied to
`http://localhost:8001` (Intern I's backend) — see `vite.config.js`.

Currently renders `src/mock/sampleScript.js` (and a generated placeholder
image at `public/sample-script.jpg`) so the UI is developable without a
live pipeline. Swap it for a real fetch once results are available — see
the `TODO` in `src/App.jsx`.

## Structure

```
src/
  api/client.js          fetch wrapper: upload, poll task, PATCH override
  components/
    Dashboard.jsx         top-level split-screen layout + shared active-question state
    ScriptViewer.jsx       left panel: image + SVG bounding-box overlay
    ResultsPanel.jsx       right panel: scrollable question card list
    QuestionCard.jsx       one question: structure / feedback / score editor
    ScoreEditor.jsx         editable mark, PATCHes on blur
    ConfidenceBadge.jsx     C_global pill with a hover breakdown by stage
  mock/sampleScript.js     matches Track4/intern_i_backend_engine's ScriptResultResponse shape
  styles/tokens.css        design tokens (color / type / radius)
  styles/dashboard.css     layout + component styles
```

## Wiring in the live backend

1. `POST /api/upload` a file → get `{ task_id }`.
2. Poll `GET /api/tasks/{task_id}` until `state` is `DONE` or `NEEDS_REVIEW`.
3. `GET /api/results/{task_id}` → feed straight into `<Dashboard script={...} />`.
4. `ScoreEditor` already calls `PATCH /api/scripts/{script_id}/questions/{question_id}/score`
   on blur — no changes needed there once real `script_id`s flow through.
