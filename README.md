# dev.emkay.ai

The page that gets you going with your own OpenVoiceOS skill: VS Code in
the browser with [Emkay](https://emkay.ai) next to your code – write a
skill, save, talk to it. In all twelve of Emkay's languages, the same way
as [emkay.ai](https://github.com/emkay-voice/emkay-voice.github.io):
`texts.js` has every text by language, English as the fallback.

| What | Where |
|---|---|
| The page | `index.html`, `texts.js` |
| Templates for *Emkay: New skill* | `templates.json` → `templates/<id>.json` + `templates/index.json`, built by `tools/build_templates.mjs` from each template's own repository |
| The Emkay Dev extension | built from [emkay-voice/vscode-emkay](https://github.com/emkay-voice/vscode-emkay) into `vscode/`, for VS Code for the Web's *Developer: Install Extension from Location…* until it is on the Marketplace |

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

Part of [Emkay Dev](https://github.com/emkay-voice/emkay/issues/43).
