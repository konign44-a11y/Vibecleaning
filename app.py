import streamlit as st
import datetime
import json
import os

# 1. Seiteneinstellungen optimieren
st.set_page_config(page_title="VibeCleaning", page_icon="🧹", layout="centered")

DB_FILE = "wg_data.json"
wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# 2. Funktionen zum Laden und Speichern der Daten
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                raw_data = json.load(f)
                # JSON speichert Keys immer als Text, wir wandeln die KW-Keys wieder in Integers um
                return {int(k): v for k, v in raw_data.items()}
        except Exception:
            return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Daten beim Start der App einmalig laden
if "tracking_data" not in st.session_state:
    st.session_state.tracking_data = load_data()

# 3. Festgelegtes WG-Setup
wg_crew = ["Nico", "Kiki", "Bruno"]
aufgaben = ["Bad putzen 🧼", "Küche & Böden 🍳", "Müll & Altglas 🗑️"]

anzahl_mitglieder = len(wg_crew)
aktuell_kw = datetime.datetime.now().isocalendar()[1]
letzte_kw = aktuell_kw - 1

# --- FIX: Absolut sichere Initialisierung der Keys ---
for kw in [aktuell_kw, letzte_kw]:
    if kw not in st.session_state.tracking_data:
        st.session_state.tracking_data[kw] = {}
    
    # Sicherstellen, dass JEDE Aufgabe als String-Key existiert
    for i in range(len(aufgaben)):
        aufgabe_key = str(i)
        if aufgabe_key not in st.session_state.tracking_data[kw]:
            st.session_state.tracking_data[kw][aufgabe_key] = {tag: False for tag in wochentage}

# Direkt einmal wegspeichern, damit die Struktur auf der Festplatte existiert
save_data(st.session_state.tracking_data)

# --- UI LAYOUT ---
st.title("🧹 VibeCleaning")

# Profil-Auswahl in der Sidebar
st.sidebar.header("👤 Profil")
aktiver_nutzer = st.sidebar.selectbox("Wer nutzt die App gerade?", wg_crew)
st.sidebar.write(f"Hallo **{aktiver_nutzer}**! Viel Spaß beim Putzen. 🙌")

st.info(f"📅 **Aktuelle Kalenderwoche:** {aktuell_kw}")

tab1, tab2 = st.tabs(["📌 Aktuelle Woche", "📜 Historie (Letzte Woche)"])

# TAB 1: AKTUELLE WOCHE
with tab1:
    st.subheader("Deine Aufgaben für diese Woche:")
    
    for i, aufgabe in enumerate(aufgaben):
        bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
        zustandiger = wg_crew[bewohner_index]
        aufgabe_key = str(i)
        
        with st.container():
            st.markdown(f"### {aufgabe}")
            st.markdown(f"👤 **Zuständig:** `{zustandiger}`")
            
            cols = st.columns(7)
            for j, tag in enumerate(wochentage):
                with cols[j]:
                    # Zustand aus dem Speicher holen
                    ist_erledigt = st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag]
                    button_label = f"✅ {tag}" if ist_erledigt else tag
                    
                    if st.button(button_label, key=f"btn_akt_{i}_{tag}", use_container_width=True):
                        # Zustand toggeln
                        st.session_state.tracking_data[aktuell_kw][aufgabe_key][tag] = not ist_erledigt
                        # Sofort speichern
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
