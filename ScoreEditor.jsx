const REGION_COLORS = {
  diagram: "var(--region-diagram)",
  code: "var(--region-code)",
  math: "var(--region-math)",
  text: "var(--region-text)",
};

const REGION_LABELS = {
  diagram: "Diagram",
  code: "Code",
  math: "Math",
  text: "Prose",
};

export default function ScriptViewer({ script, activeQuestionId, onSelectQuestion }) {
  return (
    <div className="script-viewer">
      <div className="script-viewer__toolbar">
        <span className="script-viewer__title">Scanned script</span>
        <span className="script-viewer__meta">{script.script_id}</span>
      </div>

      <div className="script-viewer__stage">
        <div
          className="script-viewer__image-frame"
          style={{ aspectRatio: `${script.image_width} / ${script.image_height}` }}
        >
          <img src={script.page_image_url} alt="Scanned answer script" className="script-viewer__image" />
          <svg
            className="script-viewer__overlay"
            viewBox={`0 0 ${script.image_width} ${script.image_height}`}
            preserveAspectRatio="none"
          >
            {script.questions.map((question) =>
              question.bounding_boxes.map((box, i) => {
                const isActive = question.question_id === activeQuestionId;
                const color = REGION_COLORS[box.region_type] ?? "var(--region-text)";
                return (
                  <g key={`${question.question_id}-${i}`}>
                    <rect
                      x={box.x0}
                      y={box.y0}
                      width={box.x1 - box.x0}
                      height={box.y1 - box.y0}
                      fill={isActive ? color : "transparent"}
                      fillOpacity={isActive ? 0.08 : 0}
                      stroke={color}
                      strokeWidth={isActive ? 3 : 1.5}
                      rx={4}
                      className="script-viewer__box"
                      onClick={() => onSelectQuestion(question.question_id)}
                    />
                    <text x={box.x0 + 6} y={box.y0 + 18} fill={color} className="script-viewer__box-label">
                      {question.question_id}
                    </text>
                  </g>
                );
              })
            )}
          </svg>
        </div>
      </div>

      <div className="script-viewer__legend">
        {Object.entries(REGION_LABELS).map(([key, label]) => (
          <span key={key} className="legend-item">
            <span className="legend-swatch" style={{ background: REGION_COLORS[key] }} />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
