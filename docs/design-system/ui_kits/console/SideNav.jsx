// SideNav.jsx — Left rail.

const SideNav = ({ view, onChange, counts }) => {
  const link = (id, icon, label, count) => (
    <button
      className={`navlink ${view === id ? 'is-active' : ''}`}
      onClick={() => onChange(id)}
    >
      <window.Icon name={icon} size={14} />
      <span>{label}</span>
      {count != null && <span className="count">{count}</span>}
    </button>
  );

  return (
    <nav className="sidenav">
      <div className="sidenav__group">Mesh</div>
      {link('catalog',     'list',     'Catalog',     counts.peers)}
      {link('topology',    'network',  'Topology')}
      {link('publications','activity', 'Publications', counts.pubs)}

      <div className="sidenav__group">Trust</div>
      {link('enrollment',  'key',      'Enrollment',  counts.enrolling)}
      {link('policy',      'shield',   'Policy')}

      <div className="sidenav__group">Forensics</div>
      {link('audit',       'history',  'Audit log')}
      {link('shell',       'terminal', 'Shell')}
    </nav>
  );
};

window.SideNav = SideNav;
