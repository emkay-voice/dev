"""Template: your own radio – a media skill (OCP) that plays internet radio stations."""
NAME, MODULE, CLASS, REPO = "ovos-skill-radio-example", "ovos_skill_radio_example", "RadioSkill", "emkay-voice/ovos-skill-radio-example"
SUMMARY = "Your own radio: internet radio stations played with OpenVoiceOS' media player (OCP)"
KEYWORDS = ["radio", "media", "ocp"]
DEPENDENCIES = []

CODE = '''
"""Your own radio: say "play Emkay Chill" and it plays.

A media skill: there are no intents. When someone says "play …", OpenVoiceOS'
media player (OCP) asks every media skill what it has for that
(search_radio) and plays the best match – a station, a song, a podcast.
Here: the internet radio stations in STATIONS, from SomaFM (listener-
supported radio, https://somafm.com), under names of their own – Emkay
Chill, Emkay Space, Emkay Lounge – so no other media skill has a station by
the same name (on a tie, the first answer wins). "play some radio"
(radio.voc) offers them all.

Try changing: STATIONS – any stream address works; what counts as a match
(MATCH, and the station's own words in "words"); or add a picture.
"""
from difflib import SequenceMatcher

from ovos_utils.ocp import MediaEntry, MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_featured_media, ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill

#: (name, other words for it, the stream, a picture)
STATIONS = [
    ("Emkay Chill", ["groove", "chill", "ambient beats"], "https://ice2.somafm.com/groovesalad-128-mp3",
     "https://somafm.com/img3/groovesalad-400.jpg"),
    ("Emkay Space", ["drone", "ambient", "space"], "https://ice2.somafm.com/dronezone-128-mp3",
     "https://somafm.com/img3/dronezone-400.jpg"),
    ("Emkay Lounge", ["spy", "lounge", "jazz"], "https://ice2.somafm.com/secretagent-128-mp3",
     "https://somafm.com/img3/secretagent-400.jpg"),
]
MATCH = 0.8   # how alike the words must be to a station's name, 0..1


def words(text):
    return " ".join("".join(c if c.isalnum() else " " for c in (text or "").lower()).split())


def score(phrase, name, others):
    """How sure we are that `phrase` asks for this station, 0..100."""
    p = f" {words(phrase)} "
    if f" {words(name)} " in p:
        return 100        # its whole name: this is the one (and beats a general radio search)
    best = max(SequenceMatcher(None, words(phrase), words(n)).ratio() for n in [name, *others])
    if any(f" {words(o)} " in p for o in others):
        best = max(best, 0.8)
    return int(best * 100) if best >= MATCH else 0


class RadioSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, supported_media=[MediaType.RADIO, MediaType.MUSIC, MediaType.GENERIC], **kwargs)

    def entry(self, station, confidence, media_type=MediaType.RADIO):
        name, _, stream, picture = station
        return MediaEntry(uri=stream, title=name, artist="SomaFM", image=picture,
                          media_type=media_type, playback=PlaybackType.AUDIO,
                          match_confidence=confidence, skill_id=self.skill_id)

    @ocp_search()
    def search_radio(self, phrase, media_type=MediaType.GENERIC):
        """What we have for "play <phrase>": each station that matches, how sure (0..100)."""
        found = [(score(phrase, s[0], s[1]), s) for s in STATIONS]
        found = [(c, s) for c, s in found if c]
        if not found and self.voc_match(phrase, "radio"):
            found = [(60, s) for s in STATIONS]          # "play some radio": all of them
        # OCP guesses from the sentence what kind of media is wanted and drops
        # every answer of another kind: a name it doesn't know ("emkay chill")
        # is often heard as music. Radio plays music, so answer as that kind.
        kind = media_type if media_type in (MediaType.RADIO, MediaType.MUSIC) else MediaType.RADIO
        return [self.entry(s, c, kind) for c, s in sorted(found, key=lambda x: -x[0])]

    @ocp_featured_media()
    def featured(self):
        """What the media player shows when you look at this skill."""
        return [self.entry(s, 100) for s in STATIONS]
'''

TEST = '''
def test_a_station_by_its_name_and_its_words():
    groove = pkg.STATIONS[0]
    assert pkg.score("play emkay chill", groove[0], groove[1]) == 100
    assert pkg.score("play something chill", groove[0], groove[1]) >= 80
    assert pkg.score("play the news", groove[0], groove[1]) == 0


def test_every_language_has_the_word_radio():
    for lang in LANGS:
        assert (PACKAGE / "locale" / lang / "radio.voc").read_text().strip(), lang
'''

L = {
"en-US": ("radio\nradio station\ninternet radio", "My radio", "Plays your own internet radio stations – here three from SomaFM – with OpenVoiceOS' media player.", ["Play Emkay Chill", "Play some radio"], ["play emkay chill", "play emkay space"]),
"da-DK": ("radio\nradiostation\nnetradio\nradiokanal", "Min radio", "Spiller dine egne netradiostationer – her tre fra SomaFM – med OpenVoiceOS' medieafspiller.", ["Spil Emkay Chill", "Spil noget radio"], ["spil emkay chill", "spil emkay space"]),
"de-DE": ("radio\nradiosender\ninternetradio", "Mein Radio", "Spielt deine eigenen Internetradiosender – hier drei von SomaFM – mit dem Mediaplayer von OpenVoiceOS.", ["Spiele Emkay Chill", "Spiele etwas Radio"], ["spiele emkay chill", "spiele emkay space"]),
"nl-NL": ("radio\nradiozender\ninternetradio", "Mijn radio", "Speelt je eigen internetradiozenders – hier drie van SomaFM – met de mediaspeler van OpenVoiceOS.", ["Speel Emkay Chill", "Speel wat radio"], ["speel emkay chill", "speel emkay space"]),
"fr-FR": ("radio\nstation de radio\nwebradio", "Ma radio", "Joue tes propres radios internet – ici trois de SomaFM – avec le lecteur multimédia d'OpenVoiceOS.", ["Joue Emkay Chill", "Joue de la radio"], ["joue emkay chill", "joue emkay space"]),
"es-ES": ("radio\nemisora\nradio por internet", "Mi radio", "Reproduce tus propias emisoras de radio por internet – aquí tres de SomaFM – con el reproductor de OpenVoiceOS.", ["Reproduce Emkay Chill", "Reproduce algo de radio"], ["reproduce emkay chill", "reproduce emkay space"]),
"it-IT": ("radio\nstazione radio\nweb radio", "La mia radio", "Riproduce le tue stazioni radio su internet – qui tre di SomaFM – con il lettore multimediale di OpenVoiceOS.", ["Riproduci Emkay Chill", "Metti un po' di radio"], ["riproduci emkay chill", "riproduci emkay space"]),
"pt-BR": ("rádio\nradio\nestação de rádio", "Meu rádio", "Toca suas próprias rádios da internet – aqui três da SomaFM – com o player de mídia do OpenVoiceOS.", ["Toque Emkay Chill", "Toque uma rádio"], ["toque emkay chill", "toque emkay space"]),
"pt-PT": ("rádio\nradio\nestação de rádio", "O meu rádio", "Toca as tuas rádios da internet – aqui três da SomaFM – com o leitor multimédia do OpenVoiceOS.", ["Toca Emkay Chill", "Toca uma rádio"], ["toca emkay chill", "toca emkay space"]),
"ca-ES": ("ràdio\nradio\nemissora", "La meva ràdio", "Reprodueix les teves emissores de ràdio per internet – aquí tres de SomaFM – amb el reproductor de l'OpenVoiceOS.", ["Reprodueix Emkay Chill", "Posa una mica de ràdio"], ["reprodueix emkay chill", "reprodueix emkay space"]),
"gl-ES": ("radio\nemisora\nradio por internet", "A miña radio", "Reproduce as túas emisoras de radio por internet – aquí tres de SomaFM – co reprodutor de OpenVoiceOS.", ["Reproducir Emkay Chill", "Pon algo de radio"], ["reproducir emkay chill", "reproducir emkay space"]),
"eu-ES": ("irratia\nirrati\nirrati katea", "Nire irratia", "Zure interneteko irrati kateak erreproduzitzen ditu – hemen SomaFM-ren hiru – OpenVoiceOS-en multimedia erreproduzitzailearekin.", ["Erreproduzitu Emkay Chill", "Jarri irratia"], ["erreproduzitu emkay chill", "erreproduzitu emkay space"]),
}

LOCALE = {lang: {"radio.voc": v[0]} for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v[1], "description": v[2], "examples": v[3]} for lang, v in L.items()}
GOLDEN = {lang: [(u, None) for u in v[4]] for lang, v in L.items()}

README = '''
# Your own radio

Say **"play Emkay Chill"** and it plays: a media skill for OpenVoiceOS'
media player (OCP), with three internet radio stations from
[SomaFM](https://somafm.com) – in all twelve of [Emkay](https://emkay.ai)'s
languages.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **Media, no intents:** "play …" goes to OpenVoiceOS' media player, which
  asks every media skill what it has (`@ocp_search` → `search_radio`) and
  plays the best match. You return `MediaEntry`s – the stream, a title, a
  picture and how sure you are (0–100).
- **Featured media:** `@ocp_featured_media` lists what the skill offers, for
  the media player's screen.
- **A word per language:** "play some radio" finds `radio.voc`'s words in the
  sentence, and offers all the stations.

## Try changing

- `STATIONS` – any stream address works: your local station, a podcast feed's
  episodes, your own music server;
- `MATCH` and each station's own words – what counts as asking for it.

SomaFM is listener-supported: if you like it, <https://somafm.com/support/>.
'''
