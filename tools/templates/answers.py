"""Template: your own answers – a common query skill answering questions from a list."""
NAME, MODULE, CLASS, REPO = "ovos-skill-answers-example", "ovos_skill_answers_example", "AnswersSkill", "emkay-voice/ovos-skill-answers-example"
SUMMARY = "Your own answers: questions and answers in a list, answered when someone asks something like them (common query)"
KEYWORDS = ["common query", "questions", "answers"]
DEPENDENCIES = []

CODE = '''
"""Your own answers: the questions and answers in locale/<language>/answers.list.

Ask "where are the spare keys?" and the skill answers "In the blue bowl in
the hall." – or anything else you write in answers.list, one line each:

    question | answer

There are no intents here. This is a common query skill: when someone asks
a question, OpenVoiceOS asks every common query skill whether it knows the
answer and how sure it is (match_common_query), and speaks the best one –
yours, Wikipedia's, or another skill's. A question that is almost like one of
yours still finds it ("where did we put the spare keys").

Try changing: the questions and answers (any number of lines), how alike a
question must be (ALIKE), or what happens when your answer is picked
(answered: it shows the answer on the screen).
"""
from difflib import SequenceMatcher

from ovos_workshop.decorators import common_query
from ovos_workshop.skills import OVOSSkill

ALIKE = 0.75   # how alike a question must be to one in answers.list, 0..1


def words(text):
    """A sentence as plain lower-case words: "Where're the keys?" -> "where re the keys"."""
    return " ".join("".join(c if c.isalnum() else " " for c in (text or "").lower()).split())


def alike(a, b):
    """How alike two questions are, 0..1."""
    return SequenceMatcher(None, words(a), words(b)).ratio()


class AnswersSkill(OVOSSkill):

    def answers(self, lang):
        """[(question, answer)] from answers.list in that language."""
        path = self.find_resource("answers.list", lang=lang)
        out = []
        for line in open(path, encoding="utf-8") if path else []:
            if "|" in line and not line.startswith("#"):
                question, answer = line.split("|", 1)
                out.append((question.strip(), answer.strip()))
        return out

    def answered(self, phrase, answer, lang):
        """Our answer was the one picked: show it on the screen too."""
        self.gui.show_text(answer, title=phrase, override_idle=15)

    @common_query(callback=answered)
    def match_common_query(self, phrase, lang):
        """Asked by OpenVoiceOS for every question: (our answer, how sure 0..1), or None."""
        best, score = None, 0.0
        for question, answer in self.answers(lang):
            s = alike(phrase, question)
            if s > score:
                best, score = answer, s
        if score < ALIKE:
            return None
        return best, min(score, 0.95)
'''

TEST = '''
def test_every_language_has_answers():
    for lang in LANGS:
        rows = [l for l in (PACKAGE / "locale" / lang / "answers.list").read_text().splitlines() if l.strip()]
        assert len(rows) >= 3 and all("|" in r for r in rows), lang


def test_alike():
    assert pkg.alike("Where are the spare keys?", "where are the spare keys") == 1
    assert pkg.alike("where did we put the spare keys", "where are the spare keys") > 0.7
    assert pkg.alike("what is the capital of france", "where are the spare keys") < 0.6
'''

L = {
"en-US": (["when is the rubbish collected | The bins are emptied every Tuesday morning.",
           "what is the wifi password | It's on the card on the fridge.",
           "where are the spare keys | In the blue bowl in the hall.",
           "who feeds the cat this week | It's Anna's turn this week.",
           "when does the corner shop close | At eight in the evening."],
          "Your own answers", "Answers your own questions – where the keys are, when the bins are emptied – from a list you write.",
          ["Where are the spare keys?", "When is the rubbish collected?"],
          ["where are the spare keys", "when is the rubbish collected"]),
"da-DK": (["hvornår bliver skraldet hentet | Skraldespandene tømmes hver tirsdag morgen.",
           "hvad er koden til wifi | Den står på kortet på køleskabet.",
           "hvor er reservenøglerne | I den blå skål i entréen.",
           "hvem fodrer katten i denne uge | Det er Annas tur i denne uge.",
           "hvornår lukker købmanden | Klokken otte om aftenen."],
          "Dine egne svar", "Svarer på dine egne spørgsmål – hvor nøglerne er, hvornår skraldet hentes – fra en liste, du selv skriver.",
          ["Hvor er reservenøglerne?", "Hvornår bliver skraldet hentet?"],
          ["hvor er reservenøglerne", "hvornår bliver skraldet hentet"]),
"de-DE": (["wann wird der müll abgeholt | Die Tonnen werden jeden Dienstagmorgen geleert.",
           "wie ist das wlan passwort | Es steht auf der Karte am Kühlschrank.",
           "wo sind die ersatzschlüssel | In der blauen Schale im Flur.",
           "wer füttert diese woche die katze | Diese Woche ist Anna dran.",
           "wann schließt der laden an der ecke | Um acht Uhr abends."],
          "Deine eigenen Antworten", "Beantwortet deine eigenen Fragen – wo die Schlüssel sind, wann der Müll abgeholt wird – aus einer Liste, die du schreibst.",
          ["Wo sind die Ersatzschlüssel?", "Wann wird der Müll abgeholt?"],
          ["wo sind die ersatzschlüssel", "wann wird der müll abgeholt"]),
"nl-NL": (["wanneer wordt het afval opgehaald | De containers worden elke dinsdagochtend geleegd.",
           "wat is het wifi wachtwoord | Het staat op het kaartje op de koelkast.",
           "waar zijn de reservesleutels | In de blauwe schaal in de gang.",
           "wie voert deze week de kat | Deze week is Anna aan de beurt.",
           "wanneer gaat de buurtwinkel dicht | Om acht uur 's avonds."],
          "Je eigen antwoorden", "Beantwoordt je eigen vragen – waar de sleutels zijn, wanneer het afval wordt opgehaald – uit een lijst die je zelf schrijft.",
          ["Waar zijn de reservesleutels?", "Wanneer wordt het afval opgehaald?"],
          ["waar zijn de reservesleutels", "wanneer wordt het afval opgehaald"]),
"fr-FR": (["quand passent les poubelles | Les poubelles sont vidées chaque mardi matin.",
           "quel est le mot de passe du wifi | Il est sur la carte sur le frigo.",
           "où sont les clés de rechange | Dans le bol bleu de l'entrée.",
           "qui nourrit le chat cette semaine | C'est le tour d'Anna cette semaine.",
           "à quelle heure ferme l'épicerie du coin | À huit heures du soir."],
          "Tes propres réponses", "Répond à tes propres questions – où sont les clés, quand passent les poubelles – à partir d'une liste que tu écris.",
          ["Où sont les clés de rechange ?", "Quand passent les poubelles ?"],
          ["où sont les clés de rechange", "quand passent les poubelles"]),
"es-ES": (["cuándo pasa la basura | Los cubos se vacían todos los martes por la mañana.",
           "cuál es la contraseña del wifi | Está en la tarjeta de la nevera.",
           "dónde están las llaves de repuesto | En el cuenco azul de la entrada.",
           "quién da de comer al gato esta semana | Esta semana le toca a Anna.",
           "a qué hora cierra la tienda de la esquina | A las ocho de la tarde."],
          "Tus propias respuestas", "Responde a tus propias preguntas – dónde están las llaves, cuándo pasa la basura – a partir de una lista que escribes tú.",
          ["¿Dónde están las llaves de repuesto?", "¿Cuándo pasa la basura?"],
          ["dónde están las llaves de repuesto", "cuándo pasa la basura"]),
"it-IT": (["quando passa la spazzatura | I bidoni vengono svuotati ogni martedì mattina.",
           "qual è la password del wifi | È sul biglietto sul frigo.",
           "dove sono le chiavi di riserva | Nella ciotola blu all'ingresso.",
           "chi dà da mangiare al gatto questa settimana | Questa settimana tocca ad Anna.",
           "a che ora chiude il negozio all'angolo | Alle otto di sera."],
          "Le tue risposte", "Risponde alle tue domande – dove sono le chiavi, quando passa la spazzatura – da un elenco che scrivi tu.",
          ["Dove sono le chiavi di riserva?", "Quando passa la spazzatura?"],
          ["dove sono le chiavi di riserva", "quando passa la spazzatura"]),
"pt-BR": (["quando o lixo é recolhido | As lixeiras são esvaziadas toda terça de manhã.",
           "qual é a senha do wifi | Está no cartão na geladeira.",
           "onde estão as chaves reserva | Na tigela azul do hall.",
           "quem dá comida ao gato esta semana | Esta semana é a vez da Anna.",
           "a que horas fecha a loja da esquina | Às oito da noite."],
          "Suas próprias respostas", "Responde às suas próprias perguntas – onde estão as chaves, quando o lixo é recolhido – a partir de uma lista que você escreve.",
          ["Onde estão as chaves reserva?", "Quando o lixo é recolhido?"],
          ["onde estão as chaves reserva", "quando o lixo é recolhido"]),
"pt-PT": (["quando é recolhido o lixo | Os caixotes são despejados todas as terças de manhã.",
           "qual é a palavra passe do wifi | Está no cartão no frigorífico.",
           "onde estão as chaves suplentes | Na taça azul da entrada.",
           "quem dá de comer ao gato esta semana | Esta semana é a vez da Anna.",
           "a que horas fecha a mercearia da esquina | Às oito da noite."],
          "As tuas respostas", "Responde às tuas próprias perguntas – onde estão as chaves, quando é recolhido o lixo – a partir de uma lista que escreves.",
          ["Onde estão as chaves suplentes?", "Quando é recolhido o lixo?"],
          ["onde estão as chaves suplentes", "quando é recolhido o lixo"]),
"ca-ES": (["quan passen a recollir les escombraries | Els contenidors es buiden cada dimarts al matí.",
           "quina és la contrasenya del wifi | És a la targeta de la nevera.",
           "on són les claus de recanvi | Al bol blau del rebedor.",
           "qui dona menjar al gat aquesta setmana | Aquesta setmana li toca a l'Anna.",
           "a quina hora tanca la botiga de la cantonada | A les vuit del vespre."],
          "Les teves respostes", "Respon a les teves preguntes – on són les claus, quan passen les escombraries – a partir d'una llista que escrius tu.",
          ["On són les claus de recanvi?", "Quan passen a recollir les escombraries?"],
          ["on són les claus de recanvi", "quan passen a recollir les escombraries"]),
"gl-ES": (["cando recollen o lixo | Os colectores baléiranse cada martes pola mañá.",
           "cal é o contrasinal da wifi | Está na tarxeta da neveira.",
           "onde están as chaves de reposto | Na cunca azul da entrada.",
           "quen lle dá de comer ao gato esta semana | Esta semana tócalle a Anna.",
           "a que hora pecha a tenda da esquina | Ás oito da tarde."],
          "As túas respostas", "Responde ás túas preguntas – onde están as chaves, cando recollen o lixo – a partir dunha lista que escribes ti.",
          ["Onde están as chaves de reposto?", "Cando recollen o lixo?"],
          ["onde están as chaves de reposto", "cando recollen o lixo"]),
"eu-ES": (["noiz biltzen dute zaborra | Edukiontziak astearte goizero husten dira.",
           "zein da wifiaren pasahitza | Hozkailuko txartelean dago.",
           "non daude ordezko giltzak | Atariko ontzi urdinean.",
           "nork ematen dio jaten katuari aste honetan | Aste honetan Annaren txanda da.",
           "noiz ixten du izkinako dendak | Arratsaldeko zortzietan."],
          "Zure erantzunak", "Zure galderak erantzuten ditu – non dauden giltzak, noiz biltzen duten zaborra – zuk idatzitako zerrenda batetik.",
          ["Non daude ordezko giltzak?", "Noiz biltzen dute zaborra?"],
          ["non daude ordezko giltzak", "noiz biltzen dute zaborra"]),
}

LOCALE = {lang: {"answers.list": "\n".join(v[0])} for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v[1], "description": v[2], "examples": v[3]} for lang, v in L.items()}
GOLDEN = {lang: [(u, None) for u in v[4]] for lang, v in L.items()}

README = '''
# Your own answers

Ask **"where are the spare keys?"** and the skill answers *"In the blue bowl in
the hall."* – or anything else you write in `answers.list`, one line each,
`question | answer` – in all twelve of [Emkay](https://emkay.ai)'s languages.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **Common query, no intents:** when someone asks a question, OpenVoiceOS asks
  every *common query* skill whether it knows the answer and how sure it is,
  and speaks the best one – yours, Wikipedia's or another skill's. Your part
  is one method: `@common_query` on `match_common_query(phrase, lang)`, which
  returns `(answer, how sure 0..1)` or `None`.
- **Almost the same question:** `alike()` compares the question with yours
  (Python's own `difflib`), so "where did we put the spare keys" finds it too.
- **When your answer is picked:** the `callback` (`answered`) runs – here it
  shows the answer on the screen.
- **Your own data per language:** `locale/<language>/answers.list`.

## Try changing

- the questions and answers – your house, your club, your class;
- `ALIKE` – how alike a question must be (lower: more questions find yours,
  and more wrong ones);
- what `answered` does – speak more, show a picture, start something.
'''
