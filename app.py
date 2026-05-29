import streamlit as st
import datetime

# 1. Seiteneinstellungen für mobile Geräte optimieren
st.set_page_config(page_title="VibeCleaning", page_icon="🧹", layout="centered")

# Schickes CSS für größere Buttons auf dem Handy
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 60px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧹 VibeCleaning — Eure WG-App")
st.write("Wer ist diese Woche mit was dran?")

# 2. Festes WG-Setup (Hier einfach eure Namen und Aufgaben anpassen!)
wg_crew = ["Anna", "Ben", "Chris", "Daria"]
aufgaben = ["Bad putzen 🧼", "Küche & Böden 🍳", "Müll & Altglas 🗑️", "Einkaufen & Orga 🛒"]

# 3. Die Rotations-Logik basierend auf der aktuellen Kalenderwoche (KW)
aktuell_kw = datetime.datetime.now().isocalendar()[1]
anzahl_mitglieder = len(wg_crew)

st.info(#cite: 14
    f"📅 **Aktuelle Kalenderwoche:** {aktuell_kw}"
)

st.subheader("📌 Aufgabenverteilung für diese Woche:")

# Berechnung, wer was macht (Verschiebung jede Woche um 1)
for i, aufgabe in enumerate(aufgaben):
    # Der Index des Bewohners rotiert jede Woche weiter
    bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
    zustandiger = wg_crew[bewohner_index]
    
    # Schicke Boxen für die Aufgaben im mobilen Layout
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### {aufgabe}")
            st.markdown(f"👤 **Verantwortlich:** {zustandiger}")
        with col2:
            # Ein simpler Haken-Button für das Handy
            if st.button("Erledigt! ✅", key=f"btn_{i}"):
                st.success(f"Danke, {zustandiger}! 🎉")
        st.markdown("---")

st.caption("💡 Die Aufgaben rotieren jeden Montag automatisch eine Person weiter.")
