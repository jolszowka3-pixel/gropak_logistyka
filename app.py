import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KOMPLEKSOWA BAZA KURIERÓW ---
# max_L: najdłuższy bok, max_G: obwód (L + 2W + 2H), max_W: waga
KURIERZY = {
    "DPD (Standard)": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Paczkomat A": {"L": 64, "W": 38, "H": 8, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat B": {"L": 64, "W": 38, "H": 19, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "Orlen Paczka S": {"L": 60, "W": 38, "H": 8, "max_W": 20.0, "color": "#e30613"},
    "Orlen Paczka M": {"L": 60, "W": 38, "H": 19, "max_W": 20.0, "color": "#e30613"},
    "Orlen Paczka L": {"L": 60, "W": 38, "H": 41, "max_W": 20.0, "color": "#e30613"},
    "GLS (Polska)": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "UPS Standard": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"},
    "FedEx Polska": {"max_L": 175, "max_G": 330, "max_W": 35.0, "color": "#4d148c"},
    "Pocztex (Standard)": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#ee1d23"},
    "Geis": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#004a99"},
    "Meest": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#25b14b"},
    "TNT Express": {"max_L": 240, "max_G": 400, "max_W": 30.0, "color": "#ff6600"},
    "Ambro Express (Gabaryt)": {"max_L": 300, "max_G": 500, "max_W": 50.0, "color": "#000000"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Karton Fasonowy (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Super Optymalizator", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek")

with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Typ pudełka:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (cm)", 1); W = st.number_input("Szer (cm)", 1); H = st.number_input("Wys (cm)", 1); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Tryb Pracy")
    tryb = st.radio("Co planujemy?", ["Łączenie Paczek (Bundling)", "Układanie na Palecie (120x80)"])

    if tryb == "Łączenie Paczek (Bundling)":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk do spięcia:", 1, 100, 6)
    else:
        h_max = st.number_input("Maksymalna wysokość (cm):", 20, 250, 160)

# --- WIZUALIZACJA 3D ---
def rysuj_layout_3d(bloki, color, is_pallet=False):
    fig = go.Figure()
    if is_pallet:
        fig.add_trace(go.Mesh3d(x=[0,120,120,0,0,120,120,0], y=[0,0,80,80,0,0,80,80], z=[-14,-14,-14,-14,0,0,0,0], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=1, color="#8B4513"))

    for b in bloki:
        x0, y0, z0 = b['pos']
        l, w, h = b['dims']
        nx, ny, nz = b['count']
        fL, fW, fH = l*nx, w*ny, h*nz
        fig.add_trace(go.Mesh3d(x=[x0, x0+fL, x0+fL, x0, x0, x0+fL, x0+fL, x0], y=[y0, y0, y0+fW, y0+fW, y0, y0, y0+fW, y0+fW], z=[z0, z0, z0, z0, z0+fH, z0+fH, z0+fH, z0+fH], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=0.3, color=color))
        lx, ly, lz = [], [], []
        for i in range(nx + 1):
            for j in range(ny + 1):
                lx.extend([x0+i*l, x0+i*l, None]); ly.extend([y0+j*w, y0+j*w, None]); lz.extend([z0, z0+fH, None])
        for i in range(nx + 1):
            for k in range(nz + 1):
                lx.extend([x0+i*l, x0+i*l, None]); ly.extend([y0, y0+fW, None]); lz.extend([z0+k*h, z0+k*h, None])
        for j in range(ny + 1):
            for k in range(nz + 1):
                lx.extend([x0, x0+fL, None]); ly.extend([y0+j*w, y0+j*w, None]); lz.extend([z0+k*h, z0+k*h, None])
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#000', width=3), showlegend=False))
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Dł', yaxis_title='Szer', zaxis_title='Wys'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- SILNIK PACZKI (BUNDLING) ---
def optymalizuj_paczke(n, L, W, H, w_jedn, k_name):
    k = KURIERZY[k_name]
    wyniki = []
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                fL, fW, fH = L*nx, W*ny, H*nz
                ds = sorted([fL, fW, fH], reverse=True)
                girth = ds[0] + 2*ds[1] + 2*ds[2]
                
                # Specyficzna logika dla automatów paczkowych (sztywne wymiary)
                if "Paczkomat" in k_name or "Orlen Paczka" in k_name:
                    ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"] and w_jedn*n <= k["max_W"])
                else:
                    ok = (ds[0] <= k["max_L"] and girth <= k["max_G"] and w_jedn*n <= k["max_W"])
                
                if ok:
                    wyniki.append({"conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth, "stab": abs(nx-ny)+abs(ny-nz)})
    return sorted(wyniki, key=lambda x: x['stab'])[0] if wyniki else None

# --- SILNIK PALETY (MIX ORIENTACJI) ---
def optymalizuj_palete(L, W, H, h_max):
    best_total = 0
    best_layout = []
    for ol, ow, oh in [(L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)]:
        nz = h_max // oh
        if nz == 0: continue
        for split in range(0, 121, 5):
            nx_a = split // ol
            ny_a = 80 // ow
            nx_b = (120 - (nx_a * ol)) // ow
            ny_b = 80 // ol
            sztuk = (nx_a * ny_a + nx_b * ny_b) * nz
            if sztuk > best_total:
                best_total = sztuk
                best_layout = [
                    {'pos': (0,0,0), 'dims': (ol, ow, oh), 'count': (int(nx_a), int(ny_a), int(nz))},
                    {'pos': (nx_a*ol, 0, 0), 'dims': (ow, ol, oh), 'count': (int(nx_b), int(ny_b), int(nz))}
                ]
    return best_layout, best_total

# --- WIDOK ---
c1, c2 = st.columns([1, 1.5])
if tryb == "Łączenie Paczek (Bundling)":
    res = optymalizuj_paczke(sztuk, L, W, H, Waga, kurier_name)
    if res:
        nx, ny, nz = res['conf']
        with c1:
            st.subheader("📋 Instrukcja Spiania")
            st.success(f"Układ optymalny: **{nx} x {ny} x {nz}**")
            st.write(f"- Finalne wymiary: {res['dims'][0]}x{res['dims'][1]}x{res['dims'][2]} cm")
            st.write(f"- Waga: {Waga*sztuk:.1f} kg | Obwód: {int(res['girth'])} cm")
        with c2:
            st.plotly_chart(rysuj_layout_3d([{'pos': (0,0,0), 'dims': (L, W, H), 'count': (nx, ny, nz)}], KURIERZY[kurier_name]['color']), use_container_width=True)
    else:
        st.error("❌ Paczki nie da się spiąć w tym limicie kuriera.")

else: # PALETA
    layout, total = optymalizuj_palete(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Instrukcja Palety")
            st.success(f"Razem na palecie: **{total} sztuk**")
            st.write(f"- Wysokość ładunku: {layout[0]['dims'][2] * layout[0]['count'][2]} cm")
            st.write(f"- Waga towaru: {total * Waga:.1f} kg")
            st.divider()
            for i, b in enumerate(layout):
                if b['count'][0]*b['count'][1] > 0:
                    st.write(f"**Sekcja {i+1}:** {b['count'][0]*b['count'][1]*b['count'][2]} szt. (Karton na boku {b['dims'][0]}x{b['dims'][1]})")
        with c2:
            st.plotly_chart(rysuj_layout_3d(layout, "#2ca02c", is_pallet=True), use_container_width=True)
    else:
        st.error("❌ Karton nie mieści się na palecie.")
