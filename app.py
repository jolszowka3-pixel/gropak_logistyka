import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KOMPLEKSOWA BAZA KURIERÓW (Wszystko w mm i kg) ---
# max_L: najdłuższy bok, max_G: obwód (L + 2W + 2H), max_W: waga
KURIERZY = {
    "DPD (Standard)": {"max_L": 1750, "max_G": 3000, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 1200, "max_G": 3000, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Paczkomat A": {"L": 640, "W": 380, "H": 80, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat B": {"L": 640, "W": 380, "H": 190, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 640, "W": 380, "H": 410, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 1200, "max_G": 2200, "max_W": 30.0, "color": "#ffcc00"},
    "Orlen Paczka S": {"L": 600, "W": 380, "H": 80, "max_W": 20.0, "color": "#e30613"},
    "Orlen Paczka M": {"L": 600, "W": 380, "H": 190, "max_W": 20.0, "color": "#e30613"},
    "Orlen Paczka L": {"L": 600, "W": 380, "H": 410, "max_W": 20.0, "color": "#e30613"},
    "GLS (Polska)": {"max_L": 2000, "max_G": 3000, "max_W": 31.5, "color": "#003399"},
    "UPS Standard": {"max_L": 2740, "max_G": 4000, "max_W": 32.0, "color": "#351c15"},
    "FedEx Polska": {"max_L": 1750, "max_G": 3300, "max_W": 35.0, "color": "#4d148c"},
    "Pocztex (Standard)": {"max_L": 1500, "max_G": 3000, "max_W": 30.0, "color": "#ee1d23"},
    "Geis": {"max_L": 1750, "max_G": 3000, "max_W": 31.5, "color": "#004a99"},
    "Meest": {"max_L": 1500, "max_G": 3000, "max_W": 30.0, "color": "#25b14b"},
    "TNT Express": {"max_L": 2400, "max_G": 4000, "max_W": 30.0, "color": "#ff6600"},
    "Ambro Express (Gabaryt)": {"max_L": 3000, "max_G": 5000, "max_W": 50.0, "color": "#000000"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (400x300x200)": {"L": 400, "W": 300, "H": 200, "Waga": 2.5},
    "Karton K2 (600x400x300)": {"L": 600, "W": 400, "H": 300, "Waga": 6.0},
    "Karton K3 (800x600x150)": {"L": 800, "W": 600, "H": 150, "Waga": 10.0},
    "Karton Fasonowy (350x250x100)": {"L": 350, "W": 250, "H": 100, "Waga": 1.2},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Super Optymalizator (mm)", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek (mm)")

with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Typ pudełka:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (mm)", 10); W = st.number_input("Szer (mm)", 10); H = st.number_input("Wys (mm)", 10); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Tryb Pracy")
    tryb = st.radio("Co planujemy?", ["Łączenie Paczek (Bundling)", "Układanie na Palecie (1200x800)"])

    if tryb == "Łączenie Paczek (Bundling)":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk do spięcia:", 1, 100, 6)
    else:
        h_max = st.number_input("Maksymalna wysokość (mm):", 200, 2500, 1600)

# --- WIZUALIZACJA 3D ---
def rysuj_layout_3d(bloki, color, is_pallet=False):
    fig = go.Figure()
    if is_pallet:
        # Rysuj paletę EURO w mm
        fig.add_trace(go.Mesh3d(x=[0,1200,1200,0,0,1200,1200,0], y=[0,0,800,800,0,0,800,800], z=[-144,-144,-144,-144,0,0,0,0], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=1, color="#8B4513"))

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
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Dł (mm)', yaxis_title='Szer (mm)', zaxis_title='Wys (mm)'), margin=dict(l=0,r=0,b=0,t=0))
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
        for split in range(0, 1201, 50): # Split co 50mm dla wydajności
            nx_a = split // ol
            ny_a = 800 // ow
            nx_b = (1200 - (nx_a * ol)) // ow
            ny_b = 800 // ol
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
            st.write(f"- Finalne wymiary: {res['dims'][0]}x{res['dims'][1]}x{res['dims'][2]} mm")
            st.write(f"- Waga: {Waga*sztuk:.1f} kg | Obwód: {int(res['girth'])} mm")
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
            st.write(f"- Wysokość ładunku: {layout[0]['dims'][2] * layout[0]['count'][2]} mm")
            st.write(f"- Waga towaru: {total * Waga:.1f} kg")
            st.divider()
            for i, b in enumerate(layout):
                if b['count'][0]*b['count'][1] > 0:
                    st.write(f"**Sekcja {i+1}:** {b['count'][0]*b['count'][1]*b['count'][2]} szt. (Karton na boku {b['dims'][0]}x{b['dims'][1]} mm)")
        with c2:
            st.plotly_chart(rysuj_layout_3d(layout, "#2ca02c", is_pallet=True), use_container_width=True)
    else:
        st.error("❌ Karton nie mieści się na palecie.")
