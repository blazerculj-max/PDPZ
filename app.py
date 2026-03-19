import streamlit as st

# --- FUNKCIJA ZA IZRAČUN PO LOGIKI ZPIZ (2026) ---
def izracun_zpiz_dohodnina(bruto_dohodek_vsi, bruto_pokojnina_letna, starost):
    # Mesečni parametri iz tvojih slik
    SPLUSNA_MESEČNA = 438.33
    SENIORSKA_MESEČNA = 131.50 if starost >= 70 else 0.0
    OZP_MESEČNI = 37.17
    PDO_STOPNJA = 0.01  # 1% za dolgotrajno oskrbo
    
    # Preračun na letno raven
    letna_splosna = SPLUSNA_MESEČNA * 12
    letna_seniorska = SENIORSKA_MESEČNA * 12
    letni_ozp = OZP_MESEČNI * 12
    letni_pdo = bruto_pokojnina_letna * PDO_STOPNJA
    
    # 1. Zmanjšana davčna osnova (Bruto - Prispevki - Olajšave)
    osnova = max(0, bruto_dohodek_vsi - letni_ozp - letni_pdo - letna_splosna - letna_seniorska)
    
    # 2. Obračun dohodnine po lestvici (informativni razredi)
    if osnova <= 9000:
        davek_po_lestvici = osnova * 0.16
    elif osnova <= 25000:
        davek_po_lestvici = 1440 + (osnova - 9000) * 0.26
    else:
        davek_po_lestvici = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # 3. Pokojninska olajšava (13,5% od bruto pokojnine)
    pokojninska_olajsava = bruto_pokojnina_letna * 0.135
    
    # Končni znesek (ne more biti manj kot 0)
    koncni_davek = max(0, davek_po_lestvici - pokojninska_olajsava)
    return round(koncni_davek, 2)

# --- STREAMLIT UI ---
st.set_page_config(page_title="ZPIZ Kalkulator 2026", layout="centered")
st.title("🛡️ Svetovalec: Optimizacija PDPZ")

# Vnosi
col_a, col_b = st.columns(2)
with col_a:
    starost = st.number_input("Starost stranke", value=65)
    bruto_pok_mesec = st.number_input("Bruto pokojnina (mesečno) €", value=1700.0)
with col_b:
    pdpz_kapital = st.number_input("Sredstva na PDPZ računu €", value=20000.0)
    renta_mesec = st.number_input("Ponujena mesečna renta €", value=100.0)

# Izračun osnovnih letnih prihodkov (brez PDPZ)
letna_pok_bruto = bruto_pok_mesec * 12
davek_brez = izracun_zpiz_dohodnina(letna_pok_bruto, letna_pok_bruto, starost)

# SCENARIJ 1: Enkratni odkup
davek_odkup = izracun_zpiz_dohodnina(letna_pok_bruto + pdpz_kapital, letna_pok_bruto, starost)
dodaten_davek_odkup = davek_odkup - davek_brez

# SCENARIJ 2: Renta (50% obdavčitev)
letna_renta_bruto = renta_mesec * 12
davek_renta = izracun_zpiz_dohodnina(letna_pok_bruto + (letna_renta_bruto * 0.5), letna_pok_bruto, starost)
dodaten_davek_renta = davek_renta - davek_brez

# --- PRIKAZ ZA STRANKO ---
st.divider()
st.subheader("Primerjava dodatnega davka")

c1, c2 = st.columns(2)
c1.metric("Enkratni odkup", f"{dodaten_davek_odkup:,.2f} €", delta="DAVEK", delta_color="inverse")
c2.metric("Mesečna renta", f"{dodaten_davek_renta:,.2f} €", delta="DAVEK", delta_color="normal")

st.info(f"**Nasvet:** Z izbiro rente stranka prihrani **{dodaten_davek_odkup - dodaten_davek_renta:,.2f} €** pri dohodnini.")

if starost < 70:
    st.warning(f"Stranka je mlajša od 70 let, zato ne koristi seniorske olajšave (131,50 €/mesec). To pomeni, da vsak dodaten dohodek (odkup) hitreje zapade v višjo obdavčitev.")
