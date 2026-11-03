// PeerDetail.jsx — Right-side drawer for a selected peer.

const PeerDetail = ({ peer, publications, onClose }) => {
  if (!peer) return null;

  return (
    <aside className="drawer">
      <div className="drawer__head" style={{position:'relative'}}>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
          <div className="t-label" style={{color: 'var(--fg-faint)'}}>peer · {peer.kind}</div>
        </div>
        <div className="name">{peer.id}</div>
        <div className="sub">
          <window.ChipDot state={peer.state} />
          <span style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--fg-muted)'}}>
            {peer.addr !== '—' ? peer.addr : 'no address assigned'}
          </span>
        </div>
        <button className="drawer__close" onClick={onClose}>
          <window.Icon name="x" size={12}/>
        </button>
      </div>

      <div className="drawer__section">
        <h4>Identity</h4>
        <dl className="kv-tight">
          <dt>fingerprint</dt><dd>{peer.fp}</dd>
          <dt>vendor</dt><dd>{peer.vendor}</dd>
          <dt>mesh</dt><dd>{peer.mesh}</dd>
          <dt>enrolled</dt><dd>{peer.enrolled}</dd>
          <dt>expiry</dt><dd>{peer.expiry}</dd>
        </dl>
      </div>

      <div className="drawer__section">
        <h4>Health</h4>
        <dl className="kv-tight">
          <dt>state</dt><dd>{peer.state}</dd>
          <dt>rtt</dt><dd>{peer.rtt != null ? `${peer.rtt.toFixed(1)} ms` : '—'}</dd>
          <dt>loss</dt><dd>{peer.loss != null ? `${peer.loss.toFixed(1)} %` : '—'}</dd>
          <dt>msg/s</dt><dd style={{color: peer.msgRate > 0 ? 'var(--fg-link)' : 'var(--fg-faint)'}}>{peer.msgRate.toLocaleString()}</dd>
          <dt>last seen</dt><dd>{peer.lastSeen}</dd>
        </dl>
      </div>

      <div className="drawer__section">
        <h4>Publications</h4>
        {publications && publications.length ? (
          <div>
            <div style={{display:'grid', gridTemplateColumns:'1fr 90px 70px', gap:10, paddingBottom:6, fontFamily:'var(--font-mono)', fontSize:10, textTransform:'uppercase', letterSpacing:'0.06em', color:'var(--fg-faint)', borderBottom:'1px solid var(--c-line)'}}>
              <span>topic</span><span>shape</span><span style={{textAlign:'right'}}>hz</span>
            </div>
            {publications.map(pub => (
              <div className="pub-row" key={pub.topic}>
                <span className="topic">{pub.topic}</span>
                <span className="shape">{pub.shape}</span>
                <span className="rate">{pub.rate.toFixed(1)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--fg-faint)'}}>
            No active publications.
          </div>
        )}
      </div>

      <div className="drawer__section" style={{borderBottom:0}}>
        <h4>Actions</h4>
        <div style={{display:'flex', flexWrap:'wrap', gap:6}}>
          <button className="btn btn--sm"><window.Icon name="terminal" size={12}/> Shell into</button>
          <button className="btn btn--sm"><window.Icon name="activity" size={12}/> Trace</button>
          <button className="btn btn--sm btn--danger">Revoke</button>
        </div>
      </div>
    </aside>
  );
};

window.PeerDetail = PeerDetail;
