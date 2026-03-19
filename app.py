import streamlit as st

# --- FUNKCIJA ZA IZRAČUN DOHODNINE (LOGIKA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # Parametri 2026 iz slik
    SPLUSNA_LETNA = 438.33 * 12
    SENIORSKA_LETNA = 131.50 * 12 if starost >= 70 else 0
    OZP_LETNI = 37.17 * 12 
    PDO_STOPNJA = 0.01    # 1% za dolgotrajno oskrbo
    
    # Prispevki (zmanjšujejo osnovo)
    prispevki = OZP_LETNI + (bruto_pok_letna * PDO_STOPNJA)
    
    # Davčna osnova
    osnova = max(0, bruto_vsi - prispevki - SPLUSNA_LETNA - SENIORSKA_LETNA)
    
    # Lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # Pokojninska olajšava (13,5% od bruto pokojnine)
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz)

# --- UI NASTAVITVE ---
st.set_page_config(page_title="PDPZ Svetovalec 2026", layout="wide")
st.title("🛡️ Izračun odkupne vrednosti in davčne optimizacije (2026)")

with st.sidebar:
    st.header("Vhodni podatki")
    starost = st.number_input("Starost stranke", value=65)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    
    st.header("Sredstva PDPZ")
    pdpz_kapital = st.number_input("Skupno stanje na PDPZ računu (€)", value=30000.0)
    renta_mes_bruto = st.number_input("Mesečna bruto renta (€)", value=400.0)

# --- IZRAČUNI ---
letna_pok_bruto = bruto_pok_mes * 12
davek_osnova = izracun_dohodnine_2026(letna_pok_bruto, letna_pok_bruto, starost)

# SCENARIJ: ODKUP (Takojšen odtegljaj 25% + Letni poračun)
akontacija_odkup_25 = pdpz_kapital * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(letna_pok_bruto + pdpz_kapital, letna_pok_bruto, starost)
dejanski_davek_pdpz = davek_skupaj_odkup - davek_osnova
morebitno_doplacilo = max(0, dejanski_davek_pdpz - akontacija_odkup_25)

# SCENARIJ: RENTA (Pravilo 160€)
letna_renta_bruto = renta_mes_bruto * 12
davek_skupaj_renta = izracun_dohodnine_2026(letna_pok_bruto + (letna_renta_bruto * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta = davek_skupaj_renta - davek_osnova
akontacija_renta = renta_mes_bruto * 0.125 if renta_mes_bruto >= 160 else 0

# --- PRIKAZ REZULTATOV ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 ENKRATNI ODKUP")
    st.write(f"**Bruto znesek:** {pdpz_kapital:,.2f} €")
    st.write(f"**Takojšen odtegljaj (25% akontacija):** -{akontacija_odkup_25:,.2f} €")
    st.write(f"**Predviden poračun dohodnine:** -{morebitno_doplacilo:,.2f} €")
    st.subheader(f"Končni NETO: {pdpz_kapital - dejanski_davek_pdpz:,.2f} €")
    st.caption(f"Skupna obdavčitev odkupa znaša {round((dejanski_davek_pdpz/pdpz_kapital)*100, 1)} %.")

with col2:
    st.success("### 🟢 MESEČNA RENTA")
    st.write(f"**Bruto mesečna renta:** {renta_mes_bruto:,.2f} €")
    if akontacija_renta > 0:
        st.write(f"**Mesečna akontacija (12,5%):** -{akontacija_renta:,.2f} €")
    else:
        st.write("**Mesečna akontacija:** 0,00 € (pod pragom 160€)")
    
    neto_renta_letno = letna_renta_bruto - dejanski_davek_renta
    st.subheader(f"Povprečni NETO: {neto_renta_letno/12:,.2f} €/mes")
    st.caption(f"Skupna obdavčitev rente znaša le {round((dejanski_davek_renta/letna_renta_bruto)*100, 1) if letna_renta_bruto > 0 else 0} %.")

st.divider()

# --- KRITIČNA ARGUMENTACIJA ---
st.subheader("Kaj to pomeni za vašo denarnico?")
razlika = dejanski_davek_pdpz - dejanski_davek_renta
st.info(f"""
Zaradi progresivne lestvice v letu 2026 in ugodnosti 50% obdavčitve rente (čl. 42 ZDoh-2), 
stranka z izbiro rente obdrži **{razlika:,.2f} €** več, kot če bi se odločila za enkratni odkup.
""")

st.warning("""
**Opomba za svetovalca:** Pri enkratnem odkupu se po zakonu o PDPZ takoj odvede 25% akontacije, 
vendar izračun zgoraj kaže, da bo stranka zaradi prehoda v višji davčni razred verjetno 
morala doplačati razliko ob letni dohodninski napovedi.
""")
