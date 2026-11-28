#!/usr/bin/env python3
"""Write docs/goat/sec4laymen/index.html: the security page for readers with no technical background.

  python3 -I docs/goat/sec4laymen/build.py           # write index.html
  python3 -I docs/goat/sec4laymen/build.py --check   # fail if index.html is not current

The page is one self-contained file: its text is in this script, its drawings are fixed-layout SVG
written by figures.py beside it, and its two measured times are computed from the security page's
run record (../security/run.json), so the two pages cannot disagree. Standard library only.
"""
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "index.html"
RUN = HERE.parent / "security" / "run.json"


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dur(s):
    m, sec = divmod(int(s), 60)
    return f"{m} minutes" if sec == 0 else f"{m} minutes {sec} seconds"


def measures():
    d = json.loads(RUN.read_text())
    total = sum(x["seconds"] for s in d["stages"] for x in s["steps"]) + d["between_steps_s"]
    return {"build": dur(total), "build-min": str(total // 60), "down": dur(d["teardown"]["seconds"]),
            "req-site": str(d["requirement"]["first_site_s"] // 60)}


def m(key, M):
    return f'<span data-measure="{key}">{M[key]}</span>'


CSS = """
/* Layout: a letter on the kitchen table. Warm paper, dark ink, one calm teal for what is ours.
   System fonts only; light and dark through prefers-color-scheme. */
:root {
  --paper: #f6f3ec; --panel: #fffdf8; --ink: #22303a; --quiet: #55626b; --rule: #ddd6c8; --line: #8b959c;
  --accent: #1c6c76; --accent-soft: #d6eae8; --on-accent: #ffffff; --soft: #ece7dc;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
  --serif: Georgia, "Iowan Old Style", "Times New Roman", serif;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #151b1f; --panel: #1c2429; --ink: #ebe8e0; --quiet: #a6b0b6; --rule: #2e3940; --line: #7f8b92;
    --accent: #74c5cb; --accent-soft: #18333a; --on-accent: #0c1518; --soft: #232c32;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { margin: 0; background: var(--paper); color: var(--ink); font: 18px/1.62 var(--sans); }
a { color: var(--accent); text-underline-offset: 3px; }
.top { border-bottom: 1px solid var(--rule); font-size: 15px; }
.top .wrap { display: flex; justify-content: space-between; gap: 16px; padding-top: 12px; padding-bottom: 12px; }
.top a { text-decoration: none; }
.wrap { max-width: 720px; margin: 0 auto; padding: 0 20px; }
.hero { padding: 40px 0 28px; }
.kicker { font-size: 14px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin: 0 0 10px; }
h1 { font: 700 34px/1.18 var(--serif); margin: 0 0 16px; letter-spacing: -.01em; }
.lede { font-size: 20px; line-height: 1.5; color: var(--quiet); margin: 0 0 20px; }
.btns { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 8px; }
.btn { display: inline-block; padding: 11px 18px; border-radius: 999px; border: 1.5px solid var(--accent); text-decoration: none; font-weight: 600; font-size: 16px; }
.btn.fill { background: var(--accent); color: var(--on-accent); }
figure { margin: 22px 0 6px; }
figure svg { display: block; width: 100%; height: auto; background: var(--panel); border: 1px solid var(--rule); border-radius: 18px; }
figcaption { font-size: 15px; color: var(--quiet); margin-top: 8px; }
section { padding: 34px 0 10px; border-top: 1px solid var(--rule); }
.num { font: 700 14px/1 var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin: 0 0 8px; }
h2 { font: 700 27px/1.22 var(--serif); margin: 0 0 12px; letter-spacing: -.005em; }
p { margin: 0 0 16px; }
dfn { font-style: normal; font-weight: 700; background: linear-gradient(transparent 62%, var(--accent-soft) 62%); }
.short { background: var(--soft); border-radius: 14px; padding: 14px 18px; margin: 6px 0 20px; }
.short b { display: block; font-size: 13px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-bottom: 2px; }
.short p { margin: 0; }
.state { font-size: 16px; color: var(--quiet); border-left: 3px solid var(--accent); padding: 2px 0 2px 14px; margin: 0 0 18px; }
.nums { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 4px 0 18px; }
.nums div { background: var(--panel); border: 1px solid var(--rule); border-radius: 14px; padding: 14px 16px; }
.nums b { display: block; font: 700 22px/1.2 var(--serif); color: var(--accent); }
.nums span.l { display: block; font-size: 15px; color: var(--quiet); margin-top: 4px; }
dl.words { margin: 0; }
dl.words dt { font-weight: 700; margin-top: 14px; }
dl.words dd { margin: 2px 0 0; color: var(--quiet); }
footer { border-top: 1px solid var(--rule); margin-top: 30px; padding: 22px 0 40px; font-size: 15px; color: var(--quiet); }
footer a { margin-right: 16px; }
.svg-t { font-family: var(--sans); fill: var(--ink); }
.svg-q { font-family: var(--sans); fill: var(--quiet); }
@media (min-width: 760px) {
  body { font-size: 19px; }
  h1 { font-size: 44px; }
  h2 { font-size: 31px; }
  .hero { padding-top: 56px; }
}
@media (max-width: 400px) { .nums { grid-template-columns: 1fr; } }
"""


def section(sid, num, title, fig, alt_caption, body, short):
    cap = f"<figcaption>{alt_caption}</figcaption>" if alt_caption else ""
    return f"""
<section id="{sid}">
  <div class="wrap">
    <p class="num">{num}</p>
    <h2>{title}</h2>
    <figure>{fig}{cap}</figure>
{body}
    <div class="short"><b>In one sentence</b><p>{short}</p></div>
  </div>
</section>"""


def render():
    F = load("figures")
    M = measures()
    P = lambda *xs: "\n".join(f"    <p>{x}</p>" for x in xs)
    S = lambda x: f'    <p class="state">{x}</p>'
    parts = []

    parts.append(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sec4laymen: our security work, in plain words</title>
<meta name="description" content="What the goat team builds and why it matters, explained with no technical background needed: a private network that a group can set up itself, keep hidden, and rebuild from a clean start.">
<style>{CSS}</style>
</head>
<body>
<!-- Written by docs/goat/sec4laymen/build.py from its own text, figures.py and ../security/run.json; edit those, then run the script. -->
<div class="top"><div class="wrap"><a href="../">&larr; All goat pages</a><a href="../security/">The technical version</a></div></div>
<header class="hero">
  <div class="wrap">
    <p class="kicker">sec4laymen &middot; our work, in plain words</p>
    <h1>We build a private way for a group's computers to talk to each other.</h1>
    <p class="lede">The group can set it up itself, keep it hidden from strangers, and set it up again from a clean start with less than an hour of machine work.</p>
    <div class="btns"><a class="btn fill" href="#why">Start reading</a><a class="btn" href="#words">Words used here</a></div>
    <figure>{F.hero()}</figure>
  </div>
</header>""")

    parts.append(section("why", "Why it matters", "Some people cannot afford to lose touch", F.why(), "",
        P("Think of the people whose work depends on staying in touch with each other: a rescue team, a hospital, a ship's crew, people working far from home. They share maps, positions, warnings and orders through computers.",
          "Two things can go badly wrong. A stranger can break in, and then read what is sent, change it, or shut things off. Or the connection to the outside world can be cut, and everything that depended on it stops.",
          "Most designs guard against the first problem with a strong front gate, and have no answer to the second. Our team's work is a different design. It is hard to find, it checks everyone every time, it keeps what is sent locked, it is designed to keep working when it is cut off, and if something does go wrong it can be wiped and set up again quickly."),
        "We make it hard to break in, and quick to start again clean if someone does."))

    parts.append(section("basics", "First, five ordinary words", "Computers send each other letters", F.basics(), "",
        P("A <dfn>program</dfn> is a set of instructions that a computer follows, the way a cook follows a recipe.",
          "A <dfn>message</dfn> is anything one computer sends to another: a line of text, a position on a map, a photograph, a reading from an instrument. You can think of each message as a letter.",
          "A <dfn>computer network</dfn> is a group of computers that can send messages to each other, the way houses on connected streets can send each other letters.",
          "The <dfn>internet</dfn> is the largest network there is: the public streets that almost every computer in the world shares.",
          "A <dfn>server</dfn> is a computer whose job is to run programs for many other computers. It is to a network what a post office is to a town."),
        "A network is streets, computers are houses, and messages are letters."))

    parts.append(section("locks", "Locks and keys", "Locking a message, and the difference between unlocking and translating", F.locks(), "",
        P("<dfn>Encryption</dfn> is scrambling a message so that it looks like nonsense to everyone except the person meant to read it. It is the same idea as putting a letter in a locked box. On this page, when we say a message is <dfn>sealed</dfn>, we mean it is encrypted.",
          "A <dfn>key</dfn> is what opens the box. On a computer a key is a very long secret number. Whoever has the right key can open the box. Nobody else can.",
          "To <dfn>decrypt</dfn> a message is to unlock it with the key and read it.",
          "To <dfn>decode</dfn> a message is something different, and people often confuse the two. Decoding is translating. Different machines write the same information in different ways, like people writing in different languages, and decoding turns one machine's way of writing into another's. No secret is involved. Anyone who knows the language can decode. Only the holder of the key can decrypt."),
        "Decrypting is unlocking with a secret key; decoding is translating, and needs no secret."))

    parts.append(section("route", "A private route", "Our network is a sealed route laid across the public roads", F.route(), "",
        P("Messages have to travel over something. A <dfn>link</dfn>, also called a <dfn>transport</dfn>, is whatever carries them: a cable in the ground, a mobile phone network, a satellite.",
          "The <dfn>underlay</dfn> is the name for those shared links taken together. It is the public road system that everyone uses.",
          "An <dfn>overlay</dfn> is a private route laid across those public roads. The letters still travel on the same roads as everyone else's, but each one is locked, and only the houses that belong to the route can open them. The network our team builds is an overlay, and it can ride on any link that is available."),
        "We do not build new roads; we build a private, locked route across the roads that already exist."))

    parts.append(section("hidden", "Hidden", "A house with no door on the street", F.hidden(), "",
        P("Most of what you use on the internet, such as a shop's website, has a public address. It is like a shop with a door on the street: anyone can find it, walk up and try the handle.",
          "The computers in our network have no door on the street. If a stranger sends one of them a message, it does not reply at all, not even to say no. A stranger who goes looking finds nothing that answers.",
          "There is one exception, and it is on purpose. A new computer needs some way to join, so the network has a single public name that is used only for joining. The newcomer must present a key that works one time. After that it talks to the other computers directly, and the name is not used again."),
        "A stranger who knocks gets no answer, because there is no door to knock on."))

    parts.append(section("own", "Your own computers", "Everything that matters stays on computers you own", F.own(), "",
        P("A <dfn>site</dfn> is one place and the group of computers there: an office, a vehicle, a camp.",
          "In our design, each site runs everything it needs on its own computers, which its owner holds and controls. The information stays there.",
          "Sometimes two computers cannot reach each other directly. Then a <dfn>relay</dfn> helps. A relay is a rented computer somewhere on the internet that passes sealed letters along. It is like a courier who carries a locked box from one house to another. The courier has no key, so the courier cannot read what is inside or change it, and any courier can be replaced by another."),
        "Rented computers only carry locked boxes; the keys and the contents never leave your own machines."))

    parts.append(section("trust", "Checking everyone, every time", "No inside and no outside", F.trust(), "",
        P("Many networks work like a building with one guard at the front door. Once you are past the guard, every room is open to you. If a stranger gets past the guard once, the stranger can go everywhere.",
          "Ours works like a building where every single door checks your badge, every time. Being inside the building earns you nothing.",
          "The badge is called an <dfn>identity</dfn>: proof of exactly who or what is asking. A person has one. So does each computer, and so does each program.",
          "This approach has a name, <dfn>zero trust</dfn>. It means that nothing is trusted because of where it is. Each time one thing wants to talk to another, four questions are asked. Who is asking? Is there a written rule that allows these two to talk? Is this particular action allowed? Is the badge still good, or has it been taken away? If any answer is no, nothing happens."),
        "There is no trusted inside to sneak into, because every door checks every visitor."))

    parts.append(section("layers", "More than one lock", "A message is locked for the journey, and can be locked again for its readers", F.layers(), "",
        P("Every message between two of our computers travels inside a lock that only those two computers can open.",
          "Sensitive information can get a second lock. The owner seals it for a named list of readers, and only those readers hold keys. The computers that carry and store it in between hold no key at all. That includes the servers that our own programs run on.",
          "The same is true for the place where secrets such as passwords are kept. A secret is locked on your own computer or phone before it is stored, so the store cannot read what it is holding."),
        "If someone steals a server, what they get is a pile of locked boxes."))

    parts.append(section("verified", "Nothing unchecked runs", "Every program is checked before it is allowed to start", F.verified(), "",
        P("Programs are written by people as text. A <dfn>build</dfn> turns that text into a program a computer can run, the way baking turns a recipe into bread.",
          "A <dfn>release</dfn> is one finished, numbered version of a program that is ready for others to use.",
          "An <dfn>image</dfn> is a complete, packed copy of a program with everything it needs, ready to run. Think of a sealed package from a factory.",
          "A <dfn>deployment</dfn> is the act of putting a program onto the computers where it will run.",
          "Before anything is put onto a computer, it is checked the way you would check that sealed package. Is the maker's seal on it, and is the seal real? Are the contents exactly what the label says, with nothing added or swapped? If either check fails, the program is refused and never starts."),
        "A program that has been tampered with is refused before it reaches a single computer."))

    parts.append(section("quantum", "A problem from the future", "Locked messages copied today could be opened years from now", F.quantum(), "",
        P("A new kind of computer, called a quantum computer, is being developed. It is expected to be able to break some of the locks that protect messages today.",
          "That creates a danger now, not only later. Someone can copy locked messages today, keep them, and wait. This is called <dfn>harvest now, decrypt later</dfn>. For information that must stay private for many years, a lock that will fail in ten years is already not good enough.",
          "<dfn>Post-quantum</dfn> locks are designed to hold even against such a computer. Our design uses two locks together: the usual kind, and a post-quantum kind. To read the message, someone would have to break both."),
        "We add a second lock that is built to hold against the code-breaking computers of the future.") .replace('<div class="short">', S("Where this stands: the two locks together are working today on the part of the network that delivers messages between programs. For the connections between computers it is built and not yet switched on. For connections between different organizations it is planned.") + '\n    <div class="short">', 1))

    parts.append(section("decoys", "Decoys", "A door that leads nowhere, and rings a bell", F.decoys(), "",
        P("A <dfn>decoy</dfn> is something that looks real and useful but that nobody has any reason to touch: a name or an address that leads nowhere.",
          "The people and programs that belong on the network never go near a decoy. So when someone does touch one, there is only one explanation. An alarm goes to the person on duty at once.",
          "Ordinary alarms have to notice something unusual among everything normal, so a quiet intruder can go unseen for a long time. An alarm from a decoy is never set off by normal work."),
        "Anyone who tries a decoy door has told us they do not belong.") .replace('<div class="short">', S("Where this stands: decoy names and addresses are built. More kinds of decoy are planned.") + '\n    <div class="short">', 1))

    parts.append(section("rebuild", "Starting again clean", "A whole site can be wiped and set up again with less than an hour of machine work", F.rebuild(),
        "",
        P("If your phone behaves strangely and you suspect something bad is on it, the surest fix is to erase it and set it up again from a clean start. Cleaning it by hand leaves you wondering what you missed.",
          "For a whole site full of computers and programs, starting again has always been slow and painful: days of work, done rarely, by a procedure nobody has practiced. So people avoid it, and an intruder who got in stays in.",
          "In our design, a site is fully described by a written plan. A <dfn>rebuild</dfn> means setting the whole site up again from that plan. One instruction does it: it prepares the computers, locks what is stored on them, starts every program, connects the site to the network, and then runs a set of checks to prove that everything works.") +
        f"""
    <div class="nums">
      <div><b>{m("build", M)}</b><span class="l">of machine working time to set up a whole site, measured on real computers</span></div>
      <div><b>{m("down", M)}</b><span class="l">to take a site down, measured on real computers</span></div>
    </div>
""" + S(f'Where this stands: both times above are measured. The team\'s requirement for its next major version is the whole job, from start to finish with no pauses, in {m("req-site", M)} minutes or less. The team is working toward that now.'),
        "When in doubt about a machine, we do not clean it; we rebuild it, and that takes minutes, not days."))

    parts.append(section("alone", "Cut off, and still working", "A site keeps working when its connection is cut", F.alone(), "",
        P("Picture a town with its own generator and its own well. When a storm takes down the lines to the rest of the country, the lights stay on.",
          "A site in our design is meant to be like that town. Each site carries everything it needs. If its connection to the other sites is cut, the people there keep working.",
          "This has a second benefit. A site that does not depend on a long connection does not have to send anything outward at all. A site that is silent is much harder for anyone to find.",
          "One more piece is planned. If a site can no longer be trusted, the main site can cut it away from the others. From then on nothing it sends reaches anyone else, which protects the rest. But the site that was cut away is not shut down. The people there keep their own systems and keep working. It comes back only after it has been rebuilt."),
        "Losing the connection does not stop a site, and protecting everyone else does not mean destroying one part.") .replace('<div class="short">', S("Where this stands: this part is planned. Pieces of it are built and tested.") + '\n    <div class="short">', 1))

    parts.append(section("open", "Open to inspection", "Anyone can read how it works", F.open_(), "",
        P("All of this work is published. The instructions, the designs and the tests are public, and anyone may read them, use them and check them.",
          "That can sound backwards. Would it not be safer to keep it secret? A lock is only good if it still holds when everyone knows exactly how it is made. Only the keys are secret. Showing the design lets many more people look for weaknesses and tell us, which makes the work stronger.",
          'If you would like to see the same ideas with the technical detail, read <a href="../security/">the security page</a>.'),
        "The design is public; only the keys are secret."))

    words = [
        ("Build", "Turning the text that people write into a program a computer can run."),
        ("Computer network", "A group of computers that can send each other messages."),
        ("Decode", "To translate a message from one machine's way of writing into another's. No secret is needed."),
        ("Decoy", "Something that looks real, that nobody has a reason to touch, and that raises an alarm when touched."),
        ("Decrypt", "To unlock a sealed message with its key and read it."),
        ("Deployment", "Putting a program onto the computers where it will run."),
        ("Encryption", "Scrambling a message so that only the holder of the right key can read it."),
        ("Harvest now, decrypt later", "Copying locked messages today in order to open them years later with a stronger machine."),
        ("Identity", "Proof of exactly who or what is asking: a person, a computer or a program."),
        ("Image", "A complete, packed copy of a program, ready to run."),
        ("Internet", "The largest network: the public roads that almost every computer shares."),
        ("Key", "A long secret number that locks and unlocks a message."),
        ("Link, or transport", "Whatever carries the messages: a cable, a phone network, a satellite."),
        ("Message", "Anything one computer sends to another."),
        ("Overlay", "A private, locked route laid across the public roads."),
        ("Post-quantum", "A lock designed to hold against the code-breaking computers of the future."),
        ("Program", "A set of instructions that a computer follows."),
        ("Quantum computer", "A new kind of computer, still being developed, that is expected to break some of today's locks."),
        ("Rebuild", "Setting a whole site up again from its written plan, from a clean start."),
        ("Relay", "A rented computer that passes sealed messages along and cannot read them."),
        ("Release", "One finished, numbered version of a program."),
        ("Sealed", "Encrypted."),
        ("Server", "A computer whose job is to run programs for many other computers."),
        ("Site", "One place and the group of computers there."),
        ("Underlay", "The shared links that everyone uses, taken together."),
        ("Zero trust", "Nothing is trusted because of where it is; every request is checked."),
    ]
    dl = "\n".join(f"      <dt>{t}</dt><dd>{d}</dd>" for t, d in words)
    parts.append(f"""
<section id="words">
  <div class="wrap">
    <p class="num">Words used here</p>
    <h2>Every special word on this page</h2>
    <dl class="words">
{dl}
    </dl>
  </div>
</section>
<footer>
  <div class="wrap">
    <p><a href="../security/">The technical version</a><a href="https://github.com/USAREUR-AF/goatcore">Repository</a><a href="https://github.com/USAREUR-AF/goatcore/blob/main/LICENSE">Apache License 2.0</a><a href="https://github.com/USAREUR-AF/goatcore/blob/main/SECURITY.md">Security policy</a></p>
    <p>Portions written by U.S. Federal government employees within the scope of their employment are in the public domain in the United States. Part of <a href="https://github.com/USAREUR-AF/goatcore">goat</a>.</p>
  </div>
</footer>
</body>
</html>
""")
    return "".join(parts)


def main():
    html = render()
    if "--check" in sys.argv[1:]:
        if not PAGE.exists() or PAGE.read_text() != html:
            print("docs/goat/sec4laymen: index.html is not current; run build.py")
            return 1
        print("docs/goat/sec4laymen: current")
        return 0
    PAGE.write_text(html)
    print(f"docs/goat/sec4laymen: wrote index.html ({len(html)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
