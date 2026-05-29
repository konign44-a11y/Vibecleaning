import streamlit as st
import datetime
import json
import os
import random
import streamlit.components.v1 as components

# 1. Seiteneinstellungen für mobile Handys optimieren
st.set_page_config(
    page_title="VibeCleaning", 
    page_icon="🏆", 
    layout="centered"
)

DB_FILE = "wg_data.json"
wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# 2. Festgelegtes WG-Setup und Punkteverteilung
wg_crew = ["Nico", "Kiki", "Bruno"]
aufgaben_mit_punkten = {
    "Bad putzen 🧼": 5,
    "Küche & Böden 🍳": 3,
    "Müll & Altglas 🗑️": 1
}
aufgaben = list(aufgaben_mit_punkten.keys())

# --- ANIMATIONS-FUNKTION ---
def zeige_animation_effekt(effekt_typ):
    if effekt_typ == "feuerwerk":
        js = """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            var end = Date.now() + 1000;
            (function frame() {
                confetti({ particleCount: 5, angle: 60, spread: 55, origin: { x: 0, y: 0.8 } });
                confetti({ particleCount: 5, angle: 120, spread: 55, origin: { x: 1, y: 0.8 } });
                if (Date.now() < end) { requestAnimationFrame(frame); }
            }());
        </script>
        """
    elif effekt_typ == "explosion":
        js = """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            confetti({ scalar: 2, spread: 140, particleCount: 60, origin: { y: 0.4 } });
        </script>
        """
    else: # regen
        js = """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            confetti({ particleCount: 100, spread: 70, origin: { y: 0.4 } });
        </script>
        """
    components.html(js, height=0, width=0)

# 3. Daten laden / speichern
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                raw_data = json.load(f)
                return {int(k): v for k, v in raw_data.items()}
        except Exception:
            return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "tracking_data" not in st.session_state:
    st.session_state.tracking_data = load_data()

if "animations_trigger" not in st.session_state:
    st.session_state.animations_trigger = None

anzahl_mitglieder = len(wg_crew)
aktuell_kw = datetime.datetime.now().isocalendar()[1]
letzte_kw = aktuell_kw - 1
heute_wochentag_index = datetime.datetime.now().weekday()

# Strukturen absichern
for kw in [aktuell_kw, letzte_kw]:
    if kw not in st.session_state.tracking_data:
        st.session_state.tracking_data[kw] = {}
    for i in range(len(aufgaben)):
        aufgabe_key = str(i)
        if aufgabe_key not in st.session_state.tracking_data[kw]:
            st.session_state.tracking_data[kw][aufgabe_key] = {}
        for tag in wochentage:
            if tag not in st.session_state.tracking_data[kw][aufgabe_key]:
                st.session_state.tracking_data[kw][aufgabe_key][tag] = {"erledigt": False, "helfer": None}

save_data(st.session_state.tracking_data)

# --- SCOREBERECHNUNG ---
punkte_stand = {name: 0 for name in wg_crew}
wer_hat_was_erledigt = {name: 0 for name in wg_crew}

for kw in [aktuell_kw]:
    for i, aufgabe in enumerate(aufgaben):
        bewohner_index = (i + kw) % anzahl_mitglieder
        zustandiger = wg_crew[bewohner_index]
        aufgabe_key = str(i)
        
        for tag in wochentage:
            tag_data = st.session_state.tracking_data[kw][aufgabe_key][tag]
            if tag_data["erledigt"]:
                punkte_stand[zustandiger] += aufgaben_mit_punkten[aufgabe]
                wer_hat_was_erledigt[zustandiger] += 1
                if tag_data["helfer"] and tag_data["helfer"] in punkte_stand:
                    punkte_stand[tag_data["helfer"]] += 1

# --- LOGIN-PRÜFUNG ---
if "eingeloggter_user" not in st.session_state:
    st.session_state.eingeloggter_user = None

if "aktueller_trash_spruch" not in st.session_state:
    st.session_state.aktueller_trash_spruch = ""
if "letzter_status_typ" not in st.session_state:
    st.session_state.letzter_status_typ = ""

# --- ANSICHT 1: WILLKOMMENS-BILDSCHIRM ---
if st.session_state.eingeloggter_user is None:
    st.title("🧹 Willkommen bei VibeCleaning!")
    st.subheader("Wer öffnet gerade die App?")
    
    cols_login = st.columns(3)
    for index, name in enumerate(wg_crew):
        with cols_login[index]:
            if st.button(f"👤 {name}", key=f"login_{name}", use_container_width=True):
                st.session_state.eingeloggter_user = name
                st.session_state.aktueller_trash_spruch = "" 
                st.session_state.letzter_status_typ = ""
                st.rerun()
    st.markdown("---")
    st.caption("💡 Tippe auf deinen Namen, um zu deinen Aufgaben zu gelangen.")

# --- ANSICHT 2: DIE HAUPT-APP ---
else:
    aktiver_nutzer = st.session_state.eingeloggter_user

    st.title("🏆 VibeCleaning")
    
    col_header1, col_header2 = st.columns([2, 1])
    with col_header1:
        st.write(f"Hallo **{aktiver_nutzer}**! Bring die Bude auf Hochglanz. ✨")
    with col_header2:
        if st.button("🔄 Profil wechseln", key="logout_btn", use_container_width=True):
            st.session_state.eingeloggter_user = None
            st.rerun()

    st.markdown("---")

    # RANGLISTE & TRASH-TALK
    st.subheader("📊 Das WG-Ranking diese Woche")
    
    ranking = sorted(punkte_stand.items(), key=lambda x: x[1], reverse=True)
    cols_rank = st.columns(3)
    for platz, (name, punkte) in enumerate(ranking, 1):
        medaille = "🥇" if platz == 1 else "🥈" if platz == 2 else "🥉"
        with cols_rank[platz-1]:
            st.metric(label=f"{medaille} {name}", value=f"{punkte} Pkt.")

    # --- SÜNDHAFT GROSSE TRASH-TALK DATENBANK ---
    st.markdown("#### 💬 Boss-Talk & Ansagen")
    leader_name, leader_punkte = ranking[0]
    loser_name, loser_punkte = ranking[-1]
    verfolger = [name for name, p in ranking if name != leader_name]
    verfolger_text = " und ".join(verfolger)
    
    # Zustand ermitteln
    if leader_punkte == 0:
        aktueller_typ = "streik"
    elif leader_punkte == loser_punkte:
        aktueller_typ = "gleichstand"
    elif leader_punkte >= loser_punkte + 8: # Großer Vorsprung
        aktueller_typ = "dominanz"
    else:
        aktueller_typ = "normal"

    # Nur neu würfeln, wenn sich der Zustand geändert hat oder noch kein Spruch da ist
    if not st.session_state.aktueller_trash_spruch or st.session_state.letzter_status_typ != aktueller_typ:
        st.session_state.letzter_status_typ = aktueller_typ
        
        if aktueller_typ == "streik":
            sprueche = [
                "💤 *Putz-Streik?* Alle stehen bei 0 Punkten. Seid ihr eine WG oder ein Faultier-Gehege?",
                "🕸️ *Spinnweben übernehmen das Kommando.* Macht einer mal den ersten Klick oder warten wir auf den Kammerjäger?",
                "🦠 *Biologische Kriegsführung.* Wenn hier nicht bald jemand putzt, gründet der Staub eine eigene Gewerkschaft.",
                "🦥 Alarm! Dreifacher Systemausfall bei Nico, Kiki und Bruno. Der Besen weint in der Ecke.",
                "🛑 Null Punkte überall. Ich wusste gar nicht, dass Faulheit eine olympische Disziplin ist."
            ]
        elif aktueller_typ == "gleichstand":
            sprueche = [
                "⚖️ *Waffenstillstand.* Totaler Gleichstand. Keiner traut sich, den ersten Schritt zu machen.",
                "🍿 *Spannung pur.* Alle punktgleich. Wer bricht als Erstes das WG-Ehrenwort und zieht vorbei?",
                "🔄 Ein perfektes Trio der Inaktivität. Ihr teilt euch die Punkte so fair auf, dass es fast schon wehtut.",
                "🧩 Gleichstand! Seid ihr euch heimlich einig oder schaut ihr alle 5 Minuten nach, ob der andere was geklickt hat?"
            ]
        elif aktueller_typ == "dominanz":
            sprueche = [
                f"👑 **{leader_name}** fragt sich ernsthaft, ob **{verfolger_text}** überhaupt noch leben oder schon eingestaubt sind.",
                f"🚀 **{leader_name}** zieht einsam seine Kreise, während **{loser_name}** anscheinend noch versucht herauszufinden, wie ein Besen funktioniert. 🧹",
                f"🕶️ *'Eure Armut an Punkten kotzt mich an!'* — **{leader_name}** dominiert die WG im Alleingang.",
                f"🦁 **{leader_name}** regiert den Putz-Dschungel. **{loser_name}** wurde zuletzt weinend im Müllraum gesichtet.",
                f"📢 Ansage von **{leader_name}**: *'Hinter mir ist noch herrlich viel Platz, zieht mal nach!'*",
                f"🦖 **{leader_name}** stampft alles kurz und klein. **{loser_name}** zittert schon vor der nächsten Abrechnung.",
                f"🔭 **{leader_name}** braucht ein Fernglas, um **{loser_name}** da unten am Tabellenende überhaupt noch zu sehen.",
                f"🎭 **{leader_name}** macht die Arbeit, **{verfolger_text}** machen Urlaub. Schöne Rollenverteilung!"
            ]
        else: # normal / knappe Aufholjagd
            sprueche = [
                f"🏃‍♂️ **{leader_name}** führt knapp! Aber Pass auf, **{verfolger_text}** riechen bereits deine Spur.",
                f"👀 Gerüchten zufolge hat **{leader_name}** diese Woche schon mehr getan als **{loser_name}**, aber der Kampf ist noch heiß!",
                f"💅 **{leader_name}** steht auf Platz 1. **{loser_name}** hat aber fest versprochen, 'gleich morgen' ganz viel zu machen.",
                f"🔥 Das Duell brennt! **{leader_name}** spürt den heißen Atem der Konkurrenz im Nacken.",
                f"🎯 **{leader_name}** hält die Spitze, aber das Board wackelt. Einmal Müll wegbringen und die Welt sieht anders aus!"
            ]
        st.session_state.aktueller_trash_spruch = random.choice(sprueche)
        
    # Ausgabe der Textbox
    if aktueller_typ == "streik":
        st.warning(st.session_state.aktueller_trash_spruch)
    elif aktueller_typ == "gleichstand":
        st.info(st.session_state.aktueller_trash_spruch)
    else:
        st.success(st.session_state.aktueller_trash_spruch)

    # WG-ANPRANGER
    shame_kandidaten = [name for name, haken in wer_hat_was_erledigt.items() if haken == 0]
    if shame_kandidaten:
        shame_liste = ", ".join(shame_kandidaten)
        if heute_wochentag_index >= 4:
            st.error(f"💀 **Wall of Shame:** {shame_liste} haben Freitagabend noch NULL Haken. Das kostet euch ein Kasten Bier! 🍻")
        else:
            st.markdown(f"👀 **Beobachtung:** {shame_liste} drücken sich bisher erfolgreich vor der Arbeit.")
    else:
        st.info("🙌 Alle haben diese Woche schon was gemacht. Rekordverdächtig!")

    st.markdown("---")

    # --- HAUPTBEREICH TABS ---
    st.info(f"📅 **Kalenderwoche:** {aktuell_kw}")
    tab1, tab2 = st.tabs(["📌 Aktuelle Woche", "📜 Historie (Letzte Woche)"])

    # TAB 1: AKTUELLE WOCHE
    with tab1:
        st.subheader("Deine Aufgaben für diese Woche:")
        
        for i, aufgabe in enumerate(aufgaben):
            bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
            zustandiger = wg_crew[bewohner_index]
            aufgabe_key = str(i)
            punkte_wert = aufgaben_mit_punkten[aufgabe]
            
            ist_gesperrt = (aktiver_nutzer != zustandiger)
            
            with st.container():
                hinweis = "" if not ist_gesperrt else " 🔒 (Nur lesbar)"
                st.markdown(f"### {aufgabe} `+{punkte_wert} Pkt./Tag`{hinweis}")
                st.markdown(f"👤 **Zuständig:** `{zustandiger}`")
                
                # Radio-Buttons für die Helfer direkt unter der Aufgabe
                gewahlter_helfer = None
                if not ist_gesperrt:
                    andere_bewohner = [name for name in wg_crew if name != aktiver_nutzer]
                    auswahl_optionen = ["Niemand (Allein gemacht)"] + andere_bewohner
                    
                    gewaehlt = st.radio(
                        "Hat dir jemand geholfen? (Auswählen, dann Tag anklicken)",
                        auswahl_optionen,
                        key=f"radio_helper_{i}",
                        horizontal=True
                    )
                    if gewaehlt != "Niemand (Allein gemacht)":
                        gewahlter_helfer = gewaehlt
                
                # Wochentage
                cols = st.columns(7)
                for j, tag in enumerate(wochentage):
                    with cols[j]:
                        tag_dict = st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]
                        ist_erledigt = tag_dict["erledigt"]
                        aktueller_helfer = tag_dict.get("helfer", None)
                        
                        if ist_erledigt:
                            label = f"✅ {tag}" + (f" ({aktueller_helfer[0]}.)" if aktueller_helfer else "")
                        else:
                            label = tag
                        
                        if st.button(label, key=f"btn_{i}_{tag}", use_container_width=True, disabled=ist_gesperrt):
                            neuer_zustand = not ist_erledigt
                            st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]["erledigt"] = neuer_zustand
                            
                            if neuer_zustand:
                                st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]["helfer"] = gewahlter_helfer
                                st.session_state.animations_trigger = random.choice(["regen", "feuerwerk", "explosion"])
                            else:
                                st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]["helfer"] = None
                            
                            # Bei Punkteänderung alten Spruch löschen um sofortige Neuberechnung zu erzwingen
                            st.session_state.aktueller_trash_spruch = ""
                            save_data(st.session_state.tracking_data)
                            st.rerun()
                st.markdown("---")

    # TAB 2: HISTORIE
    with tab2:
        st.subheader(f"Ergebnisse aus der Vorwoche (KW {letzte_kw})")
        with st.expander("📊 Detailübersicht öffnen", expanded=True):
            for i, aufgabe in enumerate(aufgaben):
                bewohner_index_letzte = (i + letzte_kw) % anzahl_mitglieder
                zustandiger_letzte = wg_crew[bewohner_index_letzte]
                aufgabe_key = str(i)
                
                st.markdown(f"**{aufgabe}** (Verantwortlich: *{zustandiger_letzte}*)")
                
                erledigte_tage = []
                for tag in wochentage:
                    tag_data_letzte = st.session_state.tracking_data[letzte_kw][aufgabe_key][tag]
                    if isinstance(tag_data_letzte, dict) and tag_data_letzte["erledigt"]:
                        h_name = tag_data_letzte.get("helfer")
                        suffix = f"🤝{h_name}" if h_name else ""
                        erledigte_tage.append(f"🟢 {tag}{suffix}")
                    else:
                        erledigte_tage.append(f"⚪ {tag}")
                st.write("  |  ".join(erledigte_tage))
                st.markdown("")

    # --- ANIMATION AUSFÜHREN ---
    if st.session_state.animations_trigger:
        zeige_animation_effekt(st.session_state.animations_trigger)
        st.session_state.animations_trigger = None
