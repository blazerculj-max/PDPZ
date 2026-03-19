import streamlit as st

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # 1. LINEARNA SPLOŠNA OLAJŠAVA (Izboljšava št. 1)
    # Če so prihodki pod določeno mejo (cca 16.000€), se olajšava linearno poveča.
    # Uporabljamo formulo, ki približno odraža progresivno povečanje splošne olajšave.
    osnovna_splosna = 5500.0  # Fiksni del za leto 2026
    if bruto_vsi <= 16000:
        dodatna_splosna = max(0, 18700 - 1.16875 * bruto_vsi) # Formula za linearno povečanje
        splosna_olajsava_koncna = osnovna_splosna + dodatna_splosna
    else:
        splosna_olajsava_koncna = osnovna_splosna

    # Seniorska olajšava (nad 70 let)
    seniorska_letna = 1600.0 if starost >= 70 else 0.0
    
    # Prispevki (OZP in 1% dolgotrajna oskrba)
    ozp_letni = 37.17 * 12 
    pdo_stopnja = 0.01
    prispevki_pok_letni = ozp_letni + (bruto_pok_letna * pdo_stopnja)
    
    # Davčna osnova
    osnova = max(0, bruto_vsi - prispevki_pok_letni - splosna_olajsava_koncna - seniorska_letna)
    
    # Dohodninska lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # Pokojninska olajšava (13,5% od bruto pokojnine)
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz)

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Svetovalec 2026", layout="wide")
st.title("🛡️ Davčni optimizator: Enkratni odkup vs. Dosmrtna renta (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("1. Letni prihodki")
    prihodki_delo = st.number_input("Bruto prihodki iz dela (plače, regres...) (€)", value=8000.0)
    st_mesecev_pok = st.slider("Mesecev pokojnine v tem letu", 1, 12, 9)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    starost = st.number_input("Starost stranke ob koncu leta", min_value=50, max_value=100, value=65)

    st.header("2. Podatki o PDPZ")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0)
    
    st.subheader("Parametri Rente")
    zajamcena_leta = st.number_input("Zajamčena doba (leta)", min_value=0.0, value=10.0, step=0.5)
    renta_zajamcena = st.number_input("Renta v zajamčeni dobi (€)", value=120.0)
    renta_po_zajamceni = st.number_input("Renta po zajamčeni dobi (€)", value=100.0)
    
    do_leta = st.number_input("Izračunaj skupno izplačilo do leta", value=85)

# --- IZRAČUNI ---
letna_pok_bruto = bruto_pok_mes * st_mesecev_pok
skupni_redne_osnove = prihodki_delo + letna_pok_bruto
davek_osnovni = izracun_dohodnine_2026(skupni_redne_osnove, letna_pok_bruto, starost)

# SCENARIJ: ODKUP
izstopni_stroski = pdpz_kapital * 0.01
osnova_za_davek_odkup = pdpz_kapital - izstopni_stroski
akontacija_takoj_25 = osnova_za_davek_odkup * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(skupni_redne_osnove + osnova_za_davek_odkup, letna_pok_bruto, starost)
dejanski_davek_pdpz = davek_skupaj_odkup - davek_osnovni
neto_odkup_koncni = osnova_za_davek_odkup - dejanski_davek_pdpz
efektivna_stopnja_odkup = (dejanski_davek_pdpz + izstopni_stroski) / pdpz_kapital

# SCENARIJ: RENTA
letna_renta_bruto_leto1 = renta_zajamcena * st_mesecev_pok
davek_skupaj_renta = izracun_dohodnine_2026(skupni_redne_osnove + (letna_renta_bruto_leto1 * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta = davek_skupaj_renta - davek_osnovni
efektivna_stopnja_renta = dejanski_davek_renta / letna_renta_bruto_leto1 if letna_renta_bruto_leto1 > 0 else 0

# Projekcija izplačil
mesecev_zajamcena = zajamcena_leta * 12
mesecev_po_zajamceni = max(0, ((do_leta - starost) * 12) - mesecev_zajamcena)
skupno_ven_renta = (mesecev_zajamcena * renta_zajamcena * (1 - efektivna_stopnja_renta)) + \
                   (mesecev_po_zajamceni * renta_po_zajamceni * (1 - efektivna_stopnja_renta))

# --- PRIKAZ REZULTATOV ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 ENKRATNI ODKUP")
    st.metric("Končni NETO izplen", f"{neto_odkup_koncni:,.2f} €")
    st.metric("Efektivna obdavčitev", f"{round(efektivna_stopnja_odkup * 100, 2)} %")
    st.write(f"**Takojšnje izplačilo (TRR):** {osnova_za_davek_odkup - akontacija_takoj_25:,.2f} €")
    st.write(f"**Poračun dohodnine:** -{max(0, dejanski_davek_pdpz - akontacija_takoj_25):,.2f} €")

with col2:
    st.success("### 🟢 MESEČNA RENTA")
    st.metric(f"Skupaj do {do_leta}. leta (NETO)", f"{skupno_ven_renta:,.2f} €")
    st.metric("Efektivna obdavčitev", f"{round(efektivna_stopnja_renta * 100, 2)} %")
    st.write(f"**Neto renta (zajamčena):** {renta_zajamcena * (1 - efektivna_stopnja_renta):,.2f} €/mes")
    st.write(f"**Neto renta (dosmrtna):** {renta_po_zajamceni * (1 - efektivna_stopnja_renta):,.2f} €/mes")

st.divider()

# --- PREGLEDNA TABELA ---
st.subheader("📊 Primerjalni pregled")
tabela_podatki = {
    "Parameter": ["Bruto osnova", "Izstopni stroški (1%)", "Skupna dohodnina", "Efektivna stopnja davka", "Končni neto prejemek"],
    "Enkratni odkup": [
        f"{pdpz_kapital:,.2f} €",
        f"-{izstopni_stroski:,.2f} €",
        f"-{dejanski_davek_pdpz:,.2f} €",
        f"{round(efektivna_stopnja_odkup * 100, 2)} %",
        f"{neto_odkup_koncni:,.2f} €"
    ],
    "Mesečna renta (Skupaj)": [
        f"{(mesecev_zajamcena * renta_zajamcena + mesecev_po_zajamceni * renta_po_zajamceni):,.2f} €",
        "0.00 €",
        f"-{(mesecev_zajamcena * renta_zajamcena + mesecev_po_zajamceni * renta_po_zajamceni) * efektivna_stopnja_renta:,.2f} €",
        f"{round(efektivna_stopnja_renta * 100, 2)} %",
        f"{skupno_ven_renta:,.2f} €"
    ]
}
st.table(tabela_podatki)

# --- OPOZORILO O SOCIALNIH TRANSFERJIH (Izboljšava št. 2) ---
st.warning("⚠️ **POZOR – Vpliv na socialne transferje:** Enkratno izplačilo poveča vaše premoženje in letni dohodek. To lahko povzroči izgubo ali zmanjšanje varstvenega dodatka, državne pokojnine ali povišanje plačila za institucionalno varstvo (dom upokojencev).")

st.markdown("---")
st.caption("Izračun temelji na informativnih podatkih zakonodaje 2026. Upoštevajte, da se dohodnina dokončno ugotovi z odločbo FURS.")
