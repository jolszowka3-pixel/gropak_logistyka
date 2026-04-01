import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- BAZA KURIERÓW ---
KURIERZY = {
    "DPD": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "InPost Paczkomat A": {"L": 64, "W": 38, "H": 8, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat B": {"L": 64, "W": 38, "H": 19, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "GLS": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "UPS": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Pakowanie Blokowe", layout="wide")
st.title("📦 Gropak: Generator Instrukcji (Układ Blokowy)")

with st.sidebar:
    st.header("1. Co pakujemy?")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (cm)", 1); W = st.number_input("Szer (cm)", 1)
        H = st.number_input("Wys (cm)", 1); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Opcje wysyłki")
    kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
    sztuk = st.number_input("Ilość zamówionych sztuk:", 1, 100, 6)

# --- FUNKCJA WIZUALIZACJI SIATKI ---
def rysuj_blok_3d(orig_dims, nx, ny, nz, color):
    l, w, h = orig_dims
    fL, fW, fH = l*nx, w*ny, h*nz
    fig = go.Figure()

    # Obrys bryły
    fig.add_trace(go.Mesh3d(
        x=[0, fL, fL, 0, 0, fL, fL, 0], y=[0, 0, fW, fW, 0, 0, fW, fW], z=[0, 0, 0, 0, fH, fH, fH, fH],
        i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
        opacity=0.2, color=color
    ))

    # Rysowanie linii każdego pojedynczego pudełka (siatka)
    lines_x, lines_y, lines_z = [], [], []
    for i in range(nx + 1):
        for j in range(ny + 1):
            lines_x.extend([i*l, i*l, None]); lines_y.extend([j*w, j*w, None]); lines_z.extend([0, fH, None])
    for i in range(nx + 1):
        for k in range(nz + 1):
            lines_x.extend([i*l, i*l, None]); lines_y.extend([0, fW, None]); lines_z.extend([k*h, k*h, None])
    for j in range(ny + 1):
        for k in range(nz + 1):
            lines_x.extend([0, fL, None]); lines_y.extend([j*w, j*w, None]); lines_z.extend([k*h, k*h, None])

    fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='black', width=3)))
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Długość', yaxis_title='Szerokość', zaxis_title='Wysokość'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- LOGIKA SZUKANIA BLOKU ---
def szukaj_najlepszego_bloku(n, L, W, H, w_jedn, k_name):
    mozliwe_uklady = []
    k = KURIERZY[k_name]
    
    # Sprawdzamy wszystkie dzielniki liczby n dla 3 osi (nx * ny * nz = n)
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                fL, fW, fH = L*nx, W*ny, H*nz
                dims = sorted([fL, fW, fH], reverse=True)
                girth = dims[0] + 2*dims[1] + 2*dims[2]
                w_tot = w_jedn * n
                
                if "Paczkomat" in k_name:
                    ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"] and w_tot <= k["max_W"])
                else:
                    ok = (dims[0] <= k["max_L"] and girth <= k["max_G"] and w_tot <= k["max_W"])
                
                if ok:
                    # Szukamy układu najbardziej zbliżonego do sześcianu (najbardziej stabilny)
                    odchylenie = abs(nx-ny) + abs(ny-nz) + abs(nx-nz)
                    mozliwe_uklady.append({"conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth, "stab": odchylenie})
    
    # Sortujemy: najpierw te, które są najbardziej "zbite" (najmniejsze odchylenie wymiarów)
    return sorted(mozliwe_uklady, key=lambda x: x['stab'])[0] if mozliwe_uklady else None

res = szukaj_najlepszego_bloku(sztuk, L, W, H, Waga, kurier_name)

if res:
    nx, ny, nz = res['conf']
    fL, fW, fH = res['dims']
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("🛠️ Jak spakować:")
        st.info(f"Najlepszy układ dla {sztuk} sztuk to blok **{nx} x {ny} x {nz}**")
        st.markdown(f"""
        1. **Podstawa:** Ułóż obok siebie **{nx}** szt. (dłuższy bok) i **{ny}** szt. (krótszy bok).
        2. **Warstwy:** Zrób w ten sposób **{nz}** warstwy w górę.
        
        **Parametry paczki:**
        - Gabaryty: **{fL} x {fW} x {fH} cm**
        - Waga: **{Waga * sztuk:.1f} kg**
        """)
    with c2:
        st.plotly_chart(rysuj_blok_3d((L, W, H), nx, ny, nz, KURIERZY[kurier_name]['color']), use_container_width=True)
else:
    st.error("❌ Przekroczono limity kuriera. Nie da się stworzyć bezpiecznego bloku dla tej ilości sztuk.")
