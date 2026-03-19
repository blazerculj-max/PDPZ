import streamlit as st

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    SPLUSNA_LETNA = 438.33 * 12
    SENIORSKA_LETNA = 131.50 * 12 if starost >= 70 else 0
    OZP_LETNI = 37.17 * 12 
    PDO_STOPNJA = 0.01
    
    prispevki_pok_letni = OZP_LETNI + (bruto_pok_letna * PDO_STOPNJA)
    osnova = max(0, bruto_vsi - prispevki_pok_letni - SPLUSNA_LETNA - SENIORSKA_LETNA)
    
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    olajsava_zpiz = bruto_pok_letna * 0.135
    return max(0, davek - olajsava_zpiz)

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Optimizator 2026", layout="wide")
st.title("🛡️ Davčni kalkulator: Enkratni odkup vs. Dosmrtna renta (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("1. Prihodki v letu upokojitve")
    prihodki_delo = st.number_input("Bruto prihodki iz dela (plače, regres...) (€)", value=8000.0)
    st_mesecev_pok = st.slider("Mesecev pokojnine v tem letu", 1, 12, 9)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    starost = st.number_input("Starost stranke ob koncu leta", min_value=50, max_value=100, value=65)

    st.header("2. Podatki o PDPZ")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0)
    
    st.subheader("Parametri Rente")
    zajamcena_leta = st.number_input("Zajamčena doba izplačevanja (leta)", min_value=0.0, value=10.0, step=0.5)
    renta_zajamcena = st.number_input("Znesek rente v zajamčeni dobi (€)", value=120.0)
    renta_po_zajamceni = st.number_input("Znesek rente po zajamčeni dobi (€)", value=100.0)
    
    st.header("3. Projekcija življenjske dobe")
    do_leta = st.number_input("Izračunaj skupno izplačilo do leta", value=85)

# --- IZRAČUNI OSNOVE ZA DOHODNINO ---
letna_pok_bruto = bruto_pok_mes * st_mesecev_pok
skupni_redne_osnove = prihodki_delo + letna_pok_bruto
davek_osnovni = izracun_dohodnine_2026(skupni_redne_osnove, letna_pok_bruto, starost)

# --- SCENARIJ: ENKRATNI ODKUP ---
akontacija_takoj_25 = pdpz_kapital * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(skupni_redne_osnove + pdpz_kapital, letna_pok_bruto, starost)
dejanski_davek_na_pdpz = davek_skupaj_odkup - davek_osnovni
neto_odkup_koncni = pdpz_kapital - dejanski_davek_na_pdpz

# --- SCENARIJ: RENTA (Davčni izračun za prvo leto) ---
# Za davčni izračun vzamemo trenutno rento (v zajamčeni dobi)
letna_renta_bruto_leto1 = renta_zajamcena * st_mesecev_pok
davek_skupaj_renta = izracun_dohodnine_2026(skupni_redne_osnove + (letna_renta_bruto_leto1 * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta_leto1 = davek_skupaj_renta - davek_osnovni
akontacija_renta_125 = renta_zajamcena * 0.125 if renta_zajamcena >= 160 else 0

# --- PROJEKCIJA "KOLIKO DOBIM VEN" ---
# 1. Odkup: Stranka dobi neto takoj in konec.
# 2. Renta: Vsota vseh neto izplačil do ciljnega leta.
leta_prejemanja = max(0, do_leta - starost)
mesecev_skupaj = leta_prejemanja * 12

mesecev_zajamcena = zajamcena_leta * 12
mesecev_po_zajamceni = max(0, mesecev_skupaj - mesecev_zajamcena)

# Poenostavljen izračun neto rente (povprečna obdavčitev skozi leta)
efektivna_stopnja_renta = dejanski_davek_renta_leto1 / letna_renta_bruto_leto1 if letna_renta_bruto_leto1 > 0 else 0
neto_renta_zajam = renta_zajamcena * (1 - efektivna_stopnja_renta)
neto_renta_po = renta_po_zajamceni * (1 - efektivna_stopnja_renta)

skupno_ven_renta = (mesecev_zajamcena * neto_renta_zajam) + (mesecev_po_zajamceni * neto_renta_po)

# --- PRIKAZ REZULTATOV ---
st.divider()
st.subheader(f"Primerjava neto izplačil do {do_leta}. leta starosti")

col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 ENKRATNI ODKUP")
    st.metric("Dejanski neto (po vseh davkih)", f"{neto_odkup_koncni:,.2f} €")
    st.write(f"**Takojšnje nakazilo (akontacija):** {pdpz_kapital - akontacija_takoj_25:,.2f} €")
    st.write(f"**Poračun dohodnine:** -{max(0, dejanski_davek_na_pdpz - akontacija_takoj_25):,.2f} €")
    st.write(f"**Izguba zaradi davkov:** {dejanski_davek_na_pdpz:,.2f} € ({round((dejanski_davek_na_pdpz/pdpz_kapital)*100, 1)}%)")

with col2:
    st.success("### 🟢 MESEČNA RENTA")
    st.metric("Predvideno skupno neto izplačilo", f"{skupno_ven_renta:,.2f} €")
    st.write(f"**Zajamčena doba ({zajamcena_leta} let):** {renta_zajamcena} € bruto/mes")
    st.write(f"**Po zajamčeni dobi:** {renta_po_zajamceni} € bruto/mes")
    
    if akontacija_renta_125 > 0:
        st.caption(f"Upoštevan mesečni odtegljaj akontacije: {akontacija_renta_125:,.2f} €")
    else:
        st.caption("Brez mesečnega odtegljaja akontacije (renta pod 160€).")

st.divider()

# --- VIZUALIZACIJA ZA STRANKO ---
st.subheader("📊 Kaj se bolj splača?")
razlika_total = skupno_ven_renta - neto_odkup_koncni

if razlika_total > 0:
    st.info(f"Če stranka dočaka {do_leta} let, bo z rento prejela **{razlika_total:,.2f} € VEČ** kot z enkratnim odkupom.")
else:
    st.warning(f"Z enkratnim odkupom stranka dobi **{abs(razlika_total):,.2f} € VEČ**, vendar prevzame tveganje hitre porabe sredstev.")

st.markdown(f"""
**Zakaj je renta boljša?**
1. **Davčni prihranek:** Pri renti plačate le cca. **{round(efektivna_stopnja_renta*100, 1)}%** davka, pri odkupu pa **{round((dejanski_davek_na_pdpz/pdpz_kapital)*100, 1)}%**.
2. **Dosmrtnost:** Tudi če stranka živi do 100. leta, se renta po zajamčeni dobi še vedno izplačuje.
3. **Varnost:** Zajamčena doba ({zajamcena_leta} let) zagotavlja, da se v primeru smrti preostanek izplača dedičem.
""")
