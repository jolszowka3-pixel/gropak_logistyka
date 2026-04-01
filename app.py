import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- ROZBUDOWANA BAZA KURIERÓW ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "InPost Paczkomat A": {"L": 64, "W": 38, "H": 8, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat B": {"L": 64, "W": 38, "H": 19, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "Poczta Polska (Pocztex)": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#ee1d23"},
    "GLS": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "FedEx": {"max_L": 175, "max_G": 330, "max_W": 35.0, "color": "#4d148c"},
    "UPS": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Fasonowe (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Master Packing", layout="wide")
st.title("📦 Gropak: System Instrukcji Pakowania")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Długość (cm)", 1); W = st.number_input("Szerokość (cm)", 1)
        H = st.number_input("Wysokość (cm)", 1); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Wysyłka")
    kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
    sztuk = st.number_input("Ilość sztuk do spięcia:", 1, 100, 4)

# --- FUNKCJA RYSOWANIA (Wyraźny podział) ---
def rysuj_instrukcje(orig_dims, nx, ny, nz, color):
    L_f, W_f, H_f = orig_dims[0]*nx, orig_dims[1]*ny, orig_dims[2]*nz
    fig = go.Figure()

    # Ścianki zewnętrzne (półprzezroczyste)
    fig.add_trace(go.Mesh3d(
        x=[0, L_f, L_f, 0, 0, L_f, L_f, 0], y=[0, 0, W_f, W_f, 0, 0, W_f, W_f], z=[0, 0, 0, 0, H_f, H_f, H_f, H_f],
        i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
        opacity=0.2, color=color
    ))

    # Linie podziału (siatka wewnętrzna)
    lines_x, lines_y, lines_z = [], [], []
    for x in range(nx + 1):
        for y in range(ny + 1):
            lines_x.extend([x*orig_dims[0], x*orig_dims[0]]); lines_y.extend([y*orig_dims[1], y*orig_dims[1]]); lines_z.extend([0, H_f]); lines_x.append(None); lines_y.append(None); lines_z.append(None)
    for x in range(nx + 1):
        for z in range(nz + 1):
            lines_x.extend([x*orig_dims[0], x*orig_dims[0]]); lines_y.extend([0, W_f]); lines_z.extend([z*orig_dims[2], z*orig_dims[2]]); lines_x.append(None); lines_y.append(None); lines_z.append(None)
    for y in range(ny + 1):
        for z in range(nz + 1):
            lines_x.extend([0, L_f]); lines_y.extend([y*orig_dims[1], y*orig_dims[1]]); lines_z.extend([z*orig_dims[2], z*orig_dims[2]]); lines_x.append(None); lines_y.append(None); lines_z.append(None)

    fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='black', width=4)))
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Długość', yaxis_title='Szerokość', zaxis_title='Wysokość'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- LOGIKA ---
def optymalizuj(n, L, W, H, Waga, k_name):
    wyniki = []
    k = KURIERZY[k_name]
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                fL, fW, fH = L*nx, W*ny, H*nz
                ds = sorted([fL, fW, fH], reverse=True)
                girth = ds[0] + 2*ds[1] + 2*ds[2]
                w_tot = Waga * n
                
                if "Paczkomat" in k_name:
                    ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"] and w_tot <= k["max_W"])
                else:
                    ok = (ds[0] <= k["max_L"] and girth <= k["max_G"] and w_tot <= k["max_W"])
                
                if ok: wyniki.append({"conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth})
    return sorted(wyniki, key=lambda x: x['girth'])[0] if wyniki else None

res = optymalizuj(sztuk, L, W, H, Waga, kurier_name)

if res:
    nx, ny, nz = res['conf']
    fL, fW, fH = res['dims']
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("📋 Instrukcja Pakowania")
        st.success(f"Można spiąć te **{sztuk} sztuk** w jedną paczkę!")
        st.markdown(f"""
        - **Krok 1:** Ułóż bazę: **{nx} rzędy** (długość) i **{ny} kolumny** (szerokość).
        - **Krok 2:** Dodaj warstwy w górę: łącznie **{nz} poziomów**.
        
        **Dane paczki:**
        - Gabaryty: **{fL} x {fW} x {fH} cm**
        - Waga: **{Waga * sztuk:.1f} kg**
        - Kurier: **{kurier_name}**
        """)
        st.info("💡 Wskazówka: Jeśli paczka jest ciężka, użyj podwójnego owinięcia folią na łączeniach.")
    with c2:
        st.plotly_chart(rysuj_instrukcje((L, W, H), nx, ny, nz, KURIERZY[kurier_name]['color']), use_container_width=True)
else:
    st.error(f"❌ Przekroczono limity {kurier_name} dla {sztuk} sztuk!")
    st.warning("Zmień przewoźnika na takiego z większym limitem (np. UPS/GLS) lub zmniejsz ilość sztuk.")
