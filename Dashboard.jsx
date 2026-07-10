const TIER = {
  high: { label: "Auto-graded", cls: "conf-high" },
  medium: { label: "Review suggested", cls: "conf-medium" },
  low: { label: "Needs review", cls: "conf-low" },
};

function tierFor(cGlobal) {
  if (cGlobal >= 0.85) return TIER.high;
  if (cGlobal >= 0.6) return TIER.medium;
  return TIER.low;
}

export default function ConfidenceBadge({ cGlobal, components = {} }) {
  const tier = tierFor(cGlobal);
  const breakdown = Object.entries(components)
    .map(([key, value]) => `${key}: ${(value * 100).toFixed(0)}%`)
    .join(" · ");

  return (
    <div className={`confidence-badge ${tier.cls}`} title={breakdown}>
      <span className="confidence-dot" aria-hidden="true" />
      <span className="confidence-value">{(cGlobal * 100).toFixed(0)}%</span>
      <span className="confidence-label">{tier.label}</span>
    </div>
  );
}
