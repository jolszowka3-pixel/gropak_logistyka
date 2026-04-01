import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURACJA KURIERÓW ---
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
    "Fasonowe (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2, "color": "purple"},
    "Własny wymiar...": None 
}

st.set_page_config(page_title="Gropak - Multi-Packing Pro", layout="wide")
st.title("📦 Gropak: System Pakowania Wieloproduktowego")

# --- ZARZĄDZANIE KOSZYKIEM ---
if 'koszyk' not in st.session_state:
    st.session_state.koszyk = []

# Funkcja dodająca produkt (obsługuje też nazwę dla własnych wymiarów)
def dodaj_do_koszyka(item_data, name, qty):
    for _ in range(qty):
        temp_item = item_data.copy()
        temp_item['nazwa_wyswietlana'] = name
        st.session_state.koszyk.append(temp_item)

def wyczysc_koszyk():
    st.session_state.koszyk = []

# --- PANEL BOCZNY ---
with st.sidebar:
    st.header("🛒 Kompletowanie zamówienia")
    wybrany_prod = st.selectbox("Produkt:", list(PRODUKTY_BAZA.keys()))
    
    # Obsługa wymiarów własnych
    if wybrany_prod == "Własny wymiar...":
        custom_L = st.number_input("Długość (cm)", min_value=1, value=50)
        custom_W = st.number_input("Szerokość (cm)", min_value=1, value=30)
        custom_H = st.number_input("Wysokość (cm)", min_value=1, value=20)
        custom_Waga = st.number_input("Waga (kg)", min_value=0.1, value=2.0)
        
        current_item = {
            "L": custom_L, "W": custom_W, "H": custom_H, 
            "Waga": custom_Waga, "color": "grey"
        }
        item_label = f"Własny ({custom_L}x{custom_W}x{custom_H})"
    else:
        current_item = PRODUKTY_BAZA[wybrany_prod]
        item_label = wybrany_prod

    ilosc = st.number_input("Ilość sztuk tego typu:", 1, 50, 1)
    
    if st.button("➕ Dodaj do listy wysyłkowej"):
        dodaj_do_koszyka(current_item, item_label, ilosc)
        st.toast(f"Dodano {ilosc}x {item_label}")
    
    if st.button("🗑️ Wyczyść całą listę"):
        wyczysc_koszyk()
        st.rerun()

    st.divider()
    st.header("🚚 Przewoźnik")
    kurier_name = st.selectbox("Wybierz kuriera:", list(KURIERZY.keys()))
    k = KURIERZY[kurier_name]

# --- LOGIKA UKŁADANIA (PROSTY STACKING) ---
def oblicz_paczke(elementy):
    if not elementy: return None
    
    # Sortujemy: największa powierzchnia podstawy idzie na spód
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
            'color': item.get('color', 'grey'),
            'name': item.get('nazwa_wyswietlana', 'Produkt')
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
        x, y, z = czesc['pos']
        dx, dy, dz = czesc['dims']
        fig.add_trace(go.Mesh3d(
            x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
            y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
            z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1],
            j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5],
            k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            color=czesc['color'], opacity=0.7, name=czesc['name']
        ))
        # Krawędzie dla lepszej widoczności
        lines_x = [x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x]
        lines_y = [y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy]
        lines_z = [z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz]
        fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='black', width=2), showlegend=False))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='L', yaxis_title='W', zaxis_title='H'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- WYŚWIETLANIE ---
if st.session_state.koszyk:
    wynik = oblicz_paczke(st.session_state.koszyk)
    
    # Limity
    if "Paczkomat" in kurier_name:
        lim_ok = (wynik['final_dims'][0] <= k['L'] and wynik['final_dims'][1] <= k['W'] and wynik['final_dims'][2] <= k['H'] and wynik['total_w'] <= k['max_W'])
    else:
        dims_sort = sorted(wynik['final_dims'], reverse=True)
        lim_ok = (dims_sort[0] <= k['max_L'] and wynik['girth'] <= k['max_G'] and wynik['total_w'] <= k['max_W'])
    
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("📋 Zawartość przesyłki:")
        for idx, item in enumerate(wynik['czesci']):
            st.write(f"{idx+1}. {item['name']}")
            
        st.divider()
        if lim_ok:
            st.success("✅ PACZKA ZMIEŚCI SIĘ!")
            st.write(f"Wymiary: **{wynik['final_dims'][0]}x{wynik['final_dims'][1]}x{wynik['final_dims'][2]} cm**")
            st.write(f"Waga całkowita: **{wynik['total_w']:.1f} kg**")
            st.write(f"Obwód (Girth): **{int(wynik['girth'])} cm**")
        else:
            st.error("❌ PRZEKROCZONO LIMITY KURIERA!")
            if wynik['total_w'] > k['max_W']: st.write(f"- Za ciężka! ({wynik['total_w']} kg / {k['max_W']} kg)")
            if not "Paczkomat" in kurier_name and max(wynik['final_dims']) > k['max_L']: st.write(f"- Za długa! ({max(wynik['final_dims'])} cm / {k['max_L']} cm)")
            
    with c2:
        st.plotly_chart(rysuj_paczke_multi(wynik), use_container_width=True)
else:
    st.info("Dodaj produkty (standardowe lub własne) z lewego panelu, aby wygenerować instrukcję.")
