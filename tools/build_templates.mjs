// Build the template catalog for "Emkay: New skill" (the Emkay Code extension).
//
//   node tools/build_templates.mjs <out dir>          (out dir: _site/templates)
//
// For every entry in templates.json: clone its repository, read every file,
// put the entry's "replace" placeholders into the text files ({{name}},
// {{module}}, {{id}}, {{Class}}, {{Title}}, {{repo}}, {{author}} – the
// extension fills them in with the new skill's names), and write
// <out>/<id>.json:  {id, repo, commit, files: {path: {text} | {b64}}}.
// <out>/index.json lists the templates (names and descriptions per
// language) for the extension's picker and the page.
import { execFileSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";

const out = path.resolve(process.argv[2] || "_site/templates");
const catalog = JSON.parse(fs.readFileSync(new URL("../templates.json", import.meta.url), "utf8"));
fs.mkdirSync(out, { recursive: true });

const SKIP_DIRS = new Set([".git", "__pycache__", ".pytest_cache", "node_modules"]);
const index = [];
for (const tpl of catalog) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `tpl-${tpl.id}-`));
  execFileSync("git", ["clone", "--quiet", "--depth", "1", "--branch", tpl.ref || "main",
                       `https://github.com/${tpl.repo}`, dir], { stdio: "inherit" });
  const commit = execFileSync("git", ["-C", dir, "rev-parse", "HEAD"]).toString().trim();
  const skip = new Set(tpl.skip || []);
  const files = {};
  (function walk(d) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      if (SKIP_DIRS.has(e.name) || e.name.endsWith(".egg-info")) continue;
      const p = path.join(d, e.name);
      const rel = path.relative(dir, p).split(path.sep).join("/");
      if (skip.has(rel)) continue;
      if (e.isDirectory()) { walk(p); continue; }
      const bytes = fs.readFileSync(p);
      const text = bytes.includes(0) ? null : bytes.toString("utf8");
      const isText = text !== null && Buffer.from(text, "utf8").equals(bytes);
      let name = rel;
      for (const [from, to] of tpl.replace || []) name = name.split(from).join(to);
      if (isText) {
        let t = text;
        for (const [from, to] of tpl.replace || []) t = t.split(from).join(to);
        files[name] = { text: t };
      } else {
        files[name] = { b64: bytes.toString("base64") };
      }
    }
  })(dir);
  fs.writeFileSync(path.join(out, `${tpl.id}.json`), JSON.stringify({ id: tpl.id, repo: tpl.repo, commit, files }));
  const { replace, skip: _skip, ref, ...entry } = tpl;
  index.push({ ...entry, commit, url: `${tpl.id}.json` });
  console.log(`${tpl.id}: ${Object.keys(files).length} files from ${tpl.repo}@${commit.slice(0, 7)}`);
  fs.rmSync(dir, { recursive: true, force: true });
}
fs.writeFileSync(path.join(out, "index.json"), JSON.stringify(index, null, 1));
