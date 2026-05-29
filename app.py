import streamlit as st
import datetime

st.set_page_config(page_title="VibeCleaning", page_icon="🧹", layout="centered")

wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

if "tracking_data" not in st.session_state:
    st.session_state.tracking_data = {}

wg_crew = ["Nico", "Kiki", "Bruno"]
aufgaben = ["Bad putzen 🧼", "Küche & Böden 🍳", "Müll & Altglas 🗑️"]

anzahl_mitglieder = len(wg_crew)
aktuell_kw = datetime.datetime.now().isocalendar()[1]
letzte_kw = aktuell_kw - 1

for kw in [aktuell_kw, letzte_kw]:
    if kw not in st.session_state.tracking_data:
        st.session_state.tracking_data[kw] = {
            i: {tag: False for tag in wochentage} for i in range(len(aufgaben))
        }

st.title("🧹 VibeCleaning")

st.sidebar.header("👤 Profil")
aktiver_nutzer = st.sidebar.selectbox("Wer nutzt die App gerade?", wg_crew)
st.sidebar.write(f"Hallo **{aktiver_nutzer}**! Viel Spaß beim Putzen. 🙌")

st.info(f"📅 **Aktuelle Kalenderwoche:** {aktuell_kw}")

tab1, tab2 = st.tabs(["📌 Aktuelle Woche", "📜 Historie (Letzte Woche)"])

with tab1:
    st.subheader("Deine Aufgaben für diese Woche:")
    for i, aufgabe in enumerate(aufgaben):
        bewohner_index = (i + aktuell_kw) % anzahl_mitglieder
        zustandiger = wg_crew[bewohner_index]
        
        with st.container():
            st.markdown(f"### {aufgabe}")
            st.markdown(f"👤 **Zuständig:** `{zustandiger}`")
            
            cols = st.columns(7)
            for j, tag in enumerate(wochentage):
                with cols[j]:
                    ist_erledigt = st.session_state.tracking_data[aktuell_kw][i][tag]
                    button_label = f"✅ {tag}" if ist_erledigt else tag
                    if st.button(button_label, key=f"btn_akt_{i}_{tag}", use_container_width=True):
                        st.session_state.tracking_data[aktuell_kw][i][tag] = not ist_erledigt
                        st.rerun()
            st.markdown("---")

with tab2:
    st.subheader(f"Ergebnisse aus der Vorwoche (KW {letzte_kw})")
    with st.expander("📊 Detailübersicht öffnen", expanded=True):
        for i, aufgabe in enumerate(aufgaben):
            bewohner_index_letzte = (i + letzte_kw) % anzahl_mitglieder
            zustandiger_letzte = wg_crew[bewohner_index_letzte]
            
            st.markdown(f"**{aufgabe}** (Verantwortlich: *{zustandiger_letzte}*)")
            erledigte_tage = []
            for tag in wochentage:
                if st.session_state.tracking_data[letzte_kw][i][tag]:
                    erledigte_tage.append(f"🟢 {tag}")
                else:
                    erledigte_tage.append(f"⚪ {tag}")
            st.write(" ".join(erledigte_tage))
            st.markdown("")
