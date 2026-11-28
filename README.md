# dev.emkay.ai – Emkay Dev

Making skills for [Emkay](https://emkay.ai) – OpenVoiceOS in the browser –
in two ways, to the same skill: with blocks ([Emkay Blocks](https://blocks.emkay.ai))
or with code (Emkay Code: VS Code with Emkay next to your code – write a
skill, save, talk to it; [emkay-voice/code](https://github.com/emkay-voice/code)). In all twelve of Emkay's languages, the same way
as [emkay.ai](https://github.com/emkay-voice/emkay-voice.github.io):
`texts.js` has every text by language, English as the fallback.

| What | Where |
|---|---|
| Emkay Dev, the way in: blocks or code | `index.html` |
| Emkay Blocks: the blocks way, with examples | `blocks/index.html` (the examples come from blocks.emkay.ai) |
| Emkay Code: the VS Code way, step by step | `code/index.html` (the old front page's links, `/#help` …, go on there) |
| Every text, by language | `texts.js` (`hub_*` for the way in) |
| Templates for *Emkay: New skill* | `templates.json` → `templates/<id>.json` + `templates/index.json`, built by `tools/build_templates.mjs` from each template's own repository |
| The Emkay Code extension | built from [emkay-voice/code](https://github.com/emkay-voice/code) into `vscode/`, for VS Code for the Web's *Developer: Install Extension from Location…* |

GitHub Actions builds and publishes it on every push, every night, and
when the extension or a template asks for it (`repository_dispatch`
type `rebuild`).

## Adding a template

A template is a real, working skill (or plugin) in its own repository.
Add an entry to [`templates.json`](templates.json):

- `id`, `kind` (`skill`, `reading`, `fallback`, `query`, `ocp`, …), `icon`, `repo`, `ref`
- `name` and `description` per language (at least `en`)
- `replace`: `[text in the template, placeholder]` pairs, applied in order
  to file names and text files. Placeholders: `{{name}}`
  (`ovos-skill-coffee-facts`), `{{module}}` (`ovos_skill_coffee_facts`),
  `{{id}}` (`ovos-skill-coffee-facts.you`), `{{Class}}`
  (`CoffeeFactsSkill`), `{{Title}}` (`Coffee Facts`), `{{repo}}`
  (`you/ovos-skill-coffee-facts`), `{{author}}`
- `skip`: files to leave out

Emkay Dev = Emkay Blocks + Emkay Code: [#4](https://github.com/emkay-voice/dev/issues/4).
