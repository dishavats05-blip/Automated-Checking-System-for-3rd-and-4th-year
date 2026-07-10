import QuestionCard from "./QuestionCard";

export default function ResultsPanel({ script, activeQuestionId, onSelectQuestion }) {
  return (
    <div className="results-panel">
      <div className="results-panel__toolbar">
        <span className="results-panel__title">AI evaluation</span>
        <span className="results-panel__total">
          {script.total_score} / {script.total_max_score}
        </span>
      </div>

      <div className="results-panel__list">
        {script.questions.map((question) => (
          <QuestionCard
            key={question.question_id}
            script={script}
            question={question}
            isActive={question.question_id === activeQuestionId}
            onSelect={onSelectQuestion}
          />
        ))}
      </div>
    </div>
  );
}
