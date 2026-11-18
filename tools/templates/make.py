"""Make one of Emkay Dev's template repositories from its spec.

    python3 tools/templates/make.py <id> <out dir> [<skill-template checkout>]

A template is a repository like emkay-voice/skill-template: a skill in all
twelve of Emkay's languages, its golden utterances, pytest checks, the
Codespaces/Dev Container workshop, "Make it yours" and "Publish to PyPI".
What they share comes from skill-template itself (its .devcontainer, .vscode,
workflows, LICENSE, .gitignore), with the names swapped; what is the
template's own is in tools/templates/<id>.py:

    NAME, MODULE, CLASS, REPO   ovos-skill-quiz-example, ovos_skill_quiz_example, QuizSkill, emkay-voice/ovos-skill-quiz-example
    SUMMARY, KEYWORDS, DEPENDENCIES
    CODE                        the package's __init__.py
    LOCALE                      {lang: {file name: text}}  (every language the same files)
    SKILL_JSON                  {lang: {name, description, examples}}
    GOLDEN                      {lang: [(utterance, intent file)]}
    TEST                        extra pytest code (gets pkg, SKILL_ID, Message, FakeBus)
    README                      the README, Markdown (the shared "Try it" part is added)
    FILES                       optional {path: text} more files at the repository root

The result is checked like OpenVoiceOS checks translations (ovos-localize)
by the template's own test workflow.
"""
import importlib.util
import itertools
import re
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
LANGS = ["en-US", "da-DK", "de-DE", "nl-NL", "fr-FR", "es-ES", "it-IT", "pt-BR", "pt-PT", "ca-ES", "gl-ES", "eu-ES"]
SHARED = [".gitignore", "LICENSE", ".devcontainer/devcontainer.json", ".devcontainer/setup.sh",
          ".devcontainer/ovos.sh", ".vscode/extensions.json", ".vscode/tasks.json",
          ".github/workflows/test.yml", ".github/workflows/publish.yml", ".github/workflows/make-it-yours.yml"]

TEST_HEAD = '''"""Quick checks that run without OpenVoiceOS running: `pytest`.

Talking to the skill is the real test - in Emkay (Emkay: Test the skill)
or with ovos-tui-client against an OVOS - but these catch the usual slips
early: a language missing a file, or an intent with no answer.
"""
import json
import sys
from pathlib import Path

from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

ROOT = Path(__file__).parent.parent
PACKAGE = ROOT / "{module}"
sys.path.insert(0, str(ROOT))
import {module} as pkg  # noqa: E402

SKILL_ID = "{id}"
LANGS = sorted(p.name for p in (PACKAGE / "locale").iterdir() if p.is_dir())


def test_every_language_has_the_same_files():
    first = sorted(f.name for f in (PACKAGE / "locale" / LANGS[0]).iterdir())
    for lang in LANGS[1:]:
        assert sorted(f.name for f in (PACKAGE / "locale" / lang).iterdir()) == first, lang


def test_golden_utterances_are_for_this_skill():
    for f in (ROOT / "test" / "end2end").glob("golden_utterances_*.jsonl"):
        for line in f.read_text().splitlines():
            if line.strip():
                assert json.loads(line)["skill_id"] == SKILL_ID, f.name
'''

PYPROJECT = '''[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = {summary}
readme = "README.md"
license = {{text = "Apache-2.0"}}
authors = [{{name = "emkay-voice"}}]
requires-python = ">=3.10"
keywords = {keywords}
classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
]
# what the skill needs besides OpenVoiceOS itself; Emkay installs these too
dependencies = [
{deps}
]

[project.optional-dependencies]
test = ["pytest", "ovos-bus-client"]

[project.urls]
Homepage = "https://github.com/{repo}"

# how OpenVoiceOS finds the skill: "<skill id>" = "<package>:<class>"
[project.entry-points."opm.skill"]
"{id}" = "{module}:{cls}"

[tool.setuptools]
packages = ["{module}"]

[tool.setuptools.package-data]
{module} = ["locale/**/*"]

[tool.pytest.ini_options]
addopts = "--import-mode=importlib"
testpaths = ["tests"]
'''

ABOUT = '''
## A working skill, and a template

This is a complete OpenVoiceOS skill – install it and it works – and an
example to start your own from: *Use this template* on GitHub, or
*Emkay: New skill* in VS Code ([Emkay Dev](https://dev.emkay.ai)), which
gives it your own names. Made for [Emkay](https://emkay.ai), it runs on any
OpenVoiceOS.
'''

WHEN_IT_WORKS = '''
## Try it

- **Emkay Dev (VS Code):** *Emkay: Run the skill in Emkay* (Ctrl+Alt+E) opens
  Emkay next to your code and loads the skill; type under Emkay to talk to it.
  Every save loads it again. *Emkay: Test the skill* sends the golden
  utterances and shows ✓ / ✗ in the Testing view. Emkay's menu →
  *Guardian* → *What's happening?* shows which skill took a sentence, and why.
- **ovos-tui-client (Codespaces, Dev Container):** run `ovos-tui` in the
  terminal, type to talk, `Ctrl+P` → *Test* runs the same golden utterances
  against a full OpenVoiceOS.
- **pytest:** `pytest -q` – no OpenVoiceOS needed.

When you make a repository from this template ("Use this template"), a
small workflow renames the skill after your repository and then removes
itself.

## Show it, on your own Emkay, and into the store

To show it in [See my skill](https://dev.emkay.ai/#gallery) on dev.emkay.ai –
ready or not – add the topic `emkay-skill` to the repository (the ⚙ next to
*About*). Remove the topic, or make the repository private, to take it away.

*Emkay: Send to my Emkay* shows a QR code that installs this skill from
GitHub on the Emkay you scan it with. To get it into the
[Emkay store](https://store.emkay.ai): topics `ovos` and `openvoiceos` on the
repository, a release on GitHub (`publish.yml` puts it on PyPI), and the
store's nightly test does the rest – <https://dev.emkay.ai/#store>.

More on writing skills:
[the OpenVoiceOS technical manual](https://openvoiceos.github.io/ovos-technical-manual/).
'''


def expand(line):
    """Every sentence an intent line stands for: (a|b) groups, as padatious reads them."""
    parts = re.split(r"(\([^()]*\))", line)
    opts = [p[1:-1].split("|") if p.startswith("(") else [p] for p in parts]
    return {" ".join("".join(c).split()).lower() for c in itertools.product(*opts)}


def load_spec(tid):
    spec = importlib.util.spec_from_file_location(tid, HERE / f"{tid.replace('-', '_')}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make(tid, out, base):
    s = load_spec(tid)
    out = Path(out)
    sid = f"{s.NAME}.emkay-voice"
    swap = [("ovos-skill-hello.emkay-voice", sid), ("ovos_skill_hello", s.MODULE),
            ("ovos-skill-hello", s.NAME), ("emkay-voice/skill-template", s.REPO)]
    for rel in SHARED:
        text = (Path(base) / rel).read_text()
        for a, b in swap:
            text = text.replace(a, b)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        if rel.endswith(".sh"):
            dest.chmod(0o755)
    pkg = out / s.MODULE
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text(s.CODE.lstrip())
    assert sorted(s.LOCALE) == sorted(LANGS), sorted(s.LOCALE)
    files0 = sorted(s.LOCALE["en-US"])
    for lang, files in s.LOCALE.items():
        assert sorted(files) == files0, (lang, sorted(files), files0)
        d = pkg / "locale" / lang
        d.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (d / name).write_text(text.strip("\n") + "\n")
        sj = {"skill_id": sid, "source": f"https://github.com/{s.REPO}", **s.SKILL_JSON[lang],
              "tags": list(s.KEYWORDS[:3]) + ["emkay"]}
        (d / "skill.json").write_text(json.dumps(sj, ensure_ascii=False, indent=2) + "\n")
    gold = out / "test" / "end2end"
    gold.mkdir(parents=True, exist_ok=True)
    assert sorted(s.GOLDEN) == sorted(LANGS)
    for lang, rows in s.GOLDEN.items():
        for u, i in rows:   # a golden sentence is one the intent says, word for word
            said = set().union(*(expand(l) for l in s.LOCALE[lang][i].splitlines() if l.strip()))
            assert u.lower() in said, f"{lang}: {u!r} is not a sentence of {i}"
        lines = [json.dumps({"skill_id": sid, "utterance": u, "lang": lang, "intent_label": i}, ensure_ascii=False)
                 for u, i in rows]
        (gold / f"golden_utterances_{lang}.jsonl").write_text("\n".join(lines) + "\n")
    (out / "tests").mkdir(exist_ok=True)
    (out / "tests" / "test_skill.py").write_text(
        TEST_HEAD.format(module=s.MODULE, id=sid) + "\n\n" + s.TEST.strip("\n") + "\n")
    (out / "pyproject.toml").write_text(PYPROJECT.format(
        name=s.NAME, summary=json.dumps(s.SUMMARY, ensure_ascii=False),
        keywords=json.dumps(["ovos", "openvoiceos", "skill", "emkay", *s.KEYWORDS]),
        deps="\n".join(f'    "{d}",' for d in ["ovos-workshop>=0.0.15,<10.0.0", *s.DEPENDENCIES]),
        repo=s.REPO, id=sid, module=s.MODULE, cls=s.CLASS))
    (out / "README.md").write_text(s.README.strip("\n") + "\n" + ABOUT + WHEN_IT_WORKS)
    for rel, text in getattr(s, "FILES", {}).items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(text)
    print(f"{tid}: {out} ({sum(1 for p in out.rglob('*') if p.is_file())} files)")


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else str(HERE.parents[2] / "emkay-skill-template"))
