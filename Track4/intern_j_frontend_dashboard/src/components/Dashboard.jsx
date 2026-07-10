import { useState } from "react";
import ScriptViewer from "./ScriptViewer";
import ResultsPanel from "./ResultsPanel";

export default function Dashboard({ script }) {
  const [activeQuestionId, setActiveQuestionId] = useState(script.questions[0]?.question_id ?? null);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1>Validation Desk</h1>
          <p className="dashboard__subtitle">Script {script.script_id} · Student {script.student_id}</p>
        </div>
        <div className="dashboard__score-summary">
          <span className="dashboard__score-value">{script.total_score}</span>
          <span className="dashboard__score-max">/ {script.total_max_score}</span>
        </div>
      </header>

      <div className="dashboard__split">
        <ScriptViewer script={script} activeQuestionId={activeQuestionId} onSelectQuestion={setActiveQuestionId} />
        <ResultsPanel script={script} activeQuestionId={activeQuestionId} onSelectQuestion={setActiveQuestionId} />
      </div>
    </div>
  );
}
