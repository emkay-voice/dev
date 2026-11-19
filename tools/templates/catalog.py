"""Put generated templates into templates.json (the catalog "New skill" offers).

    python3 tools/templates/catalog.py quiz air pictures

Each template's spec (tools/templates/<id>.py) gives its names; CATALOG
below gives what the catalog shows: icon and, per language, a name and one
line about it. An entry already in templates.json is replaced in place.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make import load_spec  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
KEYS = ["en", "da", "de", "nl", "fr", "es", "it", "pt-BR", "pt-PT", "ca", "gl", "eu"]

CATALOG = {
    "quiz": ("🧠", "quiz", [
        ("A quiz", "It asks, you answer, it keeps score – a skill that listens for your answer (get_response, ask_yesno) and stops when you say stop."),
        ("En quiz", "Den spørger, du svarer, den tæller point – en skill der lytter efter dit svar (get_response, ask_yesno) og stopper, når du siger stop."),
        ("Ein Quiz", "Es fragt, du antwortest, es zählt die Punkte – ein Skill, der auf deine Antwort hört (get_response, ask_yesno) und bei „Stopp“ aufhört."),
        ("Een quiz", "Hij vraagt, jij antwoordt, hij houdt de score bij – een skill die naar je antwoord luistert (get_response, ask_yesno) en stopt als je stop zegt."),
        ("Un quiz", "Il pose une question, tu réponds, il compte les points – une skill qui écoute ta réponse (get_response, ask_yesno) et s'arrête quand tu dis stop."),
        ("Un concurso", "Pregunta, respondes y lleva la cuenta – una skill que escucha tu respuesta (get_response, ask_yesno) y para cuando dices para."),
        ("Un quiz", "Fa una domanda, tu rispondi, tiene il punteggio – una skill che ascolta la tua risposta (get_response, ask_yesno) e si ferma quando dici stop."),
        ("Um quiz", "Ele pergunta, você responde, ele conta os pontos – uma skill que escuta sua resposta (get_response, ask_yesno) e para quando você diz pare."),
        ("Um quiz", "Pergunta, tu respondes, conta os pontos – uma skill que ouve a tua resposta (get_response, ask_yesno) e para quando dizes pára."),
        ("Un concurs", "Pregunta, respons i compta els punts – una skill que escolta la teva resposta (get_response, ask_yesno) i s'atura quan dius para."),
        ("Un concurso", "Pregunta, respondes e leva a conta – unha skill que escoita a túa resposta (get_response, ask_yesno) e para cando dis para."),
        ("Galdetegi bat", "Galdetu egiten du, zuk erantzun, eta puntuak zenbatzen ditu – zure erantzuna entzuten duen skill bat (get_response, ask_yesno)."),
    ]),
    "air": ("🌍", "web", [
        ("Ask the web", "Asks a free web service (Open-Meteo) about the air and the sun where you are – requests, location, and what to say when the network fails."),
        ("Spørg nettet", "Spørger en gratis webtjeneste (Open-Meteo) om luften og solen der, hvor du er – requests, placering, og hvad den siger, når nettet svigter."),
        ("Frag das Netz", "Fragt einen kostenlosen Webdienst (Open-Meteo) nach Luft und Sonne an deinem Ort – requests, Standort und was er sagt, wenn das Netz ausfällt."),
        ("Vraag het web", "Vraagt een gratis webdienst (Open-Meteo) naar de lucht en de zon waar je bent – requests, locatie, en wat hij zegt als het netwerk faalt."),
        ("Interroger le web", "Interroge un service web gratuit (Open-Meteo) sur l'air et le soleil là où tu es – requests, lieu, et quoi dire si le réseau tombe."),
        ("Pregunta a la web", "Pregunta a un servicio web gratuito (Open-Meteo) por el aire y el sol donde estás – requests, ubicación y qué decir si falla la red."),
        ("Chiedi al web", "Chiede a un servizio web gratuito (Open-Meteo) dell'aria e del sole dove sei – requests, posizione e cosa dire se la rete non va."),
        ("Pergunte à web", "Pergunta a um serviço web gratuito (Open-Meteo) sobre o ar e o sol onde você está – requests, localização e o que dizer se a rede falhar."),
        ("Pergunta à web", "Pergunta a um serviço web gratuito (Open-Meteo) sobre o ar e o sol onde estás – requests, localização e o que dizer se a rede falhar."),
        ("Pregunta a la web", "Pregunta a un servei web gratuït (Open-Meteo) per l'aire i el sol on ets – requests, ubicació i què dir si falla la xarxa."),
        ("Pregúntalle á web", "Pregúntalle a un servizo web gratuíto (Open-Meteo) polo aire e o sol onde estás – requests, localización e que dicir se falla a rede."),
        ("Galdetu sareari", "Doako web zerbitzu bati (Open-Meteo) galdetzen dio zauden lekuko aireaz eta eguzkiaz – requests, kokapena, eta sareak huts egiten duenean zer esan."),
    ]),
    "pictures": ("🖼️", "screen", [
        ("Pictures on the screen", "“Show me a dog” – shows a picture from a free web service on the device's screen (self.gui.show_image)."),
        ("Billeder på skærmen", "“Vis mig en hund” – viser et billede fra en gratis webtjeneste på enhedens skærm (self.gui.show_image)."),
        ("Bilder auf dem Bildschirm", "„Zeig mir einen Hund“ – zeigt ein Bild von einem kostenlosen Webdienst auf dem Bildschirm des Geräts (self.gui.show_image)."),
        ("Foto's op het scherm", "“Laat me een hond zien” – toont een foto van een gratis webdienst op het scherm van het apparaat (self.gui.show_image)."),
        ("Des images à l'écran", "« Montre-moi un chien » – affiche une photo d'un service web gratuit sur l'écran de l'appareil (self.gui.show_image)."),
        ("Imágenes en pantalla", "«Enséñame un perro»: muestra una foto de un servicio web gratuito en la pantalla del dispositivo (self.gui.show_image)."),
        ("Immagini sullo schermo", "«Fammi vedere un cane» – mostra una foto da un servizio web gratuito sullo schermo del dispositivo (self.gui.show_image)."),
        ("Imagens na tela", "“Me mostre um cachorro” – mostra uma foto de um serviço web gratuito na tela do dispositivo (self.gui.show_image)."),
        ("Imagens no ecrã", "“Mostra-me um cão” – mostra uma fotografia de um serviço web gratuito no ecrã do dispositivo (self.gui.show_image)."),
        ("Imatges a la pantalla", "«Ensenya'm un gos»: mostra una foto d'un servei web gratuït a la pantalla del dispositiu (self.gui.show_image)."),
        ("Imaxes na pantalla", "«Amósame un can»: amosa unha foto dun servizo web gratuíto na pantalla do dispositivo (self.gui.show_image)."),
        ("Irudiak pantailan", "«Erakutsi txakur bat»: doako web zerbitzu bateko argazki bat erakusten du gailuaren pantailan (self.gui.show_image)."),
    ]),
    "answers": ("💬", "answers", [
        ("Your own answers", "Questions and answers in a list – where the keys are, when the bins are emptied – answered when someone asks something like them (common query: no intents)."),
        ("Dine egne svar", "Spørgsmål og svar i en liste – hvor nøglerne er, hvornår skraldet hentes – besvaret, når nogen spørger om noget lignende (common query: ingen intents)."),
        ("Deine eigenen Antworten", "Fragen und Antworten in einer Liste – wo die Schlüssel sind, wann der Müll abgeholt wird – beantwortet, wenn jemand etwas Ähnliches fragt (Common Query: keine Intents)."),
        ("Je eigen antwoorden", "Vragen en antwoorden in een lijst – waar de sleutels zijn, wanneer het afval wordt opgehaald – beantwoord als iemand iets vergelijkbaars vraagt (common query: geen intents)."),
        ("Tes propres réponses", "Des questions et réponses dans une liste – où sont les clés, quand passent les poubelles – répondues quand quelqu'un demande quelque chose d'approchant (common query : pas d'intents)."),
        ("Tus propias respuestas", "Preguntas y respuestas en una lista – dónde están las llaves, cuándo pasa la basura – respondidas cuando alguien pregunta algo parecido (common query: sin intents)."),
        ("Le tue risposte", "Domande e risposte in un elenco – dove sono le chiavi, quando passa la spazzatura – risposte quando qualcuno chiede qualcosa di simile (common query: niente intent)."),
        ("Suas próprias respostas", "Perguntas e respostas numa lista – onde estão as chaves, quando o lixo é recolhido – respondidas quando alguém pergunta algo parecido (common query: sem intents)."),
        ("As tuas respostas", "Perguntas e respostas numa lista – onde estão as chaves, quando é recolhido o lixo – respondidas quando alguém pergunta algo parecido (common query: sem intents)."),
        ("Les teves respostes", "Preguntes i respostes en una llista – on són les claus, quan passen les escombraries – respostes quan algú pregunta alguna cosa semblant (common query: sense intents)."),
        ("As túas respostas", "Preguntas e respostas nunha lista – onde están as chaves, cando recollen o lixo – respondidas cando alguén pregunta algo parecido (common query: sen intents)."),
        ("Zure erantzunak", "Galderak eta erantzunak zerrenda batean – non dauden giltzak, noiz biltzen duten zaborra – norbaitek antzeko zerbait galdetzean erantzunak (common query: intent-ik gabe)."),
    ]),
    "radio": ("📻", "radio", [
        ("Your own radio", "\"Play Groove Salad\" – internet radio stations played with OpenVoiceOS' media player (OCP: a media skill)."),
        ("Din egen radio", "\"Spil Groove Salad\" – netradiostationer spillet med OpenVoiceOS' medieafspiller (OCP: en medie-skill)."),
        ("Dein eigenes Radio", "„Spiele Groove Salad“ – Internetradiosender, gespielt mit dem Mediaplayer von OpenVoiceOS (OCP: ein Medien-Skill)."),
        ("Je eigen radio", "“Speel Groove Salad” – internetradiozenders, gespeeld met de mediaspeler van OpenVoiceOS (OCP: een mediaskill)."),
        ("Ta propre radio", "« Joue Groove Salad » – des radios internet jouées avec le lecteur multimédia d'OpenVoiceOS (OCP : une skill média)."),
        ("Tu propia radio", "«Reproduce Groove Salad»: emisoras de radio por internet con el reproductor de OpenVoiceOS (OCP: una skill multimedia)."),
        ("La tua radio", "«Riproduci Groove Salad» – stazioni radio su internet con il lettore multimediale di OpenVoiceOS (OCP: una skill multimediale)."),
        ("Seu próprio rádio", "“Toque Groove Salad” – rádios da internet tocadas com o player de mídia do OpenVoiceOS (OCP: uma skill de mídia)."),
        ("O teu rádio", "“Toca Groove Salad” – rádios da internet tocadas com o leitor multimédia do OpenVoiceOS (OCP: uma skill de multimédia)."),
        ("La teva ràdio", "«Reprodueix Groove Salad»: emissores de ràdio per internet amb el reproductor de l'OpenVoiceOS (OCP: una skill multimèdia)."),
        ("A túa radio", "«Reproducir Groove Salad»: emisoras de radio por internet co reprodutor de OpenVoiceOS (OCP: unha skill multimedia)."),
        ("Zure irratia", "«Erreproduzitu Groove Salad»: interneteko irrati kateak OpenVoiceOS-en multimedia erreproduzitzailearekin (OCP: multimedia skill bat)."),
    ]),
}


def entry(tid):
    s = load_spec(tid)
    icon, short, texts = CATALOG[tid]
    sid = f"{s.NAME}.emkay-voice"
    return {
        "id": short, "kind": "skill", "icon": icon, "repo": s.REPO, "ref": "main",
        "name": {k: t[0] for k, t in zip(KEYS, texts)},
        "description": {k: t[1] for k, t in zip(KEYS, texts)},
        # the repository's address first: the skill's name is part of it
        "replace": [[s.REPO, "{{repo}}"], [sid, "{{id}}"], [s.MODULE, "{{module}}"], [s.NAME, "{{name}}"],
                    [s.CLASS, "{{Class}}"], ['authors = [{name = "emkay-voice"}]', 'authors = [{name = "{{author}}"}]']],
        "skip": [".github/workflows/make-it-yours.yml"],
    }


if __name__ == "__main__":
    path = ROOT / "templates.json"
    cat = json.loads(path.read_text())
    for tid in sys.argv[1:]:
        e = entry(tid)
        at = next((i for i, x in enumerate(cat) if x["id"] == e["id"]), None)
        if at is None:   # after the last plain skill, before the special kinds
            last = max((i for i, x in enumerate(cat) if x.get("kind") == "skill"), default=len(cat) - 1)
            cat.insert(last + 1, e)
        else:
            cat[at] = e
        print("catalog:", e["id"], e["repo"])
    path.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n")
