import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- KONFIGURACJA STYLU I MARKI ---
st.set_page_config(page_title="Gropak Logistics Suite", layout="wide", page_icon="🏢")

# Custom CSS dla lepszego wyglądu
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- BAZA DANYCH ---
KURIERZY = {
    "DPD": {"max_L": 175, "max_G": 300, "max_W": 31.5, "price": 18.50, "color": "#dc0032"},
    "DHL": {"max_L": 120, "max_G": 300, "max_W": 31.5, "price": 21.00, "color": "#ffcc00"},
    "InPost": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25, "price": 14.90, "color": "#ffcc00"},
    "FedEx": {"max_L": 175, "max_G": 330, "max_W": 35.0, "price": 24.00, "color": "#4d148c"}
}

PRODUKTY = {
    "Karton K1": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Własny...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

# --- NAGŁÓWEK ---
st.image("https://via.placeholder.com/200x50?text=GROPAK+LOGISTICS", width=200) # Tu możesz wstawić logo
st.title("🏢 System Optymalizacji Przesyłek")
st.markdown("---")

# --- INTERFEJS ---
tab1, tab2, tab3 = st.tabs(["🚀 Kalkulator Bundlingu", "📋 Cennik i Limity", "📊 Raporty"])

with st.sidebar:
    st.header("🛒 Dane Zamówienia")
    prod_select = st.selectbox("Wybierz produkt:", list(PRODUKTY.keys()))
    
    if prod_select == "Własny...":
        L = st.number_input("Długość (cm)", 1)
        W = st.number_input("Szerokość (cm)", 1)
        H = st.number_input("Wysokość (cm)", 1)
        Waga = st.number_input("Waga (kg)", 0.1)
    else:
        L, W, H, Waga = PRODUKTY[prod_select].values()
        st.info(f"Wymiary: {L}x{W}x{H} cm | {Waga} kg")

    sztuk = st.number_input("Ilość sztuk w zamówieniu:", min_value=1, value=12)
    st.divider()
    st.header("🚚 Preferencje")
    wybrany_kurier = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))

with tab1:
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    # --- LOGIKA OPTYMALIZACJI ---
    results = []
    # Sprawdzamy możliwe konfiguracje blokowe
    for n in range(1, sztuk + 1):
        for nx in range(1, n + 1):
            for ny in range(1, (n // nx) + 1):
                if n % (nx * ny) == 0:
                    nz = n // (nx * ny)
                    fL, fW, fH = L*nx, W*ny, H*nz
                    
                    # Sortowanie dla obwodu
                    ds = sorted([fL, fW, fH], reverse=True)
                    girth = ds[0] + 2*ds[1] + 2*ds[2]
                    total_w = Waga * n
                    
                    # Walidacja kuriera
                    lim = KURIERZY[wybrany_kurier]
                    if wybrany_kurier == "InPost":
                        ok = (fL <= 64 and fW <= 41 and fH <= 38 and total_w <= 25)
                    else:
                        ok = (ds[0] <= lim["max_L"] and girth <= lim["max_G"] and total_w <= lim["max_W"])
                    
                    if ok:
                        results.append({"n": n, "conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth, "waga": total_w})

    if results:
        best = sorted(results, key=lambda x: (x['n'], -x['girth']), reverse=True)[0]
        nx, ny, nz = best['conf']
        
        # Wskaźniki KPI
        with col_kpi1:
            st.metric("Paczka zawiera", f"{best['n']} szt.")
        with col_kpi2:
            st.metric("Wykorzystanie limitu", f"{int((best['girth']/KURIERZY[wybrany_kurier].get('max_G', 300))*100)}%")
        with col_kpi3:
            koszt_jedn = KURIERZY[wybrany_kurier]['price']
            oszczednosc = (sztuk * koszt_jedn) - ( (sztuk//best['n'] + (1 if sztuk%best['n']>0 else 0)) * koszt_jedn)
            st.metric("Szacowana oszczędność", f"{oszczednosc:.2f} PLN", delta="Zysk")

        # Wizualizacja i Instrukcja
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📦 Model 3D Pakowania")
            # --- FUNKCJA RYSOWANIA (Uproszczona dla profesjonalnego widoku) ---
            L_f, W_f, H_f = best['dims']
            fig = go.Figure()
            # Bryła paczki
            fig.add_trace(go.Mesh3d(
                x=[0, L_f, L_f, 0, 0, L_f, L_f, 0],
                y=[0, 0, W_f, W_f, 0, 0, W_f, W_f],
                z=[0, 0, 0, 0, H_f, H_f, H_f, H_f],
                i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1],
                j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5],
                k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
                opacity=0.4, color=KURIERZY[wybrany_kurier]['color']
            ))
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("📝 Instrukcja")
            st.markdown(f"""
            1. Weź karton o wymiarach **{L}x{W}x{H}**
            2. Ułóż warstwę podstawową: **{nx}x{ny}**
            3. Powtórz to **{nz}** razy w górę.
            
            **Finalna przesyłka:**
            - Waga: **{best['waga']:.1f} kg**
            - Gabaryty: **{best['dims'][0]}x{best['dims'][1]}x{best['dims'][2]} cm**
            """)
            if st.button("🖨️ Generuj PDF (Instrukcja)"):
                st.write("Generowanie... (funkcja w przygotowaniu)")

    else:
        st.error("⚠️ UWAGA: Nie znaleziono optymalnego połączenia. Wyślij jako pojedyncze paczki.")

with tab2:
    st.subheader("Porównanie limitów przewoźników")
    st.table(KURIERZY)

with tab3:
    st.info("Sekcja raportowania będzie dostępna po połączeniu z bazą danych SQL.")
