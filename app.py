import streamlit as st

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # Parametri 2026 iz uradnih tabel
    SPLUSNA_LETNA = 438.33 * 12
    SENIORSKA_LETNA = 131.50 * 12 if starost >= 70 else 0
    
    OZP_LETNI = 37.17 * 12 # Obvezni zdravstveni prispevek
    PDO_STOPNJA = 0.01     # 1% prispevek za dolgotrajno oskrbo
    
    # 1. Prispevki (obračunani od pokojnine)
    # Opomba: Prispevki od plače so že odšteti v bruto-bruto osnovi, 
    # tukaj upoštevava tiste, ki bremenijo pokojnino.
    prispevki_pok_letni = OZP_LETNI + (bruto_pok_letna * PDO_STOPNJA)
    
    # 2. Zmanjšana davčna osnova
    osnova = max(0, bruto_vsi - prispevki_pok_letni - SPLUSNA_LETNA - SENIORSKA_LETNA)
    
    # 3. Dohodninska lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # 4. Pokojninska olajšava (13,5% od bruto pokojnine)
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz)

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Optimizator 2026", layout="wide")
st.title("🛡️ Davčni kalkulator: Prehod v pokoj & PDPZ (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("1. Prihodki pred upokojitvijo")
    prihodki_delo = st.number_input("Vsi bruto prihodki iz dela v tem letu (€)", 
                                    help="Vpišite vsoto vseh bruto plač, regresov in odpravnin pred upokojitvijo.",
                                    value=8000.0)
    
    st.header("2. Podatki o pokojnini")
    st.info("Svetovalec sam določi število mesecev prejemanja.")
    st_mesecev_pok = st.slider("Število mesecev prejemanja pokojnine", 1, 12, 9)
    bruto_pok_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1700.0)
    
    st.header("3. Podatki o PDPZ")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0)
    renta_mes_bruto = st.number_input("Mesečna bruto renta (€)", value=400.0)
    
    starost = st.number_input("Starost stranke ob koncu leta", min_value=50, max_value=100, value=65)

# --- IZRAČUNI OSNOVE ---
letna_pok_bruto = bruto_pok_mes * st_mesecev_pok
skupni_redne_osnove = prihodki_delo + letna_pok_bruto

# Osnovni davek brez PDPZ vpliva
davek_osnovni = izracun_dohodnine_2026(skupni_redne_osnove, letna_pok_bruto, starost)

# SCENARIJ: ENKRATNI ODKUP
akontacija_takoj_25 = pdpz_kapital * 0.25
davek_skupaj_odkup = izracun_dohodnine_2026(skupni_redne_osnove + pdpz_kapital, letna_pok_bruto, starost)
dejanski_davek_na_pdpz = davek_skupaj_odkup - davek_osnovni
doplacilo_ob_poracunu = max(0, dejanski_davek_na_pdpz - akontacija_takoj_25)

# SCENARIJ: RENTA
# Renta se prejema toliko mesecev kot pokojnina
letna_renta_bruto = renta_mes_bruto * st_mesecev_pok
davek_skupaj_renta = izracun_dohodnine_2026(skupni_redne_osnove + (letna_renta_bruto * 0.5), letna_pok_bruto, starost)
dejanski_davek_renta = davek_skupaj_renta - davek_osnovni
akontacija_renta_125 = renta_mes_bruto * 0.125 if renta_mes_bruto >= 160 else 0

# --- PRIKAZ REZULTATOV ---
st.divider()
st.subheader(f"Analiza prehoda: {12 - st_mesecev_pok} mes. dela + {st_mesecev_pok} mes. pokojnine")

col1, col2 = st.columns(2)

with col1:
    st.error("### 🔴 SCENARIJ: Enkratni odkup")
    st.markdown(f"**Bruto znesek na PDPZ:** {pdpz_kapital:,.2f} €")
    st.markdown(f"**Takojšen odtegljaj (25%):** -{akontacija_takoj_25:,.2f} €")
    st.subheader(f"Takojšnje izplačilo: {pdpz_kapital - akontacija_takoj_25:,.2f} €")
    st.write("---")
    st.write(f"**Predviden letni poračun (DOPLAČILO):** -{doplacilo_ob_poracunu:,.2f} €")
    st.info(f"Dejanski neto po vseh davkih: **{pdpz_kapital - dejanski_davek_na_pdpz:,.2f} €**")
    st.caption(f"Efektivna obdavčitev odkupa v tem letu: {round((dejanski_davek_na_pdpz/pdpz_kapital)*100, 1)}%")

with col2:
    st.success("### 🟢 SCENARIJ: Mesečna renta")
    st.markdown(f"**Bruto mesečna renta:** {renta_mes_bruto:,.2f} €")
    if akontacija_renta_125 > 0:
        st.write(f"**Mesečni odtegljaj akontacije (12,5%):** -{akontacija_renta_125:,.2f} €")
        st.subheader(f"Mesečno neto: {renta_mes_bruto - akontacija_renta_125:,.2f} €")
    else:
        st.subheader(f"Mesečno neto: {renta_mes_bruto:,.2f} €")
    
    st.write("---")
    neto_renta_letna = letna_renta_bruto - dejanski_davek_renta
    st.write(f"**Realni neto donos rente (povprečje):** {neto_renta_letna/st_mesecev_pok:,.2f} €/mes")
    st.caption(f"Efektivna obdavčitev rente: {round((dejanski_davek_renta/letna_renta_bruto)*100, 1) if letna_renta_bruto > 0 else 0}%")

st.divider()

# --- KRITIČNI RAZMISLEK ---
razlika = dejanski_davek_na_pdpz - dejanski_davek_renta
st.markdown(f"### 💡 Zaključek svetovalca")
st.warning(f"""
Ker je stranka v tem letu prejela še **{prihodki_delo:,.2f} € plače**, je njena davčna osnova že visoka. 
Enkratni odkup bi bil letos davčno izjemno neugoden, saj bi večina zneska padla v 26 % ali 33 % razred. 
Z izbiro rente stranka prihrani **{razlika:,.2f} €** pri dohodnini.
""")

if starost >= 70:
    st.info("ℹ️ Upoštevana je seniorska olajšava za stranke nad 70 let.")
