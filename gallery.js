// See my skill: the cards, shared by the front page (the newest few) and
// gallery/ (all of them, to search and sort). The data is gallery/skills.json,
// made by tools/build_gallery.mjs every six hours.
//
//   const g = await Gallery.load(base)       {built, skills: [...]}
//   Gallery.card(skill, t, lang)              a <div class="card gal">
window.Gallery = (() => {
  /** skill.json is per locale (en-us, da-dk ...): the page's language, else English, else any. */
  function pick(o, lang) {
    if (!o) return "";
    const keys = Object.keys(o);
    const l = lang.toLowerCase();
    const k = keys.find((x) => x === l) || keys.find((x) => x.split("-")[0] === l.split("-")[0])
      || keys.find((x) => x.startsWith("en")) || keys[0];
    return k ? o[k] : "";
  }

  async function load(base = "") {
    try {
      const r = await fetch(base + "gallery/skills.json");
      return r.ok ? await r.json() : { skills: [] };
    } catch { return { skills: [] }; }
  }

  /** What a search matches: names, descriptions, examples, owner and repository, in every language. */
  function haystack(s) {
    const all = (o) => Object.values(o || {}).flat().join(" ");
    return [s.repo, s.owner, s.title, s.about, all(s.name), all(s.description), all(s.examples)].join(" ").toLowerCase();
  }

  function card(s, t, lang) {
    const el = document.createElement("div");
    el.className = "card gal";
    el.innerHTML = `<h3></h3><p class="who"><img alt="" loading="lazy"><span></span><span class="tag"></span></p>
      <p class="about"></p><p class="ex"></p><p class="meta small"></p>
      <div class="btns"><a class="open small" target="_blank" rel="noopener"></a><a class="open small ghost" target="_blank" rel="noopener"></a></div>`;
    el.querySelector("h3").textContent = pick(s.name, lang) || s.title;
    el.querySelector(".who img").src = s.avatar + (s.avatar.includes("?") ? "&" : "?") + "s=44";
    el.querySelector(".who span").textContent = s.owner;
    el.querySelector(".tag").textContent = t("gal_untested");
    el.querySelector(".about").textContent = pick(s.description, lang) || s.about;
    const ex = pick(s.examples, lang);
    el.querySelector(".ex").textContent = ex && ex.length ? `“${ex[0]}”` : "";
    const when = new Date(s.updated).toLocaleDateString(lang, { year: "numeric", month: "short", day: "numeric" });
    el.querySelector(".meta").textContent = t("gal_meta").replace("{langs}", s.langs.length).replace("{when}", when)
      + (s.stars ? ` · ★ ${s.stars}` : "");
    const [tryIt, code] = el.querySelectorAll(".btns a");
    tryIt.href = `https://app.emkay.ai/?install=github:${s.repo}`;
    tryIt.textContent = t("gal_try");
    code.href = `https://vscode.dev/github/${s.repo}`;
    code.textContent = t("gal_code");
    code.title = t("gal_code_hint").replace(/<[^>]+>/g, "");
    return el;
  }

  return { load, card, pick, haystack };
})();
