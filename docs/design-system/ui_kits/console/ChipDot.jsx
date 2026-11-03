// ChipDot.jsx — Status chip with leading dot.
// state: online | degraded | offline | enrolling | experimental | unknown

const ChipDot = ({ state, label }) => {
  const variants = {
    online:       { cls: 'chip--ok',    text: label || 'online',       live: true },
    degraded:     { cls: 'chip--warn',  text: label || 'degraded',     live: false },
    offline:      { cls: 'chip--err',   text: label || 'offline',      live: false },
    enrolling:    { cls: 'chip--info',  text: label || 'enrolling',    live: false },
    experimental: { cls: 'chip--exp',   text: label || 'experimental', live: false },
    unknown:      { cls: 'chip--muted', text: label || 'unknown',      live: false },
  };
  const v = variants[state] || variants.unknown;
  return (
    <span className={`chip ${v.cls}`}>
      <span className="chip__dot" style={v.live ? { boxShadow: 'var(--glow-text)' } : undefined}></span>
      {v.text}
    </span>
  );
};

window.ChipDot = ChipDot;
