import streamlit as st
import datetime
import json
import os

# 1. Seiteneinstellungen optimieren
st.set_page_config(page_title="VibeCleaning", page_icon="🏆", layout="centered")

DB_FILE = "wg_data.json"
wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# 2. Festgelegtes WG-Setup und Punkteverteilung
wg_crew = ["Nico", "Kiki", "Bruno"]
# Wir nutzen ein Dictionary, um jeder Aufgabe feste Punkte zuzuweisen
aufgaben_mit_punkten = {
    "Bad putzen 🧼": 5,
    "Küche & Böden 🍳": 3,
    "Müll & Altglas 🗑️": 1
}
aufgaben = list(aufgaben_mit_punkten.keys())

# 3. Funktionen zum Laden und Speichern der Daten
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

anzahl_mitglieder = len(wg_crew)
aktuell_kw = datetime.datetime.now().isocalendar()[1]
letzte_kw = aktuell_kw - 1
heute_wochentag_index = datetime.datetime.now().weekday() # 0 = Mo, 4 = Fr, 6 = So

# Sicherstellen, dass Strukturen für aktuelle und letzte Woche existieren
for kw in [aktuell_kw, letzte_kw]:
    if kw not in st.session_state.tracking_data:
        st.session_state.tracking_data[kw] = {}
    for i in range(len(aufgaben)):
        aufgabe_key = str(i)
        if aufgabe_key not in st.session_state.tracking_data[kw]:
            st.session_state.tracking_data[kw][aufgabe_key] = {tag: False for tag in wochentage}

save_data(st.session_state.tracking_data)

# --- SCOREBERECHNUNG ---
# Wir berechnen die Live-Punkte dynamisch anhand aller gesetzten Haken in der aktuellen Woche
punkte_stand = {name: 0 for name in wg_crew}
wer_hat_was_erledigt = {name: 0 for name in wg_crew} # Zähler für die Wall of Shame

for i, aufgabe in enumerate(aufgaben):
    # Wer ist diese Woche für diese Aufgabe zuständig?
    bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
    zustandiger = wg_crew[bewohner_index]
    aufgabe_key = str(i)
    
    # Punkte zählen
    punkte_wert = aufgaben_mit_punkten[aufgabe]
    for tag in wochentage:
        if st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]:
            punkte_stand[zustandiger] += punkte_wert
            wer_hat_was_erledigt[zustandiger] += 1

# --- UI LAYOUT ---
st.title("🏆 VibeCleaning — Das WG-Duell")

# --- SIDEBAR: PROFIL & LEADERBOARD ---
st.sidebar.header("👤 Profil")
aktiver_nutzer = st.sidebar.selectbox("Wer nutzt die App gerade?", wg_crew)
st.sidebar.write(f"Hallo **{aktiver_nutzer}**! Bring die Rangliste zum Beben! 🔥")

st.sidebar.markdown("---")
st.sidebar.header("📊 Live-Rangliste (KW " + str(aktuell_kw) + ")")

# Sortiere die Mitbewohner nach Punkten absteigend
ranking = sorted(punkte_stand.items(), key=lambda x: x[1], reverse=True)
for platz, (name, punkte) in enumerate(ranking, 1):
    medaille = "🥇" if platz == 1 else "🥈" if platz == 2 else "🥉"
    st.sidebar.write(f"{medaille} **{name}**: {punkte} Pkt.")

st.sidebar.markdown("---")

# GAMIFICATION FEATURE 2: WALL OF FAME & SHAME (Aktiv ab Freitag)
st.sidebar.header("📢 WG-Anpranger")
fame_name, fame_punkte = ranking[0]
shame_kandidaten = [name for name, haken in wer_hat_was_erledigt.items() if haken == 0]

# Wall of Fame
if fame_punkte > 0:
    st.sidebar.success(f"👑 **Wall of Fame:**\n{fame_name} fleht um Konkurrenz ({fame_punkte} Punkte)!")

# Wall of Shame (wird ab Freitag ernster genommen)
if shame_kandidaten:
    shame_liste = ", ".join(shame_kandidaten)
    if heute_wochentag_index >= 4: # Freitag, Samstag, Sonntag
        st.sidebar.error(f"💀 **Wall of Shame:**\n{shame_liste} haben diese Woche noch nix gemacht! Das riecht nach Straf-Bier! 🍻")
    else:
        st.sidebar.warning(f"👀 **Beobachtung:**\n{shame_liste} haben noch keinen Finger gerührt. Da geht noch was!")
else:
    st.sidebar.info("🙌 Keiner auf der Wall of Shame. Saubere WG!")


# --- HAUPTBEREICH TABS ---
st.info(f"📅 **Kalenderwoche:** {aktuell_kw}")
tab1, tab2 = st.tabs(["📌 Aktuelle Woche", "📜 Historie (Letzte Woche)"])

# TAB 1: AKTUELLE WOCHE
with tab1:
    st.subheader("Erledige deine Aufgaben und sammle Punkte:")
    
    for i, aufgabe in enumerate(aufgaben):
        bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
        zustandiger = wg_crew[bewohner_index]
        aufgabe_key = str(i)
        punkte_wert = aufgaben_mit_punkten[aufgabe]
        
        with st.container():
            st.markdown(f"### {aufgabe} `+{punkte_wert} Pkt./Tag`")
            st.markdown(f"👤 **Zuständig:** `{zustandiger}`")
            
            cols = st.columns(7)
            for j, tag in enumerate(wochentage):
                with cols[j]:
                    ist_erledigt = st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]
                    button_label = f"✅ {tag}" if ist_erledigt else tag
                    
                    if st.button(button_label, key=f"btn_akt_{i}_{tag}", use_container_width=True):
                        st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag] = not ist_erledigt
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
                if st.session_state.tracking_data[letzte_kw][aufgabe_key][tag]:
                    erledigte_tage.append(f"🟢 {tag}")
                else:
                    erledigte_tage.append(f"⚪ {tag}")
            
            st.write(" ".join(erledigte_tage))
            st.markdown("")
