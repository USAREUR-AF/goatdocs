// TopBar.jsx — 56px top bar. Logo, sector switcher, search, status.

const TopBar = ({ sector, onSearchFocus, onCmdK, status = 'all peers reporting' }) => {
  const [theme, setTheme] = React.useState(
    () => document.documentElement.getAttribute('data-theme') || 'dark'
  );
  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    setTheme(next);
  };

  return (
    <div className="topbar">
      <div className="topbar__brand">
        <img src="../../assets/goat-logo.svg" alt="GOAT-Net" className="topbar__mark" />
        <div className="word">GOAT<i>-</i>Net</div>
      </div>

      <div className="row" style={{display:'flex', alignItems:'center', gap:12, minWidth:0}}>
        <button className="sector" onClick={()=>{}}>
          <window.Icon name="flag" size={12} />
          <span>SECTOR · {sector}</span>
          <span className="chev"><window.Icon name="chev-down" size={10} /></span>
        </button>

        <div className="search" onClick={onSearchFocus}>
          <window.Icon name="search" size={14} color="var(--fg-muted)" />
          <input placeholder="Search peers, publications, fingerprints…" readOnly onFocus={onCmdK}/>
          <span className="kbd"><kbd className="kbd">⌘</kbd> <kbd className="kbd">K</kbd></span>
        </div>
      </div>

      <div className="topbar__right">
        <div className="topbar__status">
          <span className="live-dot"></span>
          <span>{status}</span>
        </div>
        <button
          className="btn btn--sm theme-toggle"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? '☾ DARK' : '☀ LIGHT'}
        </button>
        <button className="btn btn--sm">
          <window.Icon name="plus" size={12} />
          Enroll peer
        </button>
      </div>
    </div>
  );
};

window.TopBar = TopBar;
