"""Template: a quiz – the skill asks, you answer (get_response, ask_yesno)."""
NAME, MODULE, CLASS, REPO = "ovos-skill-quiz", "ovos_skill_quiz", "QuizSkill", "emkay-voice/template-quiz"
SUMMARY = "A small quiz: the skill asks questions and listens for your answers"
KEYWORDS = ["quiz", "game", "questions"]
DEPENDENCIES = []

CODE = '''
"""A small quiz: the skill asks, you answer.

Say "quiz me". The skill asks three questions from
locale/<language>/questions.list, one per line as "question | answer |
another way to say the answer", listens for your answer after each one
(get_response), says whether it was right, gives your score and asks if
you want to play again (ask_yesno).

Try changing: the questions (any number of lines), how many are asked
(ROUNDS), or what it says in right.dialog, wrong.dialog and score.dialog.

"Stop" ends a quiz: OVOS asks every skill whether it has something to stop
(can_stop) and tells the one that has (stop_session).
"""
import random

from ovos_bus_client.session import SessionManager
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

ROUNDS = 3


class QuizSkill(OVOSSkill):

    def initialize(self):
        self.playing = set()   # the sessions (devices, users) with a quiz going on

    def can_stop(self, message):
        """Asked when someone says "stop": is there a quiz to stop?"""
        return SessionManager.get(message).session_id in self.playing

    def stop_session(self, session):
        """Stop the quiz in this session; True: there was one."""
        if session.session_id in self.playing:
            self.playing.discard(session.session_id)
            return True
        return False

    def questions(self):
        """[(question, [answers])] from questions.list in the skill's language."""
        path = self.find_resource("questions.list", lang=self.lang)
        out = []
        for line in open(path, encoding="utf-8") if path else []:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and not line.startswith("#"):
                out.append((parts[0], [a.lower() for a in parts[1:] if a]))
        return out

    @staticmethod
    def is_right(reply, answers):
        """The reply says one of the answers (as a word, not inside another word)."""
        words = " " + "".join(c if c.isalnum() else " " for c in (reply or "").lower()) + " "
        return any(f" {a} " in words for a in answers)

    @intent_handler("start.intent")
    def handle_start(self, message):
        """Someone wants to play: ask, listen, keep score."""
        session = SessionManager.get(message).session_id
        self.playing.add(session)
        try:
            self.quiz(session)
        finally:
            self.playing.discard(session)

    def quiz(self, session):
        """Rounds of questions until the answer to "again?" is not yes."""
        while True:
            asked = random.sample(self.questions(), min(ROUNDS, len(self.questions())))
            self.speak_dialog("intro", {"count": len(asked)}, wait=True)
            points = 0
            for question, answers in asked:
                reply = self.get_response(question, num_retries=0)
                if session not in self.playing:   # "stop"
                    return
                if reply is None:
                    self.speak_dialog("no_answer", {"answer": answers[0]}, wait=True)
                elif self.is_right(reply, answers):
                    points += 1
                    self.speak_dialog("right", wait=True)
                else:
                    self.speak_dialog("wrong", {"answer": answers[0]}, wait=True)
            self.speak_dialog("score", {"points": points, "total": len(asked)}, wait=True)
            if self.ask_yesno("again") != "yes" or session not in self.playing:
                self.speak_dialog("bye")
                return
'''

TEST = '''
def test_every_language_has_questions():
    for lang in LANGS:
        lines = [l for l in (PACKAGE / "locale" / lang / "questions.list").read_text().splitlines() if l.strip()]
        assert len(lines) >= 3, lang
        assert all(len(l.split("|")) >= 2 for l in lines), lang


def test_right_and_wrong_answers():
    answers = ["8", "eight"]
    assert pkg.QuizSkill.is_right("I think eight", answers)
    assert pkg.QuizSkill.is_right("8", answers)
    assert not pkg.QuizSkill.is_right("eighteen", answers)
    assert not pkg.QuizSkill.is_right(None, answers)
'''

# per language: start.intent lines, questions, dialogs
L = {
"en-US": dict(
  start=["quiz me", "(give|ask) me a quiz", "i want (a|to do a) quiz", "(let's|let us) do (a|the) quiz", "ask me (some|a few) (questions|quiz questions)", "test my knowledge"],
  q=["How many legs does a spider have? | 8 | eight", "How many days are there in a week? | 7 | seven",
     "What colour do you get when you mix blue and yellow? | green", "Which is the largest planet in our solar system? | jupiter",
     "How many minutes are there in an hour? | 60 | sixty", "What do bees make? | honey"],
  intro=["Let's play! I'll ask you {count} questions.", "Quiz time – {count} questions coming up."],
  right=["That's right!", "Correct!", "Yes, well done!"],
  wrong=["Not quite – the answer is {answer}.", "Sorry, it's {answer}."],
  no_answer=["I didn't hear an answer. It's {answer}.", "No answer – it was {answer}."],
  score=["You got {points} out of {total}.", "That's {points} out of {total}."],
  again=["Do you want to play again?", "Shall we play another round?"],
  bye=["Thanks for playing!", "That was fun – see you next time."],
  name="Quiz", desc="A small quiz: it asks you questions and keeps your score.", ex=["Quiz me", "Give me a quiz"],
  gold=["quiz me", "give me a quiz", "let's do a quiz"]),
"da-DK": dict(
  start=["quiz mig", "(giv|stil) mig en quiz", "jeg vil (have|tage) en quiz", "lad os tage (en quiz|quizzen)", "stil mig (nogle|et par) spørgsmål", "test min viden"],
  q=["Hvor mange ben har en edderkop? | 8 | otte", "Hvor mange dage er der i en uge? | 7 | syv",
     "Hvilken farve får du, når du blander blå og gul? | grøn", "Hvad er den største planet i vores solsystem? | jupiter",
     "Hvor mange minutter er der i en time? | 60 | tres", "Hvad laver bier? | honning"],
  intro=["Lad os spille! Jeg stiller dig {count} spørgsmål.", "Quiztid – {count} spørgsmål kommer her."],
  right=["Det er rigtigt!", "Korrekt!", "Ja, godt klaret!"],
  wrong=["Ikke helt – svaret er {answer}.", "Desværre, det er {answer}."],
  no_answer=["Jeg hørte ikke noget svar. Det er {answer}.", "Intet svar – det var {answer}."],
  score=["Du fik {points} ud af {total}.", "Det blev {points} ud af {total}."],
  again=["Vil du spille igen?", "Skal vi tage en runde til?"],
  bye=["Tak fordi du spillede!", "Det var sjovt – vi ses."],
  name="Quiz", desc="En lille quiz: den stiller dig spørgsmål og holder styr på point.", ex=["Quiz mig", "Giv mig en quiz"],
  gold=["quiz mig", "giv mig en quiz", "lad os tage en quiz"]),
"de-DE": dict(
  start=["frag mich ab", "(gib|stell) mir ein quiz", "ich (will|möchte) ein quiz", "lass uns (ein|das) quiz machen", "stell mir (ein paar|einige) fragen", "teste mein wissen"],
  q=["Wie viele Beine hat eine Spinne? | 8 | acht", "Wie viele Tage hat eine Woche? | 7 | sieben",
     "Welche Farbe entsteht, wenn man Blau und Gelb mischt? | grün", "Welcher ist der größte Planet in unserem Sonnensystem? | jupiter",
     "Wie viele Minuten hat eine Stunde? | 60 | sechzig", "Was machen Bienen? | honig"],
  intro=["Los geht's! Ich stelle dir {count} Fragen.", "Quizzeit – {count} Fragen kommen."],
  right=["Richtig!", "Genau!", "Ja, gut gemacht!"],
  wrong=["Nicht ganz – die Antwort ist {answer}.", "Leider nein, es ist {answer}."],
  no_answer=["Ich habe keine Antwort gehört. Es ist {answer}.", "Keine Antwort – es war {answer}."],
  score=["Du hast {points} von {total}.", "Das sind {points} von {total}."],
  again=["Willst du noch einmal spielen?", "Noch eine Runde?"],
  bye=["Danke fürs Mitspielen!", "Das hat Spaß gemacht – bis zum nächsten Mal."],
  name="Quiz", desc="Ein kleines Quiz: es stellt dir Fragen und zählt deine Punkte.", ex=["Frag mich ab", "Gib mir ein Quiz"],
  gold=["frag mich ab", "gib mir ein quiz", "lass uns ein quiz machen"]),
"nl-NL": dict(
  start=["overhoor me", "geef me een quiz", "ik wil (een|de) quiz", "laten we (een|de) quiz doen", "stel me (een paar|wat) vragen", "test mijn kennis", "(doe|maak) een quiz met me"],
  q=["Hoeveel poten heeft een spin? | 8 | acht", "Hoeveel dagen heeft een week? | 7 | zeven",
     "Welke kleur krijg je als je blauw en geel mengt? | groen", "Wat is de grootste planeet in ons zonnestelsel? | jupiter",
     "Hoeveel minuten zitten er in een uur? | 60 | zestig", "Wat maken bijen? | honing"],
  intro=["Daar gaan we! Ik stel je {count} vragen.", "Quiztijd – {count} vragen komen eraan."],
  right=["Dat klopt!", "Goed zo!", "Ja, prima!"],
  wrong=["Niet helemaal – het antwoord is {answer}.", "Helaas, het is {answer}."],
  no_answer=["Ik hoorde geen antwoord. Het is {answer}.", "Geen antwoord – het was {answer}."],
  score=["Je hebt er {points} van de {total} goed.", "Dat is {points} van de {total}."],
  again=["Wil je nog een keer spelen?", "Zullen we nog een ronde spelen?"],
  bye=["Bedankt voor het spelen!", "Dat was leuk – tot de volgende keer."],
  name="Quiz", desc="Een kleine quiz: hij stelt je vragen en houdt je score bij.", ex=["Overhoor me", "Geef me een quiz"],
  gold=["overhoor me", "geef me een quiz", "laten we een quiz doen"]),
"fr-FR": dict(
  start=["interroge moi", "(fais|propose) moi un quiz", "je veux (un|faire un) quiz", "faisons (un|le) quiz", "pose moi (quelques|des) questions", "teste mes connaissances"],
  q=["Combien de pattes a une araignée ? | 8 | huit", "Combien de jours y a-t-il dans une semaine ? | 7 | sept",
     "Quelle couleur obtient-on en mélangeant du bleu et du jaune ? | vert", "Quelle est la plus grande planète de notre système solaire ? | jupiter",
     "Combien de minutes y a-t-il dans une heure ? | 60 | soixante", "Que fabriquent les abeilles ? | miel | du miel"],
  intro=["C'est parti ! Je vais te poser {count} questions.", "C'est l'heure du quiz – {count} questions arrivent."],
  right=["C'est juste !", "Bonne réponse !", "Oui, bravo !"],
  wrong=["Pas tout à fait – la réponse est {answer}.", "Dommage, c'est {answer}."],
  no_answer=["Je n'ai pas entendu de réponse. C'est {answer}.", "Pas de réponse – c'était {answer}."],
  score=["Tu as {points} sur {total}.", "Ça fait {points} sur {total}."],
  again=["Tu veux rejouer ?", "On refait une partie ?"],
  bye=["Merci d'avoir joué !", "C'était amusant – à la prochaine."],
  name="Quiz", desc="Un petit quiz : il te pose des questions et compte tes points.", ex=["Interroge-moi", "Fais-moi un quiz"],
  gold=["interroge moi", "fais moi un quiz", "faisons un quiz"]),
"es-ES": dict(
  start=["hazme un (examen|concurso)", "quiero (un|hacer un) concurso", "hagamos (un|el) concurso", "hazme (unas|algunas) preguntas", "pon a prueba mis conocimientos", "pregúntame algo"],
  q=["¿Cuántas patas tiene una araña? | 8 | ocho", "¿Cuántos días tiene una semana? | 7 | siete",
     "¿Qué color sale al mezclar azul y amarillo? | verde", "¿Cuál es el planeta más grande de nuestro sistema solar? | júpiter | jupiter",
     "¿Cuántos minutos tiene una hora? | 60 | sesenta", "¿Qué hacen las abejas? | miel"],
  intro=["¡Vamos a jugar! Te haré {count} preguntas.", "Hora del concurso: vienen {count} preguntas."],
  right=["¡Correcto!", "¡Eso es!", "¡Sí, muy bien!"],
  wrong=["No exactamente: la respuesta es {answer}.", "Lo siento, es {answer}."],
  no_answer=["No he oído ninguna respuesta. Es {answer}.", "Sin respuesta: era {answer}."],
  score=["Has acertado {points} de {total}.", "Son {points} de {total}."],
  again=["¿Quieres jugar otra vez?", "¿Jugamos otra ronda?"],
  bye=["¡Gracias por jugar!", "Ha sido divertido, hasta la próxima."],
  name="Concurso", desc="Un pequeño concurso: te hace preguntas y lleva la cuenta de tus puntos.", ex=["Hazme un concurso", "Hazme unas preguntas"],
  gold=["hazme un concurso", "hagamos un concurso", "hazme unas preguntas"]),
"it-IT": dict(
  start=["interrogami", "(fammi|proponimi) un quiz", "voglio (un|fare un) quiz", "facciamo (un|il) quiz", "fammi (qualche|alcune) domande", "verifica le mie conoscenze"],
  q=["Quante zampe ha un ragno? | 8 | otto", "Quanti giorni ci sono in una settimana? | 7 | sette",
     "Che colore ottieni mescolando blu e giallo? | verde", "Qual è il pianeta più grande del nostro sistema solare? | giove",
     "Quanti minuti ci sono in un'ora? | 60 | sessanta", "Che cosa fanno le api? | miele | il miele"],
  intro=["Giochiamo! Ti farò {count} domande.", "È l'ora del quiz: arrivano {count} domande."],
  right=["Esatto!", "Giusto!", "Sì, bravo!"],
  wrong=["Non proprio: la risposta è {answer}.", "Mi dispiace, è {answer}."],
  no_answer=["Non ho sentito una risposta. È {answer}.", "Nessuna risposta: era {answer}."],
  score=["Hai fatto {points} su {total}.", "Sono {points} su {total}."],
  again=["Vuoi giocare di nuovo?", "Facciamo un'altra partita?"],
  bye=["Grazie per aver giocato!", "È stato divertente, alla prossima."],
  name="Quiz", desc="Un piccolo quiz: ti fa domande e tiene il punteggio.", ex=["Interrogami", "Fammi un quiz"],
  gold=["interrogami", "fammi un quiz", "facciamo un quiz"]),
"pt-BR": dict(
  start=["me faça um (teste|quiz)", "quero (um|fazer um) quiz", "vamos fazer (um|o) quiz", "me faça (umas|algumas) perguntas", "teste meus conhecimentos", "me pergunte algo"],
  q=["Quantas patas tem uma aranha? | 8 | oito", "Quantos dias tem uma semana? | 7 | sete",
     "Que cor você obtém misturando azul e amarelo? | verde", "Qual é o maior planeta do nosso sistema solar? | júpiter | jupiter",
     "Quantos minutos tem uma hora? | 60 | sessenta", "O que as abelhas fazem? | mel"],
  intro=["Vamos jogar! Vou fazer {count} perguntas.", "Hora do quiz: lá vêm {count} perguntas."],
  right=["Certo!", "Isso mesmo!", "Sim, muito bem!"],
  wrong=["Não exatamente: a resposta é {answer}.", "Que pena, é {answer}."],
  no_answer=["Não ouvi uma resposta. É {answer}.", "Sem resposta: era {answer}."],
  score=["Você acertou {points} de {total}.", "Foram {points} de {total}."],
  again=["Quer jogar de novo?", "Vamos jogar mais uma rodada?"],
  bye=["Obrigado por jogar!", "Foi divertido, até a próxima."],
  name="Quiz", desc="Um pequeno quiz: ele faz perguntas e conta seus pontos.", ex=["Me faça um quiz", "Me faça umas perguntas"],
  gold=["me faça um quiz", "vamos fazer um quiz", "me faça umas perguntas"]),
"pt-PT": dict(
  start=["faz-me um (teste|quiz)", "quero (um|fazer um) quiz", "vamos fazer (um|o) quiz", "faz-me (umas|algumas) perguntas", "testa os meus conhecimentos", "pergunta-me algo"],
  q=["Quantas patas tem uma aranha? | 8 | oito", "Quantos dias tem uma semana? | 7 | sete",
     "Que cor se obtém ao misturar azul e amarelo? | verde", "Qual é o maior planeta do nosso sistema solar? | júpiter | jupiter",
     "Quantos minutos tem uma hora? | 60 | sessenta", "O que fazem as abelhas? | mel"],
  intro=["Vamos jogar! Vou fazer-te {count} perguntas.", "Hora do quiz: aí vêm {count} perguntas."],
  right=["Certo!", "Isso mesmo!", "Sim, muito bem!"],
  wrong=["Não exatamente: a resposta é {answer}.", "Que pena, é {answer}."],
  no_answer=["Não ouvi uma resposta. É {answer}.", "Sem resposta: era {answer}."],
  score=["Acertaste {points} de {total}.", "Foram {points} de {total}."],
  again=["Queres jogar outra vez?", "Jogamos mais uma ronda?"],
  bye=["Obrigado por jogares!", "Foi divertido, até à próxima."],
  name="Quiz", desc="Um pequeno quiz: faz perguntas e conta os teus pontos.", ex=["Faz-me um quiz", "Faz-me umas perguntas"],
  gold=["faz-me um quiz", "vamos fazer um quiz", "faz-me umas perguntas"]),
"ca-ES": dict(
  start=["fes-me un (examen|concurs)", "vull (un|fer un) concurs", "fem (un|el) concurs", "fes-me (unes|algunes) preguntes", "comprova els meus coneixements", "pregunta'm alguna cosa"],
  q=["Quantes potes té una aranya? | 8 | vuit", "Quants dies té una setmana? | 7 | set",
     "Quin color surt si barreges blau i groc? | verd", "Quin és el planeta més gran del nostre sistema solar? | júpiter | jupiter",
     "Quants minuts té una hora? | 60 | seixanta", "Què fan les abelles? | mel"],
  intro=["Som-hi! Et faré {count} preguntes.", "Hora del concurs: arriben {count} preguntes."],
  right=["Correcte!", "Això mateix!", "Sí, molt bé!"],
  wrong=["No del tot: la resposta és {answer}.", "Ho sento, és {answer}."],
  no_answer=["No he sentit cap resposta. És {answer}.", "Cap resposta: era {answer}."],
  score=["N'has encertat {points} de {total}.", "Són {points} de {total}."],
  again=["Vols tornar a jugar?", "Fem una altra partida?"],
  bye=["Gràcies per jugar!", "Ha estat divertit, fins a la propera."],
  name="Concurs", desc="Un petit concurs: et fa preguntes i compta els teus punts.", ex=["Fes-me un concurs", "Fes-me unes preguntes"],
  gold=["fes-me un concurs", "fem un concurs", "fes-me unes preguntes"]),
"gl-ES": dict(
  start=["faime un (exame|concurso)", "quero (un|facer un) concurso", "fagamos (un|o) concurso", "faime (unhas|algunhas) preguntas", "pon a proba os meus coñecementos", "pregúntame algo"],
  q=["Cantas patas ten unha araña? | 8 | oito", "Cantos días ten unha semana? | 7 | sete",
     "Que cor sae se mesturas azul e amarelo? | verde", "Cal é o planeta máis grande do noso sistema solar? | xúpiter | xupiter",
     "Cantos minutos ten unha hora? | 60 | sesenta", "Que fan as abellas? | mel"],
  intro=["Imos xogar! Fareiche {count} preguntas.", "Hora do concurso: chegan {count} preguntas."],
  right=["Correcto!", "Iso é!", "Si, moi ben!"],
  wrong=["Non exactamente: a resposta é {answer}.", "Síntoo, é {answer}."],
  no_answer=["Non oín ningunha resposta. É {answer}.", "Sen resposta: era {answer}."],
  score=["Acertaches {points} de {total}.", "Son {points} de {total}."],
  again=["Queres xogar outra vez?", "Facemos outra rolda?"],
  bye=["Grazas por xogar!", "Foi divertido, ata a próxima."],
  name="Concurso", desc="Un pequeno concurso: faiche preguntas e leva a conta dos teus puntos.", ex=["Faime un concurso", "Faime unhas preguntas"],
  gold=["faime un concurso", "fagamos un concurso", "faime unhas preguntas"]),
"eu-ES": dict(
  start=["azter nazazu", "egin (galdetegi|lehiaketa) bat", "(galdetegi|lehiaketa) bat nahi dut", "egin dezagun (galdetegi|lehiaketa) bat", "egin (galdera batzuk|zenbait galdera)", "jarri proban nire jakintza"],
  q=["Zenbat hanka ditu armiarma batek? | 8 | zortzi", "Zenbat egun ditu aste batek? | 7 | zazpi",
     "Zer kolore lortzen da urdina eta horia nahastuta? | berdea | berde", "Zein da gure eguzki-sistemako planetarik handiena? | jupiter",
     "Zenbat minutu ditu ordu batek? | 60 | hirurogei", "Zer egiten dute erleek? | eztia | ezti"],
  intro=["Jokatu dezagun! {count} galdera egingo dizkizut.", "Galdetegiaren ordua: {count} galdera datoz."],
  right=["Zuzena!", "Hori da!", "Bai, oso ondo!"],
  wrong=["Ez guztiz: erantzuna {answer} da.", "Sentitzen dut, {answer} da."],
  no_answer=["Ez dut erantzunik entzun. {answer} da.", "Erantzunik ez: {answer} zen."],
  score=["{total}tik {points} asmatu dituzu.", "{total}tik {points} dira."],
  again=["Berriro jokatu nahi duzu?", "Beste txanda bat jokatuko dugu?"],
  bye=["Eskerrik asko jokatzeagatik!", "Dibertigarria izan da, hurrengora arte."],
  name="Galdetegia", desc="Galdetegi txiki bat: galderak egiten dizkizu eta puntuak zenbatzen ditu.", ex=["Egin galdetegi bat", "Egin galdera batzuk"],
  gold=["azter nazazu", "egin galdetegi bat", "egin galdera batzuk"]),
}

LOCALE = {lang: {"start.intent": "\n".join(v["start"]), "questions.list": "\n".join(v["q"]),
                 **{f"{k}.dialog": "\n".join(v[k]) for k in ("intro", "right", "wrong", "no_answer", "score", "again", "bye")}}
          for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v["name"], "description": v["desc"], "examples": v["ex"]} for lang, v in L.items()}
GOLDEN = {lang: [(u, "start.intent") for u in v["gold"]] for lang, v in L.items()}

README = '''
# A quiz skill

The skill asks, you answer: say **"quiz me"**, and it asks three
questions, listens for your answer after each one, tells you whether you were
right, gives your score and asks whether you want to play again – in all
twelve of [Emkay](https://emkay.ai)'s languages.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **Asking back:** `self.get_response(question)` speaks the question and waits
  for the next thing you say; `self.ask_yesno("again")` does the same and
  turns the answer into `"yes"`, `"no"` or `None`.
- **Your own data per language:** the questions are in
  `locale/<language>/questions.list`, one per line:
  `question | answer | another way to say it`. `self.find_resource()` finds
  the file for the language Emkay speaks.
- **Stopping:** say "stop" during a quiz and it ends. `can_stop()` tells OVOS
  there is something to stop, `stop_session()` stops it – in the session
  (device) where the quiz is going on, not on every device at once.
- **Dialogs with values:** `{count}`, `{answer}`, `{points}` and `{total}` in
  the `.dialog` files are filled in by `speak_dialog(name, {...})`.

## Why not "start the quiz"?

OVOS' media player (OCP) claims every sentence that begins with *play …* or
*start …* (in Danish also *spil …*), and it is asked before ordinary skills –
"start the quiz" would look for a quiz to play as music. So the sentences in
`start.intent` begin with other words. The golden utterances in
`test/end2end/` are how you find out: a test that says `got ocp:play` means a
sentence was taken by the media player.

## Try changing

- the questions – add your own, any number of lines;
- `ROUNDS` in `__init__.py` – how many it asks;
- what it says when you are right (`right.dialog`) – one line is picked at random.
'''
