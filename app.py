import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURACJA ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "GLS": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "UPS Standard": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"}
}

PRODUKTY_BAZA = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5, "color": "blue"},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0, "color": "green"},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0, "color": "orange"},
    "Fasonowe (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2, "color": "purple"}
}

st.set_page_config(page_title="Gropak - Multi-Packing", layout="wide")
st.title("📦 Gropak: System Pakowania Wieloproduktowego")

# --- ZARZĄDZANIE KOSZYKIEM ---
if 'koszyk' not in st.session_state:
    st.session_state.koszyk = []

def dodaj_do_koszyka(name, qty):
    for _ in range(qty):
        st.session_state.koszyk.append(PRODUKTY_BAZA[name])

def wyczysc_koszyk():
    st.session_state.koszyk = []

# --- PANEL BOCZNY ---
with st.sidebar:
    st.header("🛒 Kompletowanie zamówienia")
    wybrany_prod = st.selectbox("Produkt:", list(PRODUKTY_BAZA.keys()))
    ilosc = st.number_input("Ilość:", 1, 20, 1)
    
    if st.button("➕ Dodaj do wysyłki"):
        dodaj_do_koszyka(wybrany_prod, ilosc)
    
    if st.button("🗑️ Wyczyść listę"):
        wyczysc_koszyk()
        st.rerun()

    st.divider()
    st.header("🚚 Przewoźnik")
    kurier_name = st.selectbox("Wybierz kuriera:", list(KURIERZY.keys()))
    k = KURIERZY[kurier_name]

# --- LOGIKA UKŁADANIA (PROSTY STACKING) ---
# Program próbuje ułożyć pudełka jedno na drugim (największe na spodzie)
def oblicz_paczke(elementy):
    if not elementy: return None
    
    # Sortujemy od największej powierzchni podstawy
    posortowane = sorted(elementy, key=lambda x: x['L']*x['W'], reverse=True)
    
    current_h = 0
    max_l = 0
    max_w = 0
    total_weight = 0
    
    paczka_czesci = []
    
    for item in posortowane:
        paczka_czesci.append({
            'pos': (0, 0, current_h),
            'dims': (item['L'], item['W'], item['H']),
            'color': item['color']
        })
        max_l = max(max_l, item['L'])
        max_w = max(max_w, item['W'])
        current_h += item['H']
        total_weight += item['Waga']
        
    dims_final = sorted([max_l, max_w, current_h], reverse=True)
    girth = dims_final[0] + 2*dims_final[1] + 2*dims_final[2]
    
    return {
        'czesci': paczka_czesci,
        'final_dims': (max_l, max_w, current_h),
        'total_w': total_weight,
        'girth': girth
    }

# --- RYSOWANIE 3D ---
def rysuj_paczke_multi(wynik):
    fig = go.Figure()
    
    for czesc in wynik['czesci']:
        x0, y0, z0 = czesc['pos']
        dx, dy, dz = czesc['dims']
        
        # Rysujemy każdą bryłę z osobnym kolorem
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
            y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
            z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1],
            j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5],
            k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            color=czesc['color'], opacity=0.6, showscale=False
        ))
        
    fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- WYSWIETLANIE ---
if st.session_state.koszyk:
    wynik = oblicz_paczke(st.session_state.koszyk)
    
    # Sprawdzanie limitów
    if "Paczkomat" in kurier_name:
        lim_ok = (wynik['final_dims'][0] <= k['L'] and wynik['final_dims'][1] <= k['W'] and wynik['final_dims'][2] <= k['H'] and wynik['total_w'] <= k['max_W'])
    else:
        lim_ok = (max(wynik['final_dims']) <= k['max_L'] and wynik['girth'] <= k['max_G'] and wynik['total_w'] <= k['max_W'])
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("📋 Lista w paczce:")
        for idx, item in enumerate(st.session_state.koszyk):
            st.write(f"{idx+1}. {list(PRODUKTY_BAZA.keys())[list(PRODUKTY_BAZA.values()).index(item)]}")
            
        st.divider()
        if lim_ok:
            st.success("✅ Paczka mieści się w limitach!")
            st.write(f"Wymiary: {wynik['final_dims'][0]}x{wynik['final_dims'][1]}x{wynik['final_dims'][2]} cm")
            st.write(f"Waga: {wynik['total_w']:.1f} kg")
            st.write(f"Obwód: {int(wynik['girth'])} cm")
        else:
            st.error("❌ Przekroczono limity kuriera!")
            
    with c2:
        st.plotly_chart(rysuj_paczke_multi(wynik), use_container_width=True)
else:
    st.info("Dodaj produkty z lewego panelu, aby stworzyć instrukcję pakowania.")
