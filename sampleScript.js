import ConfidenceBadge from "./ConfidenceBadge";
import ScoreEditor from "./ScoreEditor";

export default function QuestionCard({ script, question, isActive, onSelect }) {
  return (
    <article
      className={`question-card ${isActive ? "question-card--active" : ""}`}
      onClick={() => onSelect(question.question_id)}
    >
      <header className="question-card__header">
        <div>
          <span className="question-card__id">{question.question_id}</span>
          <span className="question-card__type">{question.answer_type}</span>
          <span className="question-card__co">{question.course_outcome}</span>
        </div>
        <ConfidenceBadge cGlobal={question.c_global} components={question.confidence_components} />
      </header>

      {question.human_review_required && (
        <p className="question-card__flag">⚑ {question.review_reason}</p>
      )}

      <section className="question-card__section">
        <h4>Extracted structure</h4>
        <pre className="question-card__structure">{JSON.stringify(question.structural_payload, null, 2)}</pre>
      </section>

      <section className="question-card__section">
        <h4>LLM justification</h4>
        <p className="question-card__feedback">{question.feedback}</p>
        {question.detected_errors.length > 0 && (
          <ul className="question-card__errors">
            {question.detected_errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        )}
      </section>

      <footer className="question-card__footer">
        <span className="question-card__programmatic">
          Programmatic: {question.programmatic_score}/{question.max_score}
        </span>
        <ScoreEditor
          scriptId={script.script_id}
          questionId={question.question_id}
          finalScore={question.final_score}
          maxScore={question.max_score}
        />
      </footer>
    </article>
  );
}
