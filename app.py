import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KOMPLEKSOWA BAZA KURIERÓW (Z Twojego kodu) ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Paczkomat A": {"L": 64, "W": 38, "H": 8, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat B": {"L": 64, "W": 38, "H": 19, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "GLS (Polska)": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "UPS Standard": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"},
    "FedEx Polska": {"max_L": 175, "max_G": 330, "max_W": 35.0, "color": "#4d148c"},
    "Pocztex (Poczta Polska)": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#ee1d23"},
    "Geis": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#004a99"},
    "Meest": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#25b14b"},
    "TNT (Express)": {"max_L": 240, "max_G": 400, "max_W": 30.0, "color": "#ff6600"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5, "color": "#1f77b4"},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0, "color": "#2ca02c"},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0, "color": "#ff7f0e"},
    "Karton Fasonowy (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2, "color": "#9467bd"},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0, "color": "#7f7f7f"}
}

st.set_page_config(page_title="Gropak - MultiProdukt", layout="wide")
st.title("📦 Gropak: System Pakowania Wieloproduktowego")

# --- KOSZYK (SESSION STATE) ---
if 'koszyk' not in st.session_state:
    st.session_state.koszyk = []

with st.sidebar:
    st.header("1. Kompletowanie zamówienia")
    wybrane = st.selectbox("Dodaj produkt do listy:", list(PUDEŁKA_GROPAK.keys()))
    
    if wybrane == "Własny wymiar...":
        L_cust = st.number_input("Dł (cm)", 1); W_cust = st.number_input("Szer (cm)", 1)
        H_cust = st.number_input("Wys (cm)", 1); Waga_cust = st.number_input("Waga (kg)", 0.1)
        current_prod = {"L": L_cust, "W": W_cust, "H": H_cust, "Waga": Waga_cust, "color": "#7f7f7f", "name": f"Własny {L_cust}x{W_cust}"}
    else:
        p = PUDEŁKA_GROPAK[wybrane]
        current_prod = {**p, "name": wybrane}

    sztuk = st.number_input("Ilość tej pozycji:", 1, 100, 1)
    
    if st.button("➕ Dodaj do paczki"):
        for _ in range(sztuk):
            st.session_state.koszyk.append(current_prod)
        st.success(f"Dodano {sztuk} szt.!")

    if st.button("🗑️ Wyczyść wszystko"):
        st.session_state.koszyk = []
        st.rerun()

    st.divider()
    st.header("2. Wybór przewoźnika")
    kurier_name = st.selectbox("Kurier:", list(KURIERZY.keys()))
    k = KURIERZY[kurier_name]

# --- FUNKCJA RYSOWANIA (Stacking różnych paczek) ---
def rysuj_paczke_3d(elementy, color_kurier):
    fig = go.Figure()
    
    # Sortujemy elementy: największa podstawa na dół
    sorted_items = sorted(elementy, key=lambda x: x['L'] * x['W'], reverse=True)
    
    curr_h = 0
    max_l, max_w = 0, 0
    total_w = 0
    
    for item in sorted_items:
        l, w, h = item['L'], item['W'], item['H']
        # Rysujemy bryłę produktu
        fig.add_trace(go.Mesh3d(
            x=[0, l, l, 0, 0, l, l, 0], y=[0, 0, w, w, 0, 0, w, w], z=[curr_h, curr_h, curr_h, curr_h, curr_h+h, curr_h+h, curr_h+h, curr_h+h],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            opacity=0.6, color=item['color'], name=item['name']
        ))
        # Krawędzie
        lines_x = [0, l, l, 0, 0, None, 0, l, l, 0, 0, None, 0, 0, None, l, l, None, l, l, None, 0, 0]
        lines_y = [0, 0, w, w, 0, None, 0, 0, w, w, 0, None, 0, 0, None, 0, 0, None, w, w, None, w, w]
        lines_z = [curr_h, curr_h, curr_h, curr_h, curr_h, None, curr_h+h, curr_h+h, curr_h+h, curr_h+h, curr_h+h, None, curr_h, curr_h+h, None, curr_h, curr_h+h, None, curr_h, curr_h+h, None, curr_h, curr_h+h]
        fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        max_l = max(max_l, l)
        max_w = max(max_w, w)
        curr_h += h
        total_w += item['Waga']

    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Dł', yaxis_title='Szer', zaxis_title='Wys'), margin=dict(l=0,r=0,b=0,t=0))
    return fig, max_l, max_w, curr_h, total_w

# --- LOGIKA I WIDOK ---
if st.session_state.koszyk:
    fig, fL, fW, fH, total_weight = rysuj_paczke_3d(st.session_state.koszyk, k['color'])
    
    # Obliczenia gabarytów
    ds = sorted([fL, fW, fH], reverse=True)
    girth = ds[0] + 2*ds[1] + 2*ds[2]
    
    # Walidacja
    if "Paczkomat" in kurier_name:
        ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"] and total_weight <= k["max_W"])
    else:
        ok = (ds[0] <= k["max_L"] and girth <= k["max_G"] and total_weight <= k["max_W"])

    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("🛠️ Instrukcja ułożenia")
        st.write("Produkty ułożone w stos (największe na spodzie):")
        for i, item in enumerate(reversed(sorted(st.session_state.koszyk, key=lambda x: x['L'] * x['W']))):
            st.write(f"{i+1}. {item['name']}")
            
        st.divider()
        if ok:
            st.success("✅ Paczka mieści się w limitach!")
        else:
            st.error(f"❌ Przekroczono limity {kurier_name}!")
            
        st.write(f"📊 **Dane paczki:**")
        st.write(f"- Wymiary: **{fL}x{fW}x{fH} cm**")
        st.write(f"- Waga: **{total_weight:.1f} kg**")
        if "Paczkomat" not in kurier_name:
            st.write(f"- Obwód (Girth): **{int(girth)} cm**")
            
    with c2:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Dodaj produkty z lewego panelu, aby zobaczyć wizualizację paczki.")
