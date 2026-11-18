"""Template: ask the web – air quality and UV from Open-Meteo (no key needed)."""
NAME, MODULE, CLASS, REPO = "ovos-skill-air-quality", "ovos_skill_air_quality", "AirQualitySkill", "emkay-voice/template-web"
SUMMARY = "Asks a web service (Open-Meteo) how clean the air is and how strong the sun is where you are"
KEYWORDS = ["air quality", "uv", "open-meteo", "web api"]
DEPENDENCIES = ["requests"]

CODE = '''
"""Ask the web: how clean is the air, how strong is the sun?

Say "how is the air quality". The skill takes where the device is (Settings
→ location), asks Open-Meteo's free air-quality service – no account, no key
– and says the answer: https://open-meteo.com/en/docs/air-quality-api

Try changing: what is asked for (CURRENT, see the page above for more, e.g.
pollen in Europe), the words for each level (levels.list), or add a third
intent for something else the service knows.
"""
import requests

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CURRENT = "european_aqi,uv_index"
AIR_LEVELS = (20, 40, 60, 80, 100)   # European AQI: good ... extremely poor
UV_LEVELS = (3, 6, 8, 11)            # UV index: low ... extreme


def level(value, limits):
    """Which band value is in: 0 below limits[0], 1 below limits[1], ..."""
    return sum(value >= limit for limit in limits)


class AirQualitySkill(OVOSSkill):

    def where(self):
        """(latitude, longitude, place name) of the device, or None."""
        coord = (self.location or {}).get("coordinate") or {}
        if "latitude" not in coord:
            return None
        return coord["latitude"], coord["longitude"], self.location_pretty or ""

    def now(self):
        """What the service says right now, as a dict – or None (and says why)."""
        where = self.where()
        if not where:
            self.speak_dialog("no_location")
            return None
        lat, lon, _ = where
        try:
            r = requests.get(URL, params={"latitude": lat, "longitude": lon, "current": CURRENT}, timeout=10)
            r.raise_for_status()
            return r.json()["current"]
        except Exception as e:
            self.log.warning(f"Open-Meteo did not answer: {e}")
            self.speak_dialog("no_connection")
            return None

    def words(self, name, index):
        """Line `index` of locale/<language>/<name>.list: the word for a level."""
        path = self.find_resource(f"{name}.list", lang=self.lang)
        lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
        return lines[min(index, len(lines) - 1)]

    @intent_handler("air.intent")
    def handle_air(self, message):
        now = self.now()
        if now and now.get("european_aqi") is not None:
            aqi = round(now["european_aqi"])
            self.speak_dialog("air_now", {"place": self.where()[2], "index": aqi,
                                      "level": self.words("air_levels", level(aqi, AIR_LEVELS))})

    @intent_handler("uv.intent")
    def handle_uv(self, message):
        now = self.now()
        if now and now.get("uv_index") is not None:
            uv = round(now["uv_index"])
            self.speak_dialog("uv_now", {"index": uv, "level": self.words("uv_levels", level(uv, UV_LEVELS))})
'''

TEST = '''
def test_levels():
    assert pkg.level(5, pkg.AIR_LEVELS) == 0
    assert pkg.level(45, pkg.AIR_LEVELS) == 2
    assert pkg.level(150, pkg.AIR_LEVELS) == 5
    assert pkg.level(0, pkg.UV_LEVELS) == 0
    assert pkg.level(11, pkg.UV_LEVELS) == 4


def test_every_language_has_a_word_for_every_level():
    for lang in LANGS:
        loc = PACKAGE / "locale" / lang
        assert len([l for l in (loc / "air_levels.list").read_text().splitlines() if l.strip()]) == 6, lang
        assert len([l for l in (loc / "uv_levels.list").read_text().splitlines() if l.strip()]) == 5, lang
'''

L = {
"en-US": dict(
  air=["how is the air (quality|today)", "what is the air quality (here|today|outside)", "is the air (clean|good) (today|outside)", "(check|tell me) the air quality"],
  uv=["what is the uv index (today|now)", "(how strong|how high) is the uv (today|now)", "is the (sun|uv) strong (today|now)", "how strong is the sun (today|now)"],
  air_levels="good\nfair\nmoderate\npoor\nvery poor\nextremely poor",
  uv_levels="low\nmoderate\nhigh\nvery high\nextreme",
  airD=["The air in {place} is {level} right now, with a European air quality index of {index}.", "Right now the air quality in {place} is {level}, index {index}."],
  uvD=["The UV index is {index} right now, which is {level}.", "Right now the UV index is {index} – {level}."],
  no_location=["I don't know where this device is. Set the location in Settings first.", "Tell me where you are in Settings, then ask again."],
  no_connection=["I couldn't reach the air quality service. Try again in a moment.", "The air quality service didn't answer."],
  name="Air quality", desc="Asks a free web service how clean the air is and how strong the sun is where you are.",
  ex=["How is the air quality?", "What is the UV index today?"],
  gold=[("how is the air quality", "air"), ("is the air clean today", "air"), ("what is the uv index today", "uv"), ("is the sun strong today", "uv")]),
"da-DK": dict(
  air=["hvordan er luften (i dag|udenfor)", "hvordan er luftkvaliteten (her|i dag|udenfor)", "er luften (ren|god) (i dag|udenfor)", "(tjek|fortæl mig) luftkvaliteten", "hvordan er luftkvaliteten"],
  uv=["hvad er uv indekset (i dag|nu)", "(hvor stærkt|hvor højt) er uv indekset (i dag|nu)", "er (solen|uv) stærk (i dag|nu)", "hvor stærk er solen (i dag|nu)"],
  air_levels="god\nrimelig\nmiddel\ndårlig\nmeget dårlig\nekstremt dårlig",
  uv_levels="lavt\nmoderat\nhøjt\nmeget højt\nekstremt",
  airD=["Luften i {place} er {level} lige nu, med et europæisk luftkvalitetsindeks på {index}.", "Lige nu er luftkvaliteten i {place} {level}, indeks {index}."],
  uvD=["UV-indekset er {index} lige nu, og det er {level}.", "Lige nu er UV-indekset {index} – {level}."],
  no_location=["Jeg ved ikke, hvor enheden er. Indstil placeringen i Indstillinger først.", "Fortæl mig, hvor du er, i Indstillinger, og spørg så igen."],
  no_connection=["Jeg kunne ikke få fat i luftkvalitetstjenesten. Prøv igen om lidt.", "Luftkvalitetstjenesten svarede ikke."],
  name="Luftkvalitet", desc="Spørger en gratis webtjeneste, hvor ren luften er, og hvor stærk solen er, der hvor du er.",
  ex=["Hvordan er luftkvaliteten?", "Hvad er UV-indekset i dag?"],
  gold=[("hvordan er luftkvaliteten", "air"), ("er luften ren i dag", "air"), ("hvad er uv indekset i dag", "uv"), ("er solen stærk i dag", "uv")]),
"de-DE": dict(
  air=["wie ist die luft (heute|draußen)", "wie ist die luftqualität (hier|heute|draußen)", "ist die luft (sauber|gut) (heute|draußen)", "(prüfe|sag mir) die luftqualität", "wie ist die luftqualität"],
  uv=["wie hoch ist der uv index (heute|jetzt)", "(wie stark|wie hoch) ist die uv strahlung (heute|jetzt)", "ist die (sonne|uv strahlung) stark (heute|jetzt)", "wie stark ist die sonne (heute|jetzt)"],
  air_levels="gut\nmäßig\nmittel\nschlecht\nsehr schlecht\nextrem schlecht",
  uv_levels="niedrig\nmäßig\nhoch\nsehr hoch\nextrem",
  airD=["Die Luft in {place} ist gerade {level}, mit einem europäischen Luftqualitätsindex von {index}.", "Gerade ist die Luftqualität in {place} {level}, Index {index}."],
  uvD=["Der UV-Index liegt gerade bei {index}, das ist {level}.", "Gerade ist der UV-Index {index} – {level}."],
  no_location=["Ich weiß nicht, wo dieses Gerät ist. Stell zuerst den Standort in den Einstellungen ein.", "Sag mir in den Einstellungen, wo du bist, und frag dann noch einmal."],
  no_connection=["Ich habe den Luftqualitätsdienst nicht erreicht. Versuch es gleich noch einmal.", "Der Luftqualitätsdienst hat nicht geantwortet."],
  name="Luftqualität", desc="Fragt einen kostenlosen Webdienst, wie sauber die Luft ist und wie stark die Sonne, wo du bist.",
  ex=["Wie ist die Luftqualität?", "Wie hoch ist der UV-Index heute?"],
  gold=[("wie ist die luftqualität", "air"), ("ist die luft sauber heute", "air"), ("wie hoch ist der uv index heute", "uv"), ("wie stark ist die sonne heute", "uv")]),
"nl-NL": dict(
  air=["hoe is de lucht (vandaag|buiten)", "hoe is de luchtkwaliteit (hier|vandaag|buiten)", "is de lucht (schoon|goed) (vandaag|buiten)", "(controleer|vertel me) de luchtkwaliteit", "hoe is de luchtkwaliteit"],
  uv=["wat is de uv index (vandaag|nu)", "(hoe sterk|hoe hoog) is de uv straling (vandaag|nu)", "is de (zon|uv straling) sterk (vandaag|nu)", "hoe sterk is de zon (vandaag|nu)"],
  air_levels="goed\nredelijk\nmatig\nslecht\nzeer slecht\nextreem slecht",
  uv_levels="laag\nmatig\nhoog\nzeer hoog\nextreem",
  airD=["De lucht in {place} is nu {level}, met een Europese luchtkwaliteitsindex van {index}.", "Op dit moment is de luchtkwaliteit in {place} {level}, index {index}."],
  uvD=["De UV-index is nu {index}, dat is {level}.", "Op dit moment is de UV-index {index} – {level}."],
  no_location=["Ik weet niet waar dit apparaat is. Stel eerst de locatie in bij Instellingen.", "Vertel me bij Instellingen waar je bent en vraag het dan opnieuw."],
  no_connection=["Ik kon de luchtkwaliteitsdienst niet bereiken. Probeer het zo nog eens.", "De luchtkwaliteitsdienst gaf geen antwoord."],
  name="Luchtkwaliteit", desc="Vraagt een gratis webdienst hoe schoon de lucht is en hoe sterk de zon is waar je bent.",
  ex=["Hoe is de luchtkwaliteit?", "Wat is de UV-index vandaag?"],
  gold=[("hoe is de luchtkwaliteit", "air"), ("is de lucht schoon vandaag", "air"), ("wat is de uv index vandaag", "uv"), ("hoe sterk is de zon vandaag", "uv")]),
"fr-FR": dict(
  air=["comment est l'air (aujourd'hui|dehors)", "quelle est la qualité de l'air (ici|aujourd'hui|dehors)", "est ce que l'air est (pur|bon) (aujourd'hui|dehors)", "(vérifie|dis moi) la qualité de l'air", "quelle est la qualité de l'air"],
  uv=["quel est l'indice uv (aujourd'hui|maintenant)", "(quelle est la force|quel est le niveau) des uv (aujourd'hui|maintenant)", "est ce que le (soleil|rayonnement uv) est fort (aujourd'hui|maintenant)", "le soleil est il fort (aujourd'hui|maintenant)"],
  air_levels="bonne\nmoyenne\nmodérée\nmauvaise\ntrès mauvaise\nextrêmement mauvaise",
  uv_levels="faible\nmodéré\nélevé\ntrès élevé\nextrême",
  airD=["La qualité de l'air à {place} est {level} en ce moment, avec un indice européen de {index}.", "En ce moment, la qualité de l'air à {place} est {level}, indice {index}."],
  uvD=["L'indice UV est de {index} en ce moment, c'est {level}.", "En ce moment l'indice UV est de {index} : {level}."],
  no_location=["Je ne sais pas où se trouve cet appareil. Indique d'abord le lieu dans les Réglages.", "Dis-moi où tu es dans les Réglages, puis redemande."],
  no_connection=["Je n'ai pas pu joindre le service de qualité de l'air. Réessaie dans un instant.", "Le service de qualité de l'air n'a pas répondu."],
  name="Qualité de l'air", desc="Demande à un service web gratuit si l'air est pur et si le soleil est fort là où tu es.",
  ex=["Quelle est la qualité de l'air ?", "Quel est l'indice UV aujourd'hui ?"],
  gold=[("quelle est la qualité de l'air", "air"), ("comment est l'air aujourd'hui", "air"), ("quel est l'indice uv aujourd'hui", "uv"), ("le soleil est il fort aujourd'hui", "uv")]),
"es-ES": dict(
  air=["cómo está el aire (hoy|fuera)", "cuál es la calidad del aire (aquí|hoy|fuera)", "está el aire (limpio|bien) (hoy|fuera)", "(comprueba|dime) la calidad del aire", "cuál es la calidad del aire"],
  uv=["cuál es el índice uv (hoy|ahora)", "(qué tan fuerte|qué tan alta) es la radiación uv (hoy|ahora)", "está (fuerte el sol|alta la radiación uv) (hoy|ahora)", "qué tan fuerte está el sol (hoy|ahora)"],
  air_levels="buena\nrazonable\nregular\nmala\nmuy mala\nextremadamente mala",
  uv_levels="bajo\nmoderado\nalto\nmuy alto\nextremo",
  airD=["La calidad del aire en {place} es {level} ahora mismo, con un índice europeo de {index}.", "Ahora mismo la calidad del aire en {place} es {level}, índice {index}."],
  uvD=["El índice UV es {index} ahora mismo, es decir, {level}.", "Ahora mismo el índice UV es {index}: {level}."],
  no_location=["No sé dónde está este dispositivo. Indica primero la ubicación en Ajustes.", "Dime dónde estás en Ajustes y vuelve a preguntar."],
  no_connection=["No he podido contactar con el servicio de calidad del aire. Inténtalo de nuevo en un momento.", "El servicio de calidad del aire no ha respondido."],
  name="Calidad del aire", desc="Pregunta a un servicio web gratuito lo limpio que está el aire y lo fuerte que está el sol donde estás.",
  ex=["¿Cuál es la calidad del aire?", "¿Cuál es el índice UV hoy?"],
  gold=[("cuál es la calidad del aire", "air"), ("está el aire limpio hoy", "air"), ("cuál es el índice uv hoy", "uv"), ("qué tan fuerte está el sol hoy", "uv")]),
"it-IT": dict(
  air=["com'è l'aria (oggi|fuori)", "qual è la qualità dell'aria (qui|oggi|fuori)", "l'aria è (pulita|buona) (oggi|fuori)", "(controlla|dimmi) la qualità dell'aria", "qual è la qualità dell'aria"],
  uv=["qual è l'indice uv (oggi|adesso)", "(quanto è forte|quanto è alta) la radiazione uv (oggi|adesso)", "il (sole|raggio uv) è forte (oggi|adesso)", "quanto è forte il sole (oggi|adesso)"],
  air_levels="buona\ndiscreta\nmoderata\nscarsa\nmolto scarsa\nestremamente scarsa",
  uv_levels="basso\nmoderato\nalto\nmolto alto\nestremo",
  airD=["L'aria a {place} adesso è {level}, con un indice europeo di qualità dell'aria di {index}.", "In questo momento la qualità dell'aria a {place} è {level}, indice {index}."],
  uvD=["L'indice UV adesso è {index}, cioè {level}.", "In questo momento l'indice UV è {index}: {level}."],
  no_location=["Non so dove si trova questo dispositivo. Imposta prima la posizione nelle Impostazioni.", "Dimmi dove sei nelle Impostazioni, poi chiedi di nuovo."],
  no_connection=["Non sono riuscito a raggiungere il servizio sulla qualità dell'aria. Riprova tra poco.", "Il servizio sulla qualità dell'aria non ha risposto."],
  name="Qualità dell'aria", desc="Chiede a un servizio web gratuito quanto è pulita l'aria e quanto è forte il sole dove sei.",
  ex=["Qual è la qualità dell'aria?", "Qual è l'indice UV oggi?"],
  gold=[("qual è la qualità dell'aria", "air"), ("l'aria è pulita oggi", "air"), ("qual è l'indice uv oggi", "uv"), ("quanto è forte il sole oggi", "uv")]),
"pt-BR": dict(
  air=["como está o ar (hoje|lá fora)", "qual é a qualidade do ar (aqui|hoje|lá fora)", "o ar está (limpo|bom) (hoje|lá fora)", "(verifique|me diga) a qualidade do ar", "qual é a qualidade do ar"],
  uv=["qual é o índice uv (hoje|agora)", "(quão forte|quão alta) está a radiação uv (hoje|agora)", "o (sol|uv) está forte (hoje|agora)", "quão forte está o sol (hoje|agora)"],
  air_levels="boa\nrazoável\nmoderada\nruim\nmuito ruim\nextremamente ruim",
  uv_levels="baixo\nmoderado\nalto\nmuito alto\nextremo",
  airD=["O ar em {place} está {level} agora, com um índice europeu de qualidade do ar de {index}.", "Agora a qualidade do ar em {place} está {level}, índice {index}."],
  uvD=["O índice UV está em {index} agora, o que é {level}.", "Agora o índice UV é {index}: {level}."],
  no_location=["Não sei onde este dispositivo está. Defina a localização nas Configurações primeiro.", "Diga onde você está nas Configurações e pergunte de novo."],
  no_connection=["Não consegui falar com o serviço de qualidade do ar. Tente de novo daqui a pouco.", "O serviço de qualidade do ar não respondeu."],
  name="Qualidade do ar", desc="Pergunta a um serviço web gratuito o quão limpo está o ar e o quão forte está o sol onde você está.",
  ex=["Qual é a qualidade do ar?", "Qual é o índice UV hoje?"],
  gold=[("qual é a qualidade do ar", "air"), ("o ar está limpo hoje", "air"), ("qual é o índice uv hoje", "uv"), ("quão forte está o sol hoje", "uv")]),
"pt-PT": dict(
  air=["como está o ar (hoje|lá fora)", "qual é a qualidade do ar (aqui|hoje|lá fora)", "o ar está (limpo|bom) (hoje|lá fora)", "(verifica|diz-me) a qualidade do ar", "qual é a qualidade do ar"],
  uv=["qual é o índice uv (hoje|agora)", "(quão forte|quão alta) está a radiação uv (hoje|agora)", "o (sol|uv) está forte (hoje|agora)", "quão forte está o sol (hoje|agora)"],
  air_levels="boa\nrazoável\nmoderada\nmá\nmuito má\nextremamente má",
  uv_levels="baixo\nmoderado\nelevado\nmuito elevado\nextremo",
  airD=["O ar em {place} está {level} neste momento, com um índice europeu de qualidade do ar de {index}.", "Neste momento a qualidade do ar em {place} está {level}, índice {index}."],
  uvD=["O índice UV está em {index} neste momento, o que é {level}.", "Neste momento o índice UV é {index}: {level}."],
  no_location=["Não sei onde está este dispositivo. Define primeiro a localização nas Definições.", "Diz-me onde estás nas Definições e pergunta outra vez."],
  no_connection=["Não consegui contactar o serviço de qualidade do ar. Tenta outra vez daqui a pouco.", "O serviço de qualidade do ar não respondeu."],
  name="Qualidade do ar", desc="Pergunta a um serviço web gratuito quão limpo está o ar e quão forte está o sol onde estás.",
  ex=["Qual é a qualidade do ar?", "Qual é o índice UV hoje?"],
  gold=[("qual é a qualidade do ar", "air"), ("o ar está limpo hoje", "air"), ("qual é o índice uv hoje", "uv"), ("quão forte está o sol hoje", "uv")]),
"ca-ES": dict(
  air=["com està l'aire (avui|a fora)", "quina és la qualitat de l'aire (aquí|avui|a fora)", "l'aire està (net|bé) (avui|a fora)", "(comprova|digues-me) la qualitat de l'aire", "quina és la qualitat de l'aire"],
  uv=["quin és l'índex uv (avui|ara)", "(com de forta|com d'alta) és la radiació uv (avui|ara)", "el (sol|uv) és fort (avui|ara)", "com de fort és el sol (avui|ara)"],
  air_levels="bona\nraonable\nmoderada\ndolenta\nmolt dolenta\nextremadament dolenta",
  uv_levels="baix\nmoderat\nalt\nmolt alt\nextrem",
  airD=["L'aire a {place} ara és {level}, amb un índex europeu de qualitat de l'aire de {index}.", "Ara mateix la qualitat de l'aire a {place} és {level}, índex {index}."],
  uvD=["L'índex UV ara és {index}, és a dir, {level}.", "Ara mateix l'índex UV és {index}: {level}."],
  no_location=["No sé on és aquest dispositiu. Indica primer la ubicació a Configuració.", "Digues-me on ets a Configuració i torna a preguntar."],
  no_connection=["No he pogut contactar amb el servei de qualitat de l'aire. Torna-ho a provar d'aquí a una estona.", "El servei de qualitat de l'aire no ha respost."],
  name="Qualitat de l'aire", desc="Pregunta a un servei web gratuït com de net és l'aire i com de fort és el sol on ets.",
  ex=["Quina és la qualitat de l'aire?", "Quin és l'índex UV avui?"],
  gold=[("quina és la qualitat de l'aire", "air"), ("l'aire està net avui", "air"), ("quin és l'índex uv avui", "uv"), ("com de fort és el sol avui", "uv")]),
"gl-ES": dict(
  air=["como está o aire (hoxe|fóra)", "cal é a calidade do aire (aquí|hoxe|fóra)", "está o aire (limpo|ben) (hoxe|fóra)", "(comproba|dime) a calidade do aire", "cal é a calidade do aire"],
  uv=["cal é o índice uv (hoxe|agora)", "(que forte|que alta) é a radiación uv (hoxe|agora)", "está forte o (sol|uv) (hoxe|agora)", "que forte está o sol (hoxe|agora)"],
  air_levels="boa\nrazoable\nmoderada\nmala\nmoi mala\nextremadamente mala",
  uv_levels="baixo\nmoderado\nalto\nmoi alto\nextremo",
  airD=["O aire en {place} agora está {level}, cun índice europeo de calidade do aire de {index}.", "Agora mesmo a calidade do aire en {place} é {level}, índice {index}."],
  uvD=["O índice UV agora é {index}, é dicir, {level}.", "Agora mesmo o índice UV é {index}: {level}."],
  no_location=["Non sei onde está este dispositivo. Indica primeiro a localización en Axustes.", "Dime onde estás en Axustes e volve preguntar."],
  no_connection=["Non puiden contactar co servizo de calidade do aire. Téntao de novo nun momento.", "O servizo de calidade do aire non respondeu."],
  name="Calidade do aire", desc="Pregúntalle a un servizo web gratuíto que limpo está o aire e que forte está o sol onde estás.",
  ex=["Cal é a calidade do aire?", "Cal é o índice UV hoxe?"],
  gold=[("cal é a calidade do aire", "air"), ("está o aire limpo hoxe", "air"), ("cal é o índice uv hoxe", "uv"), ("que forte está o sol hoxe", "uv")]),
"eu-ES": dict(
  air=["nolakoa da airea (gaur|kanpoan)", "nolakoa da airearen kalitatea (hemen|gaur|kanpoan)", "airea (garbia|ona) dago (gaur|kanpoan)", "(egiaztatu|esadazu) airearen kalitatea", "nolakoa da airearen kalitatea"],
  uv=["zein da uv indizea (gaur|orain)", "(zein indartsua|zein altua) da uv erradiazioa (gaur|orain)", "(eguzkia|uv erradiazioa) indartsua da (gaur|orain)", "zein indartsua da eguzkia (gaur|orain)"],
  air_levels="ona\nonargarria\nertaina\ntxarra\noso txarra\nizugarri txarra",
  uv_levels="baxua\nertaina\naltua\noso altua\nmuturrekoa",
  airD=["Airea {level} dago orain {place} inguruan; Europako aire-kalitate indizea {index} da.", "Orain airearen kalitatea {level} da {place} inguruan, {index} indizearekin."],
  uvD=["UV indizea {index} da orain, hau da, {level}.", "Orain UV indizea {index} da: {level}."],
  no_location=["Ez dakit gailu hau non dagoen. Ezarri lehenik kokapena Ezarpenetan.", "Esadazu Ezarpenetan non zauden, eta galdetu berriro."],
  no_connection=["Ezin izan dut aire-kalitatearen zerbitzuarekin konektatu. Saiatu berriro pixka bat barru.", "Aire-kalitatearen zerbitzuak ez du erantzun."],
  name="Airearen kalitatea", desc="Doako web zerbitzu bati galdetzen dio zein garbia dagoen airea eta zein indartsua den eguzkia zauden lekuan.",
  ex=["Nolakoa da airearen kalitatea?", "Zein da UV indizea gaur?"],
  gold=[("nolakoa da airearen kalitatea", "air"), ("airea garbia dago gaur", "air"), ("zein da uv indizea gaur", "uv"), ("zein indartsua da eguzkia gaur", "uv")]),
}

LOCALE = {lang: {"air.intent": "\n".join(v["air"]), "uv.intent": "\n".join(v["uv"]),
                 "air_levels.list": v["air_levels"], "uv_levels.list": v["uv_levels"],
                 "air_now.dialog": "\n".join(v["airD"]), "uv_now.dialog": "\n".join(v["uvD"]),
                 "no_location.dialog": "\n".join(v["no_location"]), "no_connection.dialog": "\n".join(v["no_connection"])}
          for lang, v in L.items()}
SKILL_JSON = {lang: {"name": v["name"], "description": v["desc"], "examples": v["ex"]} for lang, v in L.items()}
GOLDEN = {lang: [(u, f"{i}.intent") for u, i in v["gold"]] for lang, v in L.items()}

README = '''
# Ask the web: air quality and UV

Ask **"how is the air quality?"** or **"what is the UV index today?"** and the
skill asks a web service – [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api),
free, no account, no key – about the place your device is set to, and says
the answer, in all twelve of [Emkay](https://emkay.ai)'s languages.

**👉 The friendly guide: <https://dev.emkay.ai>**

## What it shows

- **Calling a web service:** `requests.get(URL, params=..., timeout=10)`,
  then `.json()`. In Emkay this runs in your browser, so the service must
  allow it (CORS) – Open-Meteo does. Emkay's *What's happening?* view shows
  every call the skill makes and where it went.
- **Where the device is:** `self.location` (the coordinates) and
  `self.location_pretty` (the place name), from Settings → location.
- **When it goes wrong:** no location, no network, a service that does not
  answer – the skill says so (`no_location.dialog`, `no_connection.dialog`)
  instead of staying silent.
- **Two intents, one skill:** `air.intent` and `uv.intent`.
- **Words per language for numbers:** `air_levels.list` and `uv_levels.list`
  hold the word for each level, one per line, in order.

## Try changing

- `CURRENT` – Open-Meteo knows more (pollen in Europe, dust, ozone …): add one
  and a third intent that asks for it;
- the words for the levels, or what it says (`air_now.dialog`, `uv_now.dialog`);
- or point it at another free service – the shape stays the same.
'''
