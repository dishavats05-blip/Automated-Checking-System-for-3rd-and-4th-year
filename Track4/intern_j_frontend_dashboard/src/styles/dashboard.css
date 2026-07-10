/* ---------- Shell ---------- */
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 18px 28px;
  background: var(--ink);
  color: #fff;
  border-bottom: 1px solid var(--ink-soft);
}

.dashboard__header h1 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 20px;
  margin: 0;
  letter-spacing: 0.01em;
}

.dashboard__subtitle {
  margin: 2px 0 0;
  font-size: 12.5px;
  color: #aab1c2;
}

.dashboard__score-summary {
  font-family: var(--font-mono);
}

.dashboard__score-value {
  font-size: 28px;
  font-weight: 500;
}

.dashboard__score-max {
  font-size: 15px;
  color: #aab1c2;
}

.dashboard__split {
  flex: 1;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  min-height: 0;
}

@media (max-width: 900px) {
  .dashboard__split {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
}

/* ---------- Left: script viewer ---------- */
.script-viewer {
  display: flex;
  flex-direction: column;
  min-height: 0;
  border-right: 1px solid var(--line);
  background: var(--ink);
}

.script-viewer__toolbar {
  display: flex;
  justify-content: space-between;
  padding: 12px 20px;
  color: #cfd4e0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.script-viewer__stage {
  flex: 1;
  overflow: auto;
  display: flex;
  justify-content: center;
  padding: 16px 24px 8px;
}

.script-viewer__image-frame {
  position: relative;
  width: 100%;
  max-width: 720px;
  height: fit-content;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  border-radius: 2px;
}

.script-viewer__image {
  width: 100%;
  display: block;
  border-radius: 2px;
}

.script-viewer__overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.script-viewer__box {
  cursor: pointer;
  transition: fill-opacity 0.15s ease, stroke-width 0.15s ease;
}

.script-viewer__box-label {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 500;
}

.script-viewer__legend {
  display: flex;
  gap: 18px;
  padding: 12px 24px 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #cfd4e0;
}

.legend-swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

/* ---------- Right: results panel ---------- */
.results-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--paper);
}

.results-panel__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}

.results-panel__title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-weight: 600;
}

.results-panel__total {
  font-family: var(--font-mono);
  font-size: 15px;
  color: var(--accent);
}

.results-panel__list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ---------- Question card ---------- */
.question-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  padding: 16px 18px;
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.question-card--active {
  border-color: var(--accent);
}

.question-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.question-card__id {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 16px;
  margin-right: 8px;
}

.question-card__type {
  display: inline-block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  background: var(--line-soft);
  padding: 2px 7px;
  border-radius: 999px;
  margin-right: 6px;
}

.question-card__co {
  font-size: 11px;
  color: var(--text-muted);
}

.question-card__flag {
  margin: 10px 0 0;
  font-size: 12.5px;
  color: var(--conf-medium);
  background: var(--conf-medium-bg);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}

.question-card__section {
  margin-top: 12px;
}

.question-card__section h4 {
  margin: 0 0 6px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.question-card__structure {
  font-family: var(--font-mono);
  font-size: 11.5px;
  background: var(--ink);
  color: #d7dbe6;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 0;
  max-height: 160px;
}

.question-card__feedback {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 14px;
  color: var(--text);
  margin: 0;
  line-height: 1.5;
}

.question-card__errors {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12.5px;
  color: var(--conf-low);
}

.question-card__footer {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--line-soft);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-card__programmatic {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}

/* ---------- Confidence badge ---------- */
.confidence-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 600;
  white-space: nowrap;
}

.confidence-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.confidence-value {
  font-family: var(--font-mono);
}

.conf-high {
  background: var(--conf-high-bg);
  color: var(--conf-high);
}
.conf-high .confidence-dot {
  background: var(--conf-high);
}

.conf-medium {
  background: var(--conf-medium-bg);
  color: var(--conf-medium);
}
.conf-medium .confidence-dot {
  background: var(--conf-medium);
}

.conf-low {
  background: var(--conf-low-bg);
  color: var(--conf-low);
}
.conf-low .confidence-dot {
  background: var(--conf-low);
}

/* ---------- Score editor ---------- */
.score-editor {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-editor__input {
  width: 56px;
  font-family: var(--font-mono);
  font-size: 14px;
  padding: 4px 6px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  text-align: right;
}

.score-editor__max {
  font-family: var(--font-mono);
  color: var(--text-muted);
  font-size: 13px;
}

.score-editor__status {
  font-size: 11px;
  color: var(--text-muted);
}

.score-editor__status--error {
  color: var(--conf-low);
}
