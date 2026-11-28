// See my skill: the gallery on dev.emkay.ai (emkay-voice/dev#2).
//
//   GITHUB_TOKEN=... node tools/build_gallery.mjs <out dir>   (out dir: _site/gallery)
//
// Lists the public GitHub repositories with the topic `emkay-skill` – a
// person puts their skill there by adding the topic, and nobody else can.
// For each: the names, descriptions and example sentences from its
// locale/<lang>/skill.json files, its languages, its owner and when it last
// changed. Written to <out>/skills.json for the pages (gallery.js). Forks are in: GitHub
// does not copy topics to a fork, so a fork with the topic was put here by
// its own owner (someone who made their own version).
//
// It is rebuilt every few hours (.github/workflows/pages.yml), so what its
// owner takes away is gone by the next build, by itself: a repository that
// is deleted, made private or archived, or loses the topic, is simply not
// found any more. gallery-hidden.json lists repositories kept out by hand.
//
// Nothing here is tested: the cards say so. Tested skills are in the store.
//
// The blocks gallery (<out>/blocks.json): blocks people made in Emkay Blocks
// and shared – the blocks of a skill above that was made in Blocks (its
// blocks.json), and *.emkay-block.json files in repositories with the topic
// `emkay-block`. Each is a small Python function; Blocks shows all of it
// before it is used (blocks.emkay.ai/?block=…).
import fs from "fs";
import path from "path";

const out = path.resolve(process.argv[2] || "_site/gallery");
const token = process.env.GITHUB_TOKEN;
const hidden = new Set(JSON.parse(fs.readFileSync(new URL("../gallery-hidden.json", import.meta.url), "utf8"))
  .map((h) => h.repo.toLowerCase()));
// the templates themselves are on the page already
const OURS = /^emkay-voice\/(skill-template|template-.*|ovos-skill-[a-z0-9-]+-example)$/i;
const MAX = 300;
const TOPIC = process.env.GALLERY_TOPIC || "emkay-skill";   // another topic only to try it out

const headers = { accept: "application/vnd.github+json", "user-agent": "emkay-dev-gallery",
  ...(token ? { authorization: `Bearer ${token}` } : {}) };
async function api(url) {
  const r = await fetch(url.startsWith("http") ? url : `https://api.github.com${url}`, { headers });
  if (!r.ok) throw new Error(`${r.status} ${url}`);
  return r.json();
}
async function raw(repo, ref, file) {
  const r = await fetch(`https://raw.githubusercontent.com/${repo}/${ref}/${file}`);
  return r.ok ? r.text() : null;
}

const found = [];
for (let page = 1; page <= 10 && found.length < MAX; page++) {
  const res = await api(`/search/repositories?q=${encodeURIComponent(`topic:${TOPIC} fork:true archived:false is:public`)}&sort=updated&per_page=100&page=${page}`);
  found.push(...res.items);
  if (res.items.length < 100) break;
}

const cards = [];
const blocks = [];
/** A shared block as the gallery shows it: what Blocks needs to offer it, and where it is from. */
function blockCard(r, b, from) {
  if (!b || typeof b.name !== "string" || typeof b.code !== "string" || !Array.isArray(b.inputs)) return;
  blocks.push({
    repo: r.full_name, url: r.html_url, owner: r.owner.login, avatar: r.owner.avatar_url, updated: r.pushed_at, from,
    name: b.name.slice(0, 40), description: String(b.description || "").slice(0, 300), kind: b.kind === "value" ? "value" : "do",
    inputs: b.inputs.slice(0, 8).map((i) => ({ name: String(i.name || "").slice(0, 30), type: i.type === "number" ? "number" : "text" })),
    code: b.code.slice(0, 4000), packages: (Array.isArray(b.packages) ? b.packages : []).map(String).slice(0, 10),
  });
}
for (const r of found.slice(0, MAX)) {
  const repo = r.full_name;
  if (OURS.test(repo) || hidden.has(repo.toLowerCase())) continue;
  try {
    const ref = r.default_branch;
    const tree = await api(`/repos/${repo}/git/trees/${encodeURIComponent(ref)}?recursive=1`);
    const files = (tree.tree || []).map((f) => f.path);
    // locale/<lang>/... anywhere in the package: the languages it speaks
    const langs = new Set();
    const skillJson = {};
    for (const f of files) {
      const m = f.match(/(?:^|\/)locale\/([a-z]{2}(?:-[a-z]{2,4})?)\/(.+)$/i);
      if (!m) continue;
      const lang = m[1].toLowerCase();
      if (/\.(intent|voc|dialog|rx|entity)$/.test(m[2])) langs.add(lang);
      if (m[2] === "skill.json") skillJson[lang] = f;
    }
    if (!langs.size) continue;   // not a skill (no sentences in any language)
    // made in Emkay Blocks: its own blocks are in its blocks.json
    if (files.includes("blocks.json")) {
      try {
        const p = JSON.parse(await raw(repo, ref, "blocks.json"));
        for (const b of p.myBlocks || []) blockCard(r, b, `${repo}#${b.id}`);
      } catch { /* not one of Blocks' */ }
    }
    const name = {}, description = {}, examples = {};
    for (const [lang, f] of Object.entries(skillJson)) {
      try {
        const j = JSON.parse(await raw(repo, ref, f));
        if (j.name) name[lang] = String(j.name).slice(0, 80);
        if (j.description) description[lang] = String(j.description).slice(0, 300);
        if (Array.isArray(j.examples)) examples[lang] = j.examples.slice(0, 3).map((e) => String(e).slice(0, 100));
      } catch { /* a broken skill.json: the card falls back to the repository's own texts */ }
    }
    cards.push({
      repo, url: r.html_url, owner: r.owner.login, avatar: r.owner.avatar_url,
      title: r.name, about: (r.description || "").slice(0, 300),
      name, description, examples, langs: [...langs].sort(),
      stars: r.stargazers_count, updated: r.pushed_at, created: r.created_at, license: r.license?.spdx_id || null,
    });
    console.log(`${repo}: ${langs.size} languages`);
  } catch (e) {
    console.log(`${repo}: skipped (${e.message})`);
  }
}
// repositories of blocks: *.emkay-block.json files, the topic emkay-block
const BLOCK_TOPIC = process.env.GALLERY_BLOCK_TOPIC || "emkay-block";
try {
  const res = await api(`/search/repositories?q=${encodeURIComponent(`topic:${BLOCK_TOPIC} fork:true archived:false is:public`)}&sort=updated&per_page=100`);
  for (const r of res.items) {
    if (hidden.has(r.full_name.toLowerCase())) continue;
    try {
      const tree = await api(`/repos/${r.full_name}/git/trees/${encodeURIComponent(r.default_branch)}?recursive=1`);
      for (const f of (tree.tree || []).map((x) => x.path).filter((x) => x.endsWith(".emkay-block.json")).slice(0, 50)) {
        try { blockCard(r, JSON.parse(await raw(r.full_name, r.default_branch, f)), `${r.full_name}/${f}`); } catch {}
      }
    } catch (e) { console.log(`${r.full_name}: skipped (${e.message})`); }
  }
} catch (e) { console.log(`blocks: ${e.message}`); }

fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, "blocks.json"), JSON.stringify({ built: new Date().toISOString(), blocks }, null, 1));
console.log(`gallery: ${blocks.length} blocks`);
fs.writeFileSync(path.join(out, "skills.json"), JSON.stringify({ built: new Date().toISOString(), skills: cards }, null, 1));
console.log(`gallery: ${cards.length} skills`);
