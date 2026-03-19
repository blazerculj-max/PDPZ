import streamlit as st

# --- FUNKCIJA ZA IZRAČUN DOHODNINE (LOGIKA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    """
    Izračuna letno dohodnino upoštevajoč vse olajšave in prispevke po slikah ZPIZ.
    """
    # Parametri iz tvojih slik (leto 2026)
    SPLUSNA_LETNA = 438.33 * 12
    SENIORSKA_LETNA = 131.50 * 12 if starost >= 70 else 0
    OZP_LETNI = 37.17 * 12 # Obvezni zdravstveni prispevek
    PDO_STOPNJA = 0.01    # Prispevek za dolgotrajno oskrbo (1%)
    
    # 1. Prispevki, ki zmanjšujejo davčno osnovo (od pokojnine)
    prispevki = OZP_LETNI + (bruto_pok_letna * PDO_STOPNJA)
    
    # 2. Zmanjšana davčna osnova
    osnova = max(0, bruto_vsi - prispevki - SPLUSNA_LETNA - SENIORSKA_LETNA)
    
    # 3. Dohodninska lestvica 2026
    if osnova <= 9000:
        davek_po_lestvici = osnova * 0.16
    elif osnova <= 25000:
        davek_po_lestvici = 1440 + (osnova - 9000) * 0.26
    else:
        davek_po_lestvici = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # 4. Pokojninska olajšava (13,5% od bruto pokojnine)
    # Odševa se direktno od odmerjenega davka
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek_po_lestvici - olajsava_zpiz)

# --- KONFIGURACIJA STRANI ---
st.set_page_config(page_title="Svetovalec za PDPZ 2026", layout="wide")

st.title("🛡️ Davčni kalkulator za prehod v pokoj (2026)")
st.markdown("Orodje za svetovalce: Primerjava obdavčitve enkratnega odkupa in mesečne rente po zakonodaji ZPIZ/ZDoh-2.")

# --- STRANSKI MENI ZA VNOS PODATKOV ---
with st.sidebar:
    st.header("1. Osnovni podatki")
    starost = st.number_input("Starost stranke", min_value=50, max_value=100, value=65)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0, step=50.0)
    
    st.header("2. PDPZ Sredstva")
    pdpz_kapital = st.number_input("Skupno stanje na računu (€)", value=30000.0, step=1000.0)
    renta_mes_bruto = st.number_input("Mesečna bruto renta (€)", value=400.0, step=10.0)

# --- IZRAČUN LETNIH OSNOV ---
letna_pok_bruto = bruto_pok_mes * 12
letna_renta_bruto = renta_mes_bruto * 12

# Osnovni davek (samo pokojnina)
davek_samo_pokojnina = izracun_dohodnine_2026(letna_pok_bruto, letna_pok_bruto, starost)

# --- SCENARIJ A: ENKRATNI ODKUP ---
davek_skupaj_odkup = izracun_dohodnine_2026(letna_pok_bruto + pdpz_kapital, letna_pok_bruto, starost)
davek_na_pdpz_odkup = davek_skupaj_odkup - davek_samo_pokojnina
neto_izplacilo_odkup = pdpz_kapital - davek_na_pdpz_odkup

# --- SCENARIJ B: MESEČNA RENTA ---
davek_skupaj_renta = izracun_dohodnine_2026(letna_pok_bruto + (letna_renta_bruto * 0.5), letna_pok_bruto, starost)
davek_na_pdpz_renta_letno = davek_skupaj_renta - davek_samo_pokojnina
neto_renta_letna = letna_renta_bruto - davek_na_pdpz_renta_letno

# NOVO PRAVILO AKONTACIJE: 
# Če je celotna mesečna renta >= 160 EUR -> 12,5% akontacije od celotnega zneska
akontacija_mesecna = 0.0
if renta_mes_bruto >= 160.0:
    akontacija_mesecna = renta_mes_bruto * 0.125

# --- PRIKAZ REZULTATOV ---
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 ENKRATNI ODKUP")
    st.metric("Neto izplačilo stranki", f"{neto_izplacilo_odkup:,.2f} €")
    st.write(f"**Plačana dohodnina:** {davek_na_pdpz_odkup:,.2f} €")
    st.write(f"**Dejanska obdavčitev:** {round((davek_na_pdpz_odkup/pdpz_kapital)*100, 2)} %")
    st.caption("Visoka enkratna osnova povzroči skok v 26% ali 33% davčni razred.")

with col2:
    st.success("### 🟢 MESEČNA RENTA")
    st.metric("Dejanska neto renta (povprečje)", f"{(neto_renta_letna/12):,.2f} €/mes")
    st.write(f"**Letni strošek dohodnine:** {davek_na_pdpz_renta_letno:,.2f} €")
    st.write(f"**Dejanska obdavčitev:** {round((davek_na_pdpz_renta_letno/letna_renta_bruto)*100, 2)} %")
    
    if akontacija_mesecna > 0:
        st.warning(f"⚠️ **Mesečna akontacija:** Ker je renta {renta_mes_bruto}€ (>= 160€), bo družba mesečno odvedla **{akontacija_mesecna:,.2f} €** (12,5%).")
    else:
        st.info("ℹ️ **Brez mesečne akontacije:** Renta je pod 160€, zato med letom ni odtegljaja akontacije.")

st.divider()

# --- TABELA ZA SVETOVALCA ---
st.subheader("Primerjava izračuna (na letni ravni)")
st.table({
    "Opis": ["Bruto prejemki", "Davčna osnova (z olajšavami)", "Skupna letna dohodnina", "Neto vpliv PDPZ"],
    "Enkratni odkup": [
        f"{letna_pok_bruto + pdpz_kapital:,.2f} €",
        f"{max(0, (letna_pok_bruto + pdpz_kapital) - (438.33*12) - (131.50*12 if starost>=70 else 0) - (37.17*12 + letna_pok_bruto*0.01)):,.2f} €",
        f"{davek_skupaj_odkup:,.2f} €",
        f"- {davek_na_pdpz_odkup:,.2f} €"
    ],
    "Mesečna renta": [
        f"{letna_pok_bruto + letna_renta_bruto:,.2f} €",
        f"{max(0, (letna_pok_bruto + letna_renta_bruto*0.5) - (438.33*12) - (131.50*12 if starost>=70 else 0) - (37.17*12 + letna_pok_bruto*0.01)):,.2f} €",
        f"{davek_skupaj_renta:,.2f} €",
        f"- {davek_na_pdpz_renta_letno:,.2f} €"
    ]
})

st.markdown(f"**Zaključek:** Z izbiro rente stranka obdrži **{davek_na_pdpz_odkup - davek_na_pdpz_renta_letno:,.2f} €** več denarja.")
