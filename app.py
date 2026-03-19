import streamlit as st

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # Parametri 2026 iz tvojih slik
    SPLUSNA_LETNA = 438.33 * 12
    SENIORSKA_LETNA = 131.50 * 12 if starost >= 70 else 0
    OZP_LETNI = 37.17 * 12 
    PDO_STOPNJA = 0.01  # 1% prispevek za dolgotrajno oskrbo
    
    # Prispevki (zmanjšujejo osnovo)
    prispevki = OZP_LETNI + (bruto_pok_letna * PDO_STOPNJA)
    
    # Davčna osnova
    osnova = max(0, bruto_vsi - prispevki - SPLUSNA_LETNA - SENIORSKA_LETNA)
    
    # Dohodninska lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # Pokojninska olajšava (13,5% od bruto pokojnine) - "Tax Credit"
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz)

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Optimizator 2026", layout="wide")
st.title("🛡️ Davčni kalkulator: Enkratni odkup vs. Renta (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("1. Podatki o upokojencu")
    starost = st.number_input("Starost stranke", value=65)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    
    st.header("2. Podatki o PDPZ")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0)
    renta_mes_bruto = st.number_input("Mesečna bruto renta (€)", value=400.0)

# --- IZRAČUNI ---
letna_pok_bruto = bruto_pok_mes * 12
davek_osnovni = izracun_dohodnine_2026(letna_pok_bruto, letna_pok_bruto, starost)

# SCENARIJ: ENKRATNI ODKUP
akontacija_takoj_25 = pdpz_kapital * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(letna_pok_bruto + pdpz_kapital, letna_pok_bruto, starost)
dejanski_davek_na_pdpz = davek_skupaj_odkup - davek_osnovni
doplacilo_ob_poracunu = max(0, dejanski_davek_na_pdpz - akontacija_takoj_25)
neto_izplacilo_trr = pdpz_kapital - akontacija_takoj_25

# SCENARIJ: RENTA
letna_renta_bruto = renta_mes_bruto * 12
davek_skupaj_renta = izracun_dohodnine_2026(letna_pok_bruto + (letna_renta_bruto * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta = davek_skupaj_renta - davek_osnovni
akontacija_renta_125 = renta_mes_bruto * 0.125 if renta_mes_bruto >= 160 else 0

# --- PRIKAZ REZULTATOV ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 SCENARIJ: Enkratni odkup")
    st.markdown(f"**Bruto znesek na računu:** {pdpz_kapital:,.2f} €")
    st.markdown(f"**Takojšen odtegljaj FURS (25%):** -{akontacija_takoj_25:,.2f} €")
    st.subheader(f"Izplačilo na TRR: {neto_izplacilo_trr:,.2f} €")
    st.write("---")
    st.write(f"**Predviden poračun dohodnine:** -{doplacilo_ob_poracunu:,.2f} €")
    st.info(f"Dejanski neto po poračunu: **{pdpz_kapital - dejanski_davek_na_pdpz:,.2f} €**")
    st.caption(f"Efektivna obdavčitev: {round((dejanski_davek_na_pdpz/pdpz_kapital)*100, 1)}%")

with col2:
    st.success("### 🟢 SCENARIJ: Mesečna renta")
    st.markdown(f"**Bruto mesečna renta:** {renta_mes_bruto:,.2f} €")
    if akontacija_renta_125 > 0:
        st.write(f"**Mesečni odtegljaj (12,5%):** -{akontacija_renta_125:,.2f} €")
        st.subheader(f"Mesečno nakazilo: {renta_mes_bruto - akontacija_renta_125:,.2f} €")
    else:
        st.subheader(f"Mesečno nakazilo: {renta_mes_bruto:,.2f} €")
        st.caption("Brez mesečne akontacije (pod 160€).")
    
    st.write("---")
    neto_renta_letna = letna_renta_bruto - dejanski_davek_renta
    st.write(f"**Dejanski neto (letno povprečje):** {neto_renta_letna/12:,.2f} €/mes")
    st.caption(f"Efektivna obdavčitev: {round((dejanski_davek_renta/letna_renta_bruto)*100, 1) if letna_renta_bruto > 0 else 0}%")

st.divider()

# --- ARGUMENTACIJA ---
st.subheader("💡 Zakaj izbrati rento?")
razlika = dejanski_davek_na_pdpz - dejanski_davek_renta
st.warning(f"""
Zaradi progresivne obdavčitve v letu 2026 stranka pri enkratnem odkupu državi plača 
**{razlika:,.2f} € več** davka kot pri renti. Pri renti se namreč v davčno osnovo 
všteje le 50% zneska (čl. 42 ZDoh-2), kar ohranja stranko v nižjem davčnem razredu.
""")
