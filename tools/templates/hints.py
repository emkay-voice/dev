"""Template: hints when nobody understood – a fallback skill."""
NAME, MODULE, CLASS, REPO = "ovos-skill-hints-example", "ovos_skill_hints_example", "HintsSkill", "emkay-voice/ovos-skill-hints-example"
SUMMARY = "Hints when nobody understood: a fallback skill that suggests the sentence you may have meant"
KEYWORDS = ["fallback", "hints", "help"]
DEPENDENCIES = []

CODE = '''
"""Hints when nobody understood: "um, the clock thing" -> "Did you mean: what time is it?"

A fallback skill: there are no intents. When no skill understood what you
said, OpenVoiceOS first asks every fallback skill whether it can answer
(can_answer), then lets them try one by one, lowest priority number first
(PRIORITY). This one looks for a word it knows in the sentence
(locale/<language>/hints.list, one line each:  word, word | the sentence to
suggest) and suggests that sentence. If it finds none it returns False, and
the next fallback gets its turn – in the end the one that says "I don't
understand".

Try changing: the words and sentences in hints.list (sentences that your
own skills understand), PRIORITY, or ask back instead ("Shall I?") and say
the sentence for the user.
"""
from ovos_bus_client.session import SessionManager
from ovos_workshop.decorators import fallback_handler
from ovos_workshop.skills.fallback import FallbackSkill

PRIORITY = 80   # 0-100: lower is asked first; "I don't understand" is 100


def words(text):
    return " ".join("".join(c if c.isalnum() else " " for c in (text or "").lower()).split())


def find_hint(sentence, hints):
    """The sentence to suggest for the first word of `hints` that is in `sentence`, or None."""
    said = f" {words(sentence)} "
    for keys, suggestion in hints:
        if any(f" {words(k)} " in said for k in keys):
            return suggestion
    return None


class HintsSkill(FallbackSkill):

    def hints(self, lang):
        """[([words], sentence)] from hints.list in that language."""
        path = self.find_resource("hints.list", lang=lang)
        out = []
        for line in open(path, encoding="utf-8") if path else []:
            if "|" in line and not line.startswith("#"):
                keys, suggestion = line.split("|", 1)
                out.append(([k.strip() for k in keys.split(",") if k.strip()], suggestion.strip()))
        return out

    def hint_for(self, message):
        lang = SessionManager.get(message).lang or self.lang
        hints = self.hints(lang)
        for utterance in message.data.get("utterances") or [message.data.get("utterance", "")]:
            hint = find_hint(utterance, hints)
            if hint:
                return hint
        return None

    def can_answer(self, message):
        """Asked before the fallback runs: can we say something useful to this?"""
        return self.hint_for(message) is not None

    @fallback_handler(priority=PRIORITY)
    def handle_fallback(self, message):
        """Nobody understood: True when we said something, False to let the next fallback try."""
        hint = self.hint_for(message)
        if not hint:
            return False
        self.speak_dialog("did_you_mean", {"sentence": hint})
        return True
'''

TEST = '''
def test_the_skill_can_be_made():
    # OpenVoiceOS refuses to load a FallbackSkill without can_answer
    assert not getattr(pkg.HintsSkill, "__abstractmethods__", None)
def test_a_hint_by_a_word_in_the_sentence():
    hints = [(["clock", "time"], "what time is it"), (["joke"], "tell me a joke")]
    assert pkg.find_hint("um the clock thing", hints) == "what time is it"
    assert pkg.find_hint("a JOKE please", hints) == "tell me a joke"
    assert pkg.find_hint("blorp the zibble", hints) is None
    assert pkg.find_hint("o'clockwork", hints) is None     # a whole word, not part of one


def test_every_language_has_hints_and_says_the_sentence():
    for lang in LANGS:
        loc = PACKAGE / "locale" / lang
        rows = [l for l in (loc / "hints.list").read_text().splitlines() if l.strip()]
        assert len(rows) >= 4 and all("|" in r for r in rows), lang
        assert "{sentence}" in (loc / "did_you_mean.dialog").read_text(), lang
'''

L = {
"en-US": (["clock, time | what time is it", "joke, funny | tell me a joke", "date, day | what is the date today",
           "timer, alarm | set a timer for five minutes", "weather, rain, umbrella | what is the weather like"],
          ["I didn't get that. Did you mean: “{sentence}”?", "Hm. Maybe try: “{sentence}”."],
          "Hints", "When nobody understood you, it suggests the sentence you may have meant.", ["Um, the clock thing", "Something funny"],
          ["blah blah clock blah", "something funny blah"]),
"da-DK": (["klokken, tid, ur | hvad er klokken", "vittighed, sjovt, joke | fortæl en vittighed", "dato, dag | hvilken dato er det i dag",
           "timer, alarm, æggeur | sæt en timer på fem minutter", "vejr, regn, paraply | hvordan er vejret"],
          ["Det forstod jeg ikke. Mente du: “{sentence}”?", "Hm. Prøv måske: “{sentence}”."],
          "Hint", "Når ingen forstod dig, foreslår den den sætning, du måske mente.", ["Øh, det med klokken", "Noget sjovt"],
          ["æggeur tak", "noget sjovt bla"]),
"de-DE": (["uhr, uhrzeit, zeit | wie spät ist es", "witz, lustig | erzähl mir einen witz", "datum, tag | welches datum ist heute",
           "timer, wecker | stell einen timer auf fünf minuten", "wetter, regen, regenschirm | wie ist das wetter"],
          ["Das habe ich nicht verstanden. Meintest du: „{sentence}“?", "Hm. Versuch es vielleicht mit: „{sentence}“."],
          "Tipps", "Wenn dich niemand verstanden hat, schlägt es den Satz vor, den du vielleicht meintest.", ["Äh, das mit der Uhr", "Etwas Lustiges"],
          ["bla bla uhr bla", "etwas lustig bla"]),
"nl-NL": (["klok, tijd | hoe laat is het", "grap, grappig | vertel een grap", "datum, dag | welke datum is het vandaag",
           "timer, wekker | zet een timer op vijf minuten", "weer, regen, paraplu | hoe is het weer"],
          ["Dat begreep ik niet. Bedoelde je: “{sentence}”?", "Hm. Probeer misschien: “{sentence}”."],
          "Tips", "Als niemand je begreep, stelt het de zin voor die je misschien bedoelde.", ["Eh, dat van de klok", "Iets grappigs"],
          ["bla bla klok bla", "iets grappig bla"]),
"fr-FR": (["heure, horloge | quelle heure est il", "blague, drôle | raconte moi une blague", "date, jour | quelle est la date aujourd'hui",
           "minuteur, alarme | mets un minuteur de cinq minutes", "météo, pluie, parapluie | quel temps fait il"],
          ["Je n'ai pas compris. Tu voulais dire : « {sentence} » ?", "Hum. Essaie peut-être : « {sentence} »."],
          "Astuces", "Quand personne ne t'a compris, elle propose la phrase que tu voulais peut-être dire.", ["Euh, le truc de l'heure", "Quelque chose de drôle"],
          ["bla bla horloge bla", "un truc drôle bla"]),
"es-ES": (["hora, reloj | qué hora es", "chiste, gracioso | cuéntame un chiste", "fecha, día | qué fecha es hoy",
           "temporizador, alarma | pon un temporizador de cinco minutos", "tiempo, lluvia, paraguas | qué tiempo hace"],
          ["No lo he entendido. ¿Querías decir: «{sentence}»?", "Mmm. Prueba quizá con: «{sentence}»."],
          "Pistas", "Cuando nadie te ha entendido, sugiere la frase que quizá querías decir.", ["Eh, lo del reloj", "Algo gracioso"],
          ["bla bla reloj bla", "algo gracioso bla"]),
"it-IT": (["ora, orologio | che ore sono", "barzelletta, divertente | raccontami una barzelletta", "data, giorno | che giorno è oggi",
           "timer, sveglia | imposta un timer di cinque minuti", "tempo, pioggia, ombrello | che tempo fa"],
          ["Non ho capito. Volevi dire: «{sentence}»?", "Mmm. Prova magari con: «{sentence}»."],
          "Suggerimenti", "Quando nessuno ti ha capito, suggerisce la frase che forse volevi dire.", ["Ehm, la cosa dell'orologio", "Qualcosa di divertente"],
          ["bla bla orologio bla", "qualcosa divertente bla"]),
"pt-BR": (["hora, relógio | que horas são", "piada, engraçado | me conte uma piada", "data, dia | que dia é hoje",
           "timer, alarme | coloque um timer de cinco minutos", "tempo, chuva, guarda chuva | como está o tempo"],
          ["Não entendi. Você quis dizer: “{sentence}”?", "Hum. Talvez tente: “{sentence}”."],
          "Dicas", "Quando ninguém te entendeu, sugere a frase que você talvez quis dizer.", ["É, aquilo do relógio", "Algo engraçado"],
          ["blá blá relógio blá", "algo engraçado blá"]),
"pt-PT": (["horas, relógio | que horas são", "anedota, piada, engraçado | conta me uma anedota", "data, dia | que dia é hoje",
           "temporizador, alarme | põe um temporizador de cinco minutos", "tempo, chuva, guarda chuva | como está o tempo"],
          ["Não percebi. Querias dizer: “{sentence}”?", "Hum. Experimenta talvez: “{sentence}”."],
          "Dicas", "Quando ninguém te percebeu, sugere a frase que talvez querias dizer.", ["Hã, aquilo do relógio", "Algo engraçado"],
          ["blá blá relógio blá", "algo engraçado blá"]),
"ca-ES": (["hora, rellotge | quina hora és", "acudit, divertit | explica'm un acudit", "data, dia | quin dia és avui",
           "temporitzador, alarma | posa un temporitzador de cinc minuts", "temps, pluja, paraigua | quin temps fa"],
          ["No ho he entès. Volies dir: «{sentence}»?", "Mmm. Prova potser amb: «{sentence}»."],
          "Pistes", "Quan ningú no t'ha entès, suggereix la frase que potser volies dir.", ["Eh, allò del rellotge", "Alguna cosa divertida"],
          ["bla bla rellotge bla", "alguna cosa divertit bla"]),
"gl-ES": (["hora, reloxo | que hora é", "chiste, gracioso | cóntame un chiste", "data, día | que día é hoxe",
           "temporizador, alarma | pon un temporizador de cinco minutos", "tempo, chuvia, paraugas | que tempo fai"],
          ["Non o entendín. Querías dicir: «{sentence}»?", "Mmm. Proba quizais con: «{sentence}»."],
          "Pistas", "Cando ninguén te entendeu, suxire a frase que quizais querías dicir.", ["Eh, o do reloxo", "Algo gracioso"],
          ["bla bla reloxo bla", "algo gracioso bla"]),
"eu-ES": (["ordua, erlojua | zer ordu da", "txistea, barregarria | kontatu txiste bat", "data, eguna | zein egun da gaur",
           "tenporizadorea, alarma | jarri bost minutuko tenporizadore bat", "eguraldia, euria, aterkia | zer eguraldi dago"],
          ["Ez dut ulertu. Hau esan nahi zenuen: «{sentence}»?", "Hm. Agian saiatu honekin: «{sentence}»."],
          "Pistak", "Inork ulertu ez zaituenean, agian esan nahi zenuen esaldia proposatzen du.", ["Eh, erlojuarena", "Zerbait barregarria"],
          ["bla bla erlojua bla", "zerbait barregarria bla"]),
}

LOCALE = {lang: {"hints.list": "\n".join(v[0]), "did_you_mean.dialog": "\n".join(v[1])} for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v[2], "description": v[3], "examples": v[4]} for lang, v in L.items()}
GOLDEN = {lang: [(v[5][0], None)] for lang, v in L.items()}

README = '''
# Hints when nobody understood

Say something no skill understands, with a word it knows in it –
**"um, the clock thing"** – and it suggests the sentence you may have meant:
*"I didn't get that. Did you mean: “what time is it”?"* – in all twelve of
[Emkay](https://emkay.ai)'s languages.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **A fallback skill, no intents:** when no skill understood a sentence,
  OpenVoiceOS asks the fallback skills one by one, the lowest priority number
  first. `@fallback_handler(priority=PRIORITY)` puts `handle_fallback` in
  that line.
- **can_answer:** OpenVoiceOS first asks every fallback whether it can
  answer; a `FallbackSkill` must have it, or it won't load.
- **True or False:** return `True` when you answered; `False` lets the next
  fallback try – in the end the one that says "I don't understand" (priority
  100).
- **Your own words per language:** `locale/<language>/hints.list`,
  `word, word | the sentence to suggest`.

## Try changing

- `hints.list` – sentences your own skills understand;
- `PRIORITY` – lower is asked earlier;
- ask back instead (`self.ask_yesno(...)`) and, on yes, say the sentence for
  the user: `self.bus.emit(message.forward("recognizer_loop:utterance",
  {"utterances": [hint]}))`.
'''
