import { useState } from "react";
import { overrideScore } from "../api/client";

export default function ScoreEditor({ scriptId, questionId, finalScore, maxScore, reviewerId = "prof_001" }) {
  const [value, setValue] = useState(finalScore);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(true);
  const [error, setError] = useState(null);

  async function commit() {
    if (Number(value) === finalScore) return;
    setSaving(true);
    setError(null);
    try {
      await overrideScore(scriptId, questionId, {
        reviewerId,
        correctedScore: Number(value),
        reason: "Manual professor override",
      });
      setSaved(true);
    } catch (err) {
      setError("Couldn't save — try again");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="score-editor">
      <input
        type="number"
        className="score-editor__input"
        value={value}
        min={0}
        max={maxScore}
        step={0.5}
        onChange={(e) => {
          setValue(e.target.value);
          setSaved(false);
        }}
        onBlur={commit}
        aria-label={`Mark for ${questionId}`}
      />
      <span className="score-editor__max">/ {maxScore}</span>
      {saving && <span className="score-editor__status">Saving…</span>}
      {!saving && saved && Number(value) !== finalScore && <span className="score-editor__status">Saved</span>}
      {error && <span className="score-editor__status score-editor__status--error">{error}</span>}
    </div>
  );
}
