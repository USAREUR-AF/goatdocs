"""Scene: an invitation to security professionals. The route and the commitments are those of the
public security policy (goatcore SECURITY.md, read 28 Nov 2026): private reporting through the
repository's security advisories; acknowledgement in 3 working days; triage in 7 working days;
credit in the public advisory unless the reporter prefers otherwise."""
from _kit import mark as _mark

ALT = ""
REPORT_URL = "https://github.com/USAREUR-AF/goatcore/security/advisories/new"
POLICY_URL = "https://github.com/USAREUR-AF/goatcore/security/policy"


def figure_wide():
    return ""


def figure_narrow():
    return ""


def mark():
    """A page with a grade on it, and a line left for the reader to write on."""
    return _mark("grade", "A page with the letter A on it and an empty line beneath.",
                 '<path d="M20 8H60L76 24V88H20Z" class="mkf"/>'
                 '<path d="M60 8V24H76" class="mk mkt"/>'
                 '<path d="M34 62L48 30L62 62M39 51H57" class="mka"/>'
                 '<path d="M32 76H64" class="mk mkd mkt"/>')


def html():
    return f'''<section class="band grade" id="grade">
  <div class="wrap">
    <div class="mk-anchor" aria-hidden="true">{mark()}</div>
    <h2>Grade our work</h2>
    <p class="known"><i>Known as: coordinated vulnerability disclosure</i></p>
    <p class="lead">If you work in security, read the design and try to break the argument. Everything on this page links to the document or the code behind it. If something is missing, weak or wrong, tell us privately through the security reporting process, and we will answer. If this does not earn an A from you, give us the homework.</p>
    <ul>
      <li><b>How:</b> use the private report form of the repository. A report is visible only to the maintainers and to you. The <a href="{POLICY_URL}">security policy</a> states what happens next: an acknowledgement within 3 working days, and triage within 7.</li>
      <li><b>Most useful:</b> a gap in the design, a claim on this page that the code does not support, or a path we did not consider.</li>
      <li><b>No exploit is needed.</b> A report about a claim on this page is welcome as it is.</li>
    </ul>
    <p class="actions"><a class="btn primary" href="{REPORT_URL}">Report privately</a></p>
  </div>
</section>'''
