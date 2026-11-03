// Icon.jsx — A tiny set of Lucide-style line icons, inlined.
// Stroke 1.5, sharp caps. Pass size prop or default to 16.

const Icon = ({ name, size = 16, color = 'currentColor', style }) => {
  const props = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: color,
    strokeWidth: 1.5,
    strokeLinecap: 'square',
    strokeLinejoin: 'miter',
    style,
  };
  switch (name) {
    case 'server':
      return (<svg {...props}><rect x="2" y="3" width="20" height="7"/><rect x="2" y="14" width="20" height="7"/><line x1="6" y1="6.5" x2="6.01" y2="6.5"/><line x1="6" y1="17.5" x2="6.01" y2="17.5"/></svg>);
    case 'network':
      return (<svg {...props}><circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><line x1="12" y1="7" x2="5" y2="17"/><line x1="12" y1="7" x2="19" y2="17"/><line x1="7" y1="19" x2="17" y2="19"/></svg>);
    case 'list':
      return (<svg {...props}><line x1="8" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="8" y1="18" x2="20" y2="18"/><line x1="4" y1="6" x2="4.01" y2="6"/><line x1="4" y1="12" x2="4.01" y2="12"/><line x1="4" y1="18" x2="4.01" y2="18"/></svg>);
    case 'key':
      return (<svg {...props}><circle cx="8" cy="14" r="4"/><line x1="11" y1="11" x2="22" y2="2"/><line x1="18" y1="6" x2="20" y2="8"/><line x1="15" y1="9" x2="17" y2="11"/></svg>);
    case 'shield':
      return (<svg {...props}><path d="M12 3l8 3v6c0 4.5-3.5 8-8 9c-4.5-1-8-4.5-8-9V6l8-3z"/></svg>);
    case 'history':
      return (<svg {...props}><polyline points="3 4 3 9 8 9"/><path d="M3.05 13a9 9 0 1 0 2.13-6.36L3 9"/><line x1="12" y1="7" x2="12" y2="12"/><line x1="12" y1="12" x2="16" y2="14"/></svg>);
    case 'search':
      return (<svg {...props}><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16" y2="16"/></svg>);
    case 'x':
      return (<svg {...props}><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>);
    case 'copy':
      return (<svg {...props}><rect x="8" y="8" width="13" height="13"/><path d="M16 8V4H4v13h4"/></svg>);
    case 'chev-down':
      return (<svg {...props}><polyline points="6 9 12 15 18 9"/></svg>);
    case 'chev-right':
      return (<svg {...props}><polyline points="9 6 15 12 9 18"/></svg>);
    case 'plus':
      return (<svg {...props}><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>);
    case 'activity':
      return (<svg {...props}><polyline points="2 12 6 12 9 4 15 20 18 12 22 12"/></svg>);
    case 'terminal':
      return (<svg {...props}><rect x="2" y="4" width="20" height="16"/><polyline points="6 9 9 12 6 15"/><line x1="12" y1="15" x2="17" y2="15"/></svg>);
    case 'globe':
      return (<svg {...props}><circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18"/></svg>);
    case 'flag':
      return (<svg {...props}><line x1="5" y1="22" x2="5" y2="4"/><path d="M5 4h12l-2 4 2 4H5"/></svg>);
    default:
      return null;
  }
};

window.Icon = Icon;
