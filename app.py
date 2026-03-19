import streamlit as st

# Nastavitve strani
st.set_page_config(page_title="Davčni Kalkulator Upokojitev 2026", layout="wide")

def izracun_dohodnine(bruto_osnova, pokojnina_bruto, starost):
    # Konstante za leto 2026
    SPLUSNA_OLAJŠAVA = 5500
    SENIORSKA_OLAJŠAVA = 1600 if starost >= 70 else 0
    
    # 1. Izračun neto davčne osnove
    davčna_osnova = max(0, bruto_osnova - SPLUSNA_OLAJŠAVA - SENIORSKA_OLAJŠAVA)
    
    # 2. Dohodninska lestvica (predvideni razredi 2026)
    davek = 0
    if davčna_osnova <= 9000:
        davek = davčna_osnova * 0.16
    elif davčna_osnova <= 25000:
        davek = 1440 + (davčna_osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (davčna_osnova - 25000) * 0.33
        
    # 3. Pokojninska olajšava (13,5% od bruto pokojnine) - zmanjša odmerjeno dohodnino
    olajšava_zpiz = pokojnina_bruto * 0.135
    koncni_davek = max(0, davek - olajšava_zpiz)
    
    return round(koncni_davek, 2)

# --- UI APPLIKACIJE ---
st.title("📊 Davčni optimizator: Odkup vs. Renta (2026)")
st.markdown("""
Ta aplikacija pomaga svetovalcem prikazati razliko v obdavčitvi med enkratnim dvigom PDPZ in dosmrtno rento.
""")

with st.sidebar:
    st.header("Vhodni podatki")
    starost = st.number_input("Starost stranke (v letu odmere)", min_value=50, max_value=100, value=65)
    
    st.subheader("Prihodki iz dela")
    mesci_delo = st.slider("Število mesecev zaposlitve v letu", 0, 12, 3)
    placa_bruto = st.number_input("Mesečna bruto plača (€)", value=2500)
    regres = st.number_input("Regres (obdavčljivi del) (€)", value=0)
    
    st.subheader("Pokojnina")
    pokojnina_bruto_mes = st.number_input("Mesečna bruto pokojnina (€)", value=1200)
    
    st.subheader("PDPZ Sredstva")
    pdpz_znesek = st.number_input("Skupni znesek na PDPZ računu (€)", value=20000)
    renta_mesecna = st.number_input("Potencialna mesečna renta (€)", value=100)

# --- LOGIKA IZRAČUNA ---
mesci_pokoj = 12 - mesci_delo
letna_placa = mesci_delo * placa_bruto + regres
letna_pokojnina = mesci_pokoj * pokojnina_bruto_mes

# Scenarij 1: Enkratni odkup
osnova_odkup = letna_placa + letna_pokojnina + pdpz_znesek
davek_odkup = izracun_dohodnine(osnova_odkup, letna_pokojnina, starost)
neto_odkup_pdpz = pdpz_znesek - (davek_odkup - izracun_dohodnine(letna_placa + letna_pokojnina, letna_pokojnina, starost))

# Scenarij 2: Renta (všteje se le 50%)
letna_renta = renta_mesecna * mesci_pokoj
osnova_renta = letna_placa + letna_pokojnina + (letna_renta * 0.5)
davek_renta = izracun_dohodnine(osnova_renta, letna_pokojnina, starost)

# --- PRIKAZ REZULTATOV ---
col1, col2 = st.columns(2)

with col1:
    st.error("### SCENARIJ: Enkratni odkup")
    st.metric("Skupna letna dohodnina", f"{davek_odkup:,.2f} €")
    st.write(f"Celoten znesek **{pdpz_znesek} €** se prišteje k vašim prihodkom, kar vas lahko potisne v višji davčni razred.")
    st.caption("Pazi: Akontacija 25% pogosto ne pokrije celotnega dolga do države!")

with col2:
    st.success("### SCENARIJ: Mesečna renta")
    st.metric("Skupna letna dohodnina", f"{davek_renta:,.2f} €")
    st.write(f"V davčno osnovo gre le **50% rente** ({letna_renta * 0.5} €).")
    st.write(f"Prihranek pri dohodnini: **{round(davek_odkup - davek_renta, 2)} €**")

st.divider()

# Grafični prikaz (opcijsko)
st.subheader("Vizualna primerjava obdavčitve")
razlika = davek_odkup - davek_renta
st.info(f"Z izbiro rente stranka na letni ravni obdrži **{razlika:,.2f} €** več denarja zaradi davčne optimizacije (člen 42. ZDoh-2).")

st.markdown("---")
st.caption("Izračun je informativne narave in temelji na zakonodaji PISRS (ZDoh-2) in ZPIZ za leto 2026.")
