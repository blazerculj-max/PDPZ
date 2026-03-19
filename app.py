import streamlit as st

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # 1. Linearna splošna olajšava (Natančnejši izračun za 2026)
    osnovna_splosna = 5500.0
    if bruto_vsi <= 16000:
        dodatna_splosna = max(0, 18700 - 1.16875 * bruto_vsi)
        splosna_olajsava_koncna = osnovna_splosna + dodatna_splosna
    else:
        splosna_olajsava_koncna = osnovna_splosna

    # 2. Seniorska olajšava (70 let+)
    seniorska_letna = 1600.0 if starost >= 70 else 0.0
    
    # 3. Prispevki (OZP 37,17€ in 1% dolgotrajna oskrba)
    ozp_letni = 37.17 * 12 
    pdo_stopnja = 0.01
    prispevki_pok_letni = ozp_letni + (bruto_pok_letna * pdo_stopnja)
    
    # 4. Davčna osnova
    osnova = max(0, bruto_vsi - prispevki_pok_letni - splosna_olajsava_koncna - seniorska_letna)
    
    # 5. Dohodninska lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # 6. Pokojninska olajšava (13,5% od bruto pokojnine)
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz)

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Svetovalec Pro 2026", layout="wide")
st.title("🛡️ Finančni & Davčni Optimizator PDPZ (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("1. Letni prihodki v letu upokojitve")
    prihodki_delo = st.number_input("Bruto prihodki iz dela (plače, regres...) (€)", value=8000.0)
    st_mesecev_pok = st.slider("Mesecev pokojnine v tem letu", 1, 12, 9)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    starost = st.number_input("Starost stranke ob koncu leta", min_value=50, max_value=100, value=65)

    st.header("2. Sredstva PDPZ")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0)
    
    st.subheader("Parametri Rente")
    zajamcena_leta = st.number_input("Zajamčena doba izplačevanja (leta)", min_value=0.0, value=20.0, step=0.5)
    renta_zajamcena = st.number_input("Znesek polne rente (zajamčena) (€)", value=120.0)
    renta_po_zajamceni = st.number_input("Znesek rente po zajamčeni dobi (€)", value=100.0)
    
    st.subheader("Možnost Predujma (Triglav)")
    znesek_predujma = st.number_input("Znesek predujma (avansa) (€)", value=10000.0)
    mesci_vracila = st.number_input("Doba vračila predujma (v mesecih)", value=200.2)
    obrestna_mera = st.slider("Pričakovan donos investicije (%)", 0.0, 10.0, 5.0)
    leta_investiranja = st.number_input("Leta investiranja predujma", value=10)

# --- IZRAČUNI OSNOVE ---
letna_pok_bruto = bruto_pok_mes * st_mesecev_pok
skupni_redne_osnove = prihodki_delo + letna_pok_bruto
davek_osnovni = izracun_dohodnine_2026(skupni_redne_osnove, letna_pok_bruto, starost)

# SCENARIJ 1: ODKUP
izstopni_stroski = pdpz_kapital * 0.01
osnova_za_davek_odkup = pdpz_kapital - izstopni_stroski
akontacija_takoj_25 = osnova_za_davek_odkup * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(skupni_redne_osnove + osnova_za_davek_odkup, letna_pok_bruto, starost)
dejanski_davek_pdpz = davek_skupaj_odkup - davek_osnovni
neto_odkup_koncni = osnova_za_davek_odkup - dejanski_davek_pdpz

# SCENARIJ 2: RENTA
letna_renta_bruto_leto1 = renta_zajamcena * st_mesecev_pok
davek_skupaj_renta = izracun_dohodnine_2026(skupni_redne_osnove + (letna_renta_bruto_leto1 * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta = davek_skupaj_renta - davek_osnovni
efektivna_stopnja_renta = dejanski_davek_renta / letna_renta_bruto_leto1 if letna_renta_bruto_leto1 > 0 else 0

# SCENARIJ 3: PREDUJEM (Davčna obravnava kot renta!)
# Akontacija na predujem je 12.5% (ker je 25% od 50% osnove)
neto_predujem_takoj = znesek_predujma * (1 - 0.125)
prihodnost_predujma = neto_predujem_takoj * (1 + (obrestna_mera/100)) ** leta_investiranja

# --- PRIKAZ REZULTATOV ---
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.error("### 🔴 ENKRATNI ODKUP")
    st.metric("Končni NETO izplen", f"{neto_odkup_koncni:,.2f} €")
    st.metric("Efektivna obdavčitev", f"{round(((dejanski_davek_pdpz + izstopni_stroski)/pdpz_kapital)*100, 1)} %")
    st.caption(f"Vključuje 1% stroškov in poračun dohodnine.")

with c2:
    st.success("### 🟢 KLASIČNA RENTA")
    st.metric("Neto mesečno (zajamčena)", f"{renta_zajamcena * (1 - efektivna_stopnja_renta):,.2f} €")
    st.metric("Efektivna obdavčitev", f"{round(efektivna_stopnja_renta * 100, 1)} %")
    st.caption("Ugodnost 50% davčne osnove po čl. 42 ZDoh-2.")

with c3:
    st.info("### 🔵 PREDUJEM + INV.")
    st.metric(f"Vrednost investicije ({leta_investiranja} let)", f"{prihodnost_predujma:,.2f} €")
    st.write(f"Neto predujem danes: **{neto_predujem_takoj:,.2f} €**")
    st.caption(f"Pri {obrestna_mera}% donosu.")

st.divider()

# --- PREGLEDNA TABELA ---
st.subheader("📊 Primerjalni pregled scenarijev")
ostanek_zajamcene = max(0, (zajamcena_leta * 12) - mesci_vracila)

tabela_podatki = {
    "Parameter": ["Davčna osnova", "Izstopni stroški", "Likvidnost (takoj)", "Efektivna obdavčitev"],
    "Enkratni odkup": ["100% zneska", "1%", f"{neto_odkup_koncni:,.2f} €", f"{round(((dejanski_davek_pdpz + izstopni_stroski)/pdpz_kapital)*100, 1)} %"],
    "Predujem + Investiranje": ["50% zneska", "0%", f"{neto_predujem_takoj:,.2f} €", "cca. 12.5%"],
    "Klasična renta": ["50% zneska", "0%", "0 €", f"{round(efektivna_stopnja_renta * 100, 1)} %"]
}
st.table(tabela_podatki)

# --- POSEBNO OPOZORILO ---
st.warning(f"ℹ️ **Logika predujma:** Stranka vrne predujem v {mesci_vracila} mesecih (nižja renta). Nato še {round(ostanek_zajamcene, 1)} mesecev prejema povišano polno rento iz zajamčene dobe, nato pa dosmrtno rento {renta_po_zajamceni} €.")

st.warning("⚠️ **Vpliv na socialne transferje:** Enkratni odkup poveča premoženje in letni dohodek, kar lahko vpliva na varstveni dodatek ali plačilo doma upokojencev.")

st.markdown("---")
st.caption("Izračun je informativne narave za leto 2026. Seniorska olajšava in linearna splošna olajšava sta upoštevani.")
