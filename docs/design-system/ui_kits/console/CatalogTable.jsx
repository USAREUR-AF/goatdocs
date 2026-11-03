// CatalogTable.jsx — Main view: peers and their publications.

const CatalogTable = ({ peers, selectedId, onSelect, filter, onFilter }) => {
  const filters = [
    { id: 'all',           label: 'All',           match: () => true },
    { id: 'online',        label: 'Online',        match: p => p.state === 'online' },
    { id: 'degraded',      label: 'Degraded',      match: p => p.state === 'degraded' },
    { id: 'offline',       label: 'Offline',       match: p => p.state === 'offline' },
    { id: 'enrolling',     label: 'Enrolling',     match: p => p.state === 'enrolling' },
    { id: 'experimental',  label: 'Experimental',  match: p => p.state === 'experimental' },
  ];
  const active = filters.find(f => f.id === filter) || filters[0];
  const rows = peers.filter(active.match);

  const lastTick = '04:21:18Z';

  return (
    <div className="main">
      <header className="main__header">
        <div className="main__title-row">
          <div className="main__eyebrow">catalog · live</div>
          <div className="main__title" style={{marginLeft: 0}}>Peers and publications</div>
          <div className="main__meta">
            <div><b>{peers.filter(p => p.state === 'online').length}</b> online</div>
            <div><b>{peers.length}</b> enrolled</div>
            <div>tick · <b>{lastTick}</b></div>
          </div>
        </div>
      </header>

      <div className="toolbar">
        {filters.map(f => (
          <button
            key={f.id}
            className={`filterpill ${filter === f.id ? 'is-active' : ''}`}
            onClick={() => onFilter(f.id)}
          >
            {f.label} · {peers.filter(f.match).length}
          </button>
        ))}
        <div style={{flex: 1}}></div>
        <button className="btn btn--ghost btn--sm">
          <window.Icon name="copy" size={12}/> Export
        </button>
      </div>

      <div className="tablewrap">
        <table className="peers">
          <thead>
            <tr>
              <th style={{width: '22%'}}>peer</th>
              <th>kind</th>
              <th>vendor</th>
              <th>state</th>
              <th className="num">rtt</th>
              <th className="num">loss</th>
              <th className="num">pubs</th>
              <th className="num">msg/s</th>
              <th>last seen</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(p => (
              <tr
                key={p.id}
                className={selectedId === p.id ? 'is-selected' : ''}
                onClick={() => onSelect(p.id)}
              >
                <td><span className="peerid">{p.id}</span></td>
                <td>{p.kind}</td>
                <td>{p.vendor}</td>
                <td><window.ChipDot state={p.state}/></td>
                <td className="num">{p.rtt != null ? `${p.rtt} ms` : <span className="dim">—</span>}</td>
                <td className="num">{p.loss != null ? `${p.loss.toFixed(1)} %` : <span className="dim">—</span>}</td>
                <td className="num">{p.pubs}</td>
                <td className="num">{p.msgRate.toLocaleString()}</td>
                <td>{p.lastSeen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

window.CatalogTable = CatalogTable;
