"""Template: pictures on the screen – a dog or a cat, from free web services."""
NAME, MODULE, CLASS, REPO = "ovos-skill-pictures-example", "ovos_skill_pictures_example", "PicturesSkill", "emkay-voice/ovos-skill-pictures-example"
SUMMARY = "Shows a picture on the screen: a dog or a cat, from free web services"
KEYWORDS = ["gui", "screen", "pictures", "dog", "cat"]
DEPENDENCIES = ["requests"]

CODE = '''
"""Pictures on the screen: say "show me a dog" or "show me a cat".

The skill asks a free web service for a random picture (no account, no key)
and shows it on the device's screen with self.gui.show_image(). A device
without a screen still hears the answer.

  dogs: https://dog.ceo/dog-api/
  cats: https://thecatapi.com/

Try changing: the title shown with the picture (dog_title.dialog), how the
picture fills the screen (FILL), how long it stays (SHOW_FOR), or show text instead with
self.gui.show_text("Hello!").
"""
import requests

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

DOG_API = "https://dog.ceo/api/breeds/image/random"
CAT_API = "https://api.thecatapi.com/v1/images/search"
FILL = "PreserveAspectFit"   # the whole picture; "PreserveAspectCrop" fills the screen
SHOW_FOR = 30                # seconds on the screen before the clock comes back


class PicturesSkill(OVOSSkill):

    def picture(self, kind):
        """The address of a random picture of a dog or a cat, or None."""
        try:
            if kind == "dog":
                return requests.get(DOG_API, timeout=10).json()["message"]
            return requests.get(CAT_API, timeout=10).json()[0]["url"]
        except Exception as e:
            self.log.warning(f"no {kind} picture: {e}")
            return None

    def show(self, kind):
        url = self.picture(kind)
        if not url:
            self.speak_dialog("no_picture")
            return
        self.gui.show_image(url, title=self.dialog_renderer.render(f"{kind}_title"),
                            fill=FILL, override_idle=SHOW_FOR)
        self.speak_dialog(f"{kind}_here")

    @intent_handler("dog.intent")
    def handle_dog(self, message):
        self.show("dog")

    @intent_handler("cat.intent")
    def handle_cat(self, message):
        self.show("cat")
'''

TEST = '''
def test_every_language_has_titles():
    for lang in LANGS:
        for name in ("dog_title", "cat_title", "dog_here", "cat_here", "no_picture"):
            assert (PACKAGE / "locale" / lang / f"{name}.dialog").read_text().strip(), (lang, name)
'''

L = {
"en-US": dict(
  dog=["show me a (dog|puppy)", "(show|give) me a (dog|puppy) picture", "i want to see a (dog|puppy)", "(dog|puppy) picture please"],
  cat=["show me a (cat|kitten)", "(show|give) me a (cat|kitten) picture", "i want to see a (cat|kitten)", "(cat|kitten) picture please"],
  dog_title=["A dog for you", "Woof!"], cat_title=["A cat for you", "Meow!"],
  dog_here=["Here is a dog.", "Look at this dog."], cat_here=["Here is a cat.", "Look at this cat."],
  no_picture=["I couldn't get a picture right now.", "The picture service didn't answer. Try again in a moment."],
  name="Pictures", desc="Shows a picture of a dog or a cat on the screen.", ex=["Show me a dog", "Show me a cat"],
  gold=[("show me a dog", "dog"), ("i want to see a puppy", "dog"), ("show me a cat", "cat"), ("give me a kitten picture", "cat")]),
"da-DK": dict(
  dog=["vis mig en (hund|hundehvalp)", "(vis|giv) mig et (hundebillede|billede af en hund)", "jeg vil se en (hund|hundehvalp)", "(hundebillede|billede af en hund) tak", "vis en hund"],
  cat=["vis mig en (kat|killing)", "(vis|giv) mig et (kattebillede|billede af en kat)", "jeg vil se en (kat|killing)", "(kattebillede|billede af en kat) tak", "vis en kat"],
  dog_title=["En hund til dig", "Vov!"], cat_title=["En kat til dig", "Miav!"],
  dog_here=["Her er en hund.", "Se lige den her hund."], cat_here=["Her er en kat.", "Se lige den her kat."],
  no_picture=["Jeg kunne ikke hente et billede lige nu.", "Billedtjenesten svarede ikke. Prøv igen om lidt."],
  name="Billeder", desc="Viser et billede af en hund eller en kat på skærmen.", ex=["Vis mig en hund", "Vis mig en kat"],
  gold=[("vis mig en hund", "dog"), ("jeg vil se en hundehvalp", "dog"), ("vis mig en kat", "cat"), ("giv mig et kattebillede", "cat")]),
"de-DE": dict(
  dog=["zeig mir einen (hund|welpen)", "(zeig|gib) mir ein (hundebild|bild von einem hund)", "ich will einen (hund|welpen) sehen", "(hundebild|bild von einem hund) bitte", "zeig einen hund"],
  cat=["zeig mir eine (katze|babykatze)", "(zeig|gib) mir ein (katzenbild|bild von einer katze)", "ich will eine (katze|babykatze) sehen", "(katzenbild|bild von einer katze) bitte", "zeig eine katze"],
  dog_title=["Ein Hund für dich", "Wuff!"], cat_title=["Eine Katze für dich", "Miau!"],
  dog_here=["Hier ist ein Hund.", "Schau dir diesen Hund an."], cat_here=["Hier ist eine Katze.", "Schau dir diese Katze an."],
  no_picture=["Ich konnte gerade kein Bild holen.", "Der Bilderdienst hat nicht geantwortet. Versuch es gleich noch einmal."],
  name="Bilder", desc="Zeigt ein Bild von einem Hund oder einer Katze auf dem Bildschirm.", ex=["Zeig mir einen Hund", "Zeig mir eine Katze"],
  gold=[("zeig mir einen hund", "dog"), ("ich will einen welpen sehen", "dog"), ("zeig mir eine katze", "cat"), ("gib mir ein katzenbild", "cat")]),
"nl-NL": dict(
  dog=["laat me een (hond|puppy) zien", "(toon|geef) me een (hondenfoto|foto van een hond)", "ik wil een (hond|puppy) zien", "(hondenfoto|foto van een hond) graag", "toon een hond"],
  cat=["laat me een (kat|kitten) zien", "(toon|geef) me een (kattenfoto|foto van een kat)", "ik wil een (kat|kitten) zien", "(kattenfoto|foto van een kat) graag", "toon een kat"],
  dog_title=["Een hond voor jou", "Waf!"], cat_title=["Een kat voor jou", "Miauw!"],
  dog_here=["Hier is een hond.", "Kijk eens naar deze hond."], cat_here=["Hier is een kat.", "Kijk eens naar deze kat."],
  no_picture=["Ik kon nu geen foto ophalen.", "De fotodienst gaf geen antwoord. Probeer het zo nog eens."],
  name="Foto's", desc="Toont een foto van een hond of een kat op het scherm.", ex=["Laat me een hond zien", "Laat me een kat zien"],
  gold=[("laat me een hond zien", "dog"), ("ik wil een puppy zien", "dog"), ("laat me een kat zien", "cat"), ("geef me een kattenfoto", "cat")]),
"fr-FR": dict(
  dog=["montre moi un (chien|chiot)", "(montre|donne) moi une photo (de chien|d'un chien)", "je veux voir un (chien|chiot)", "une photo (de chien|d'un chien) s'il te plaît", "montre un chien"],
  cat=["montre moi un (chat|chaton)", "(montre|donne) moi une photo (de chat|d'un chat)", "je veux voir un (chat|chaton)", "une photo (de chat|d'un chat) s'il te plaît", "montre un chat"],
  dog_title=["Un chien pour toi", "Ouaf !"], cat_title=["Un chat pour toi", "Miaou !"],
  dog_here=["Voici un chien.", "Regarde ce chien."], cat_here=["Voici un chat.", "Regarde ce chat."],
  no_picture=["Je n'ai pas pu obtenir de photo pour l'instant.", "Le service de photos n'a pas répondu. Réessaie dans un instant."],
  name="Images", desc="Affiche une photo de chien ou de chat à l'écran.", ex=["Montre-moi un chien", "Montre-moi un chat"],
  gold=[("montre moi un chien", "dog"), ("je veux voir un chiot", "dog"), ("montre moi un chat", "cat"), ("donne moi une photo de chat", "cat")]),
"es-ES": dict(
  dog=["enséñame un (perro|cachorro)", "(enséñame|dame) una foto de un (perro|cachorro)", "quiero ver un (perro|cachorro)", "una foto de (perro|un perro) por favor", "muestra un perro"],
  cat=["enséñame un (gato|gatito)", "(enséñame|dame) una foto de un (gato|gatito)", "quiero ver un (gato|gatito)", "una foto de (gato|un gato) por favor", "muestra un gato"],
  dog_title=["Un perro para ti", "¡Guau!"], cat_title=["Un gato para ti", "¡Miau!"],
  dog_here=["Aquí tienes un perro.", "Mira este perro."], cat_here=["Aquí tienes un gato.", "Mira este gato."],
  no_picture=["No he podido conseguir una foto ahora mismo.", "El servicio de fotos no ha respondido. Inténtalo de nuevo en un momento."],
  name="Imágenes", desc="Muestra una foto de un perro o un gato en la pantalla.", ex=["Enséñame un perro", "Enséñame un gato"],
  gold=[("enséñame un perro", "dog"), ("quiero ver un cachorro", "dog"), ("enséñame un gato", "cat"), ("dame una foto de un gatito", "cat")]),
"it-IT": dict(
  dog=["fammi vedere un (cane|cucciolo)", "(mostrami|dammi) una foto di un (cane|cucciolo)", "voglio vedere un (cane|cucciolo)", "una foto di (cane|un cane) per favore", "mostra un cane"],
  cat=["fammi vedere un (gatto|gattino)", "(mostrami|dammi) una foto di un (gatto|gattino)", "voglio vedere un (gatto|gattino)", "una foto di (gatto|un gatto) per favore", "mostra un gatto"],
  dog_title=["Un cane per te", "Bau!"], cat_title=["Un gatto per te", "Miao!"],
  dog_here=["Ecco un cane.", "Guarda questo cane."], cat_here=["Ecco un gatto.", "Guarda questo gatto."],
  no_picture=["Non sono riuscito a trovare una foto adesso.", "Il servizio di foto non ha risposto. Riprova tra poco."],
  name="Immagini", desc="Mostra sullo schermo la foto di un cane o di un gatto.", ex=["Fammi vedere un cane", "Fammi vedere un gatto"],
  gold=[("fammi vedere un cane", "dog"), ("voglio vedere un cucciolo", "dog"), ("fammi vedere un gatto", "cat"), ("dammi una foto di un gattino", "cat")]),
"pt-BR": dict(
  dog=["me mostre um (cachorro|filhote)", "(me mostre|me dê) uma foto de um (cachorro|filhote)", "quero ver um (cachorro|filhote)", "uma foto de (cachorro|um cachorro) por favor", "mostre um cachorro"],
  cat=["me mostre um (gato|gatinho)", "(me mostre|me dê) uma foto de um (gato|gatinho)", "quero ver um (gato|gatinho)", "uma foto de (gato|um gato) por favor", "mostre um gato"],
  dog_title=["Um cachorro para você", "Au au!"], cat_title=["Um gato para você", "Miau!"],
  dog_here=["Aqui está um cachorro.", "Olha só este cachorro."], cat_here=["Aqui está um gato.", "Olha só este gato."],
  no_picture=["Não consegui pegar uma foto agora.", "O serviço de fotos não respondeu. Tente de novo daqui a pouco."],
  name="Imagens", desc="Mostra a foto de um cachorro ou de um gato na tela.", ex=["Me mostre um cachorro", "Me mostre um gato"],
  gold=[("me mostre um cachorro", "dog"), ("quero ver um filhote", "dog"), ("me mostre um gato", "cat"), ("me dê uma foto de um gatinho", "cat")]),
"pt-PT": dict(
  dog=["mostra-me um (cão|cachorro)", "(mostra-me|dá-me) uma fotografia de um (cão|cachorro)", "quero ver um (cão|cachorro)", "uma fotografia de (cão|um cão) por favor", "mostra um cão"],
  cat=["mostra-me um (gato|gatinho)", "(mostra-me|dá-me) uma fotografia de um (gato|gatinho)", "quero ver um (gato|gatinho)", "uma fotografia de (gato|um gato) por favor", "mostra um gato"],
  dog_title=["Um cão para ti", "Ão ão!"], cat_title=["Um gato para ti", "Miau!"],
  dog_here=["Aqui está um cão.", "Olha para este cão."], cat_here=["Aqui está um gato.", "Olha para este gato."],
  no_picture=["Não consegui obter uma fotografia agora.", "O serviço de fotografias não respondeu. Tenta outra vez daqui a pouco."],
  name="Imagens", desc="Mostra no ecrã a fotografia de um cão ou de um gato.", ex=["Mostra-me um cão", "Mostra-me um gato"],
  gold=[("mostra-me um cão", "dog"), ("quero ver um cachorro", "dog"), ("mostra-me um gato", "cat"), ("dá-me uma fotografia de um gatinho", "cat")]),
"ca-ES": dict(
  dog=["ensenya'm un (gos|cadell)", "(ensenya'm|dona'm) una foto d'un (gos|cadell)", "vull veure un (gos|cadell)", "una foto (de gos|d'un gos) si us plau", "mostra un gos"],
  cat=["ensenya'm un (gat|gatet)", "(ensenya'm|dona'm) una foto d'un (gat|gatet)", "vull veure un (gat|gatet)", "una foto (de gat|d'un gat) si us plau", "mostra un gat"],
  dog_title=["Un gos per a tu", "Bub!"], cat_title=["Un gat per a tu", "Mèu!"],
  dog_here=["Aquí tens un gos.", "Mira aquest gos."], cat_here=["Aquí tens un gat.", "Mira aquest gat."],
  no_picture=["Ara mateix no he pogut aconseguir cap foto.", "El servei de fotos no ha respost. Torna-ho a provar d'aquí a una estona."],
  name="Imatges", desc="Mostra a la pantalla la foto d'un gos o d'un gat.", ex=["Ensenya'm un gos", "Ensenya'm un gat"],
  gold=[("ensenya'm un gos", "dog"), ("vull veure un cadell", "dog"), ("ensenya'm un gat", "cat"), ("dona'm una foto d'un gatet", "cat")]),
"gl-ES": dict(
  dog=["amósame un (can|cachorro)", "(amósame|dáme) unha foto dun (can|cachorro)", "quero ver un (can|cachorro)", "unha foto (de can|dun can) por favor", "amosa un can"],
  cat=["amósame un (gato|gatiño)", "(amósame|dáme) unha foto dun (gato|gatiño)", "quero ver un (gato|gatiño)", "unha foto (de gato|dun gato) por favor", "amosa un gato"],
  dog_title=["Un can para ti", "Guau!"], cat_title=["Un gato para ti", "Miau!"],
  dog_here=["Aquí tes un can.", "Mira este can."], cat_here=["Aquí tes un gato.", "Mira este gato."],
  no_picture=["Agora mesmo non puiden conseguir ningunha foto.", "O servizo de fotos non respondeu. Téntao de novo nun momento."],
  name="Imaxes", desc="Amosa na pantalla a foto dun can ou dun gato.", ex=["Amósame un can", "Amósame un gato"],
  gold=[("amósame un can", "dog"), ("quero ver un cachorro", "dog"), ("amósame un gato", "cat"), ("dáme unha foto dun gatiño", "cat")]),
"eu-ES": dict(
  dog=["erakutsi (txakur|txakurkume) bat", "(erakutsi|eman) (txakur|txakurkume) baten argazki bat", "(txakur|txakurkume) bat ikusi nahi dut", "(txakur|txakurkume) baten argazkia mesedez", "txakur bat erakutsidazu"],
  cat=["erakutsi (katu|katakume) bat", "(erakutsi|eman) (katu|katakume) baten argazki bat", "(katu|katakume) bat ikusi nahi dut", "(katu|katakume) baten argazkia mesedez", "katu bat erakutsidazu"],
  dog_title=["Txakur bat zuretzat", "Au au!"], cat_title=["Katu bat zuretzat", "Miau!"],
  dog_here=["Hemen duzu txakur bat.", "Begira txakur hau."], cat_here=["Hemen duzu katu bat.", "Begira katu hau."],
  no_picture=["Ezin izan dut argazkirik lortu orain.", "Argazki zerbitzuak ez du erantzun. Saiatu berriro pixka bat barru."],
  name="Irudiak", desc="Txakur edo katu baten argazkia erakusten du pantailan.", ex=["Erakutsi txakur bat", "Erakutsi katu bat"],
  gold=[("erakutsi txakur bat", "dog"), ("txakurkume bat ikusi nahi dut", "dog"), ("erakutsi katu bat", "cat"), ("eman katakume baten argazki bat", "cat")]),
}

DIALOGS = ("dog_title", "cat_title", "dog_here", "cat_here", "no_picture")
LOCALE = {lang: {"dog.intent": "\n".join(v["dog"]), "cat.intent": "\n".join(v["cat"]),
                 **{f"{k}.dialog": "\n".join(v[k]) for k in DIALOGS}}
          for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v["name"], "description": v["desc"], "examples": v["ex"]} for lang, v in L.items()}
GOLDEN = {lang: [(u, f"{i}.intent") for u, i in v["gold"]] for lang, v in L.items()}

README = '''
# Pictures on the screen

Say **"show me a dog"** or **"show me a cat"**: the skill asks a free web
service for a random picture and shows it on the device's screen – in all
twelve of [Emkay](https://emkay.ai)'s languages. A device without a screen
still hears the answer.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **The screen:** `self.gui.show_image(url, title=..., fill=...)` shows a
  picture. `self.gui` can also show text (`show_text`), a web page
  (`show_url`) or your own page – see the
  [OVOS GUI docs](https://openvoiceos.github.io/ovos-technical-manual/gui/).
- **Asking the web:** two free services, no account or key –
  [dog.ceo](https://dog.ceo/dog-api/) and [The Cat API](https://thecatapi.com/).
  Emkay's *What's happening?* view shows each call.
- **One handler, two intents:** `dog.intent` and `cat.intent` both end in
  `show()`; the dialogs are named after the animal (`dog_here.dialog`,
  `cat_here.dialog`).
- **Text from a dialog without speaking it:**
  `self.dialog_renderer.render("dog_title")` – the title on the screen.

## Try changing

- `FILL` – `PreserveAspectCrop` fills the whole screen;
- `SHOW_FOR` – how many seconds the picture stays before the clock comes back;
- show text instead: `self.gui.show_text("Hello!")`;
- a third animal: a new intent, two dialogs, and a free picture service.
'''
