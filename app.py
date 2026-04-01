import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KOMPLEKSOWA BAZA KURIERÓW (mm i kg) ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 1750, "max_G": 3000, "max_W": 31.5},
    "DHL (Standard)": {"max_L": 1200, "max_G": 3000, "max_W": 31.5},
    "InPost Paczkomat A": {"L": 640, "W": 380, "H": 80, "max_W": 25.0},
    "InPost Paczkomat B": {"L": 640, "W": 380, "H": 190, "max_W": 25.0},
    "InPost Paczkomat C": {"L": 640, "W": 380, "H": 410, "max_W": 25.0},
    "InPost Kurier": {"max_L": 1200, "max_G": 2200, "max_W": 30.0},
    "Orlen Paczka S": {"L": 600, "W": 380, "H": 80, "max_W": 20.0},
    "Orlen Paczka M": {"L": 600, "W": 380, "H": 190, "max_W": 20.0},
    "Orlen Paczka L": {"L": 600, "W": 380, "H": 410, "max_W": 20.0},
    "GLS (Polska)": {"max_L": 2000, "max_G": 3000, "max_W": 31.5},
    "UPS Standard": {"max_L": 2740, "max_G": 4000, "max_W": 32.0},
    "FedEx Polska": {"max_L": 1750, "max_G": 3300, "max_W": 35.0},
    "Pocztex": {"max_L": 1500, "max_G": 3000, "max_W": 30.0},
    "Geis": {"max_L": 1750, "max_G": 3000, "max_W": 31.5},
    "Meest": {"max_L": 1500, "max_G": 3000, "max_W": 30.0},
    "TNT Express": {"max_L": 2400, "max_G": 4000, "max_W": 30.0},
    "Ambro Express (Gabaryt)": {"max_L": 3000, "max_G": 5000, "max_W": 50.0}
}

# --- TWOJA PEŁNA BAZA KARTONÓW (Przeliczona na mm) ---
PUDEŁKA_GROPAK = {
    "Karton na wiórka (380x380x240)": {"L": 380, "W": 380, "H": 240, "Waga": 0.0},
    "Zbiorczy na papier nacinany (390x390x620)": {"L": 390, "W": 390, "H": 620, "Waga": 0.0},
    "Zbiorczy na papier nacinany (390x390x420)": {"L": 390, "W": 390, "H": 420, "Waga": 0.0},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275, "Waga": 0.0},
    "Dyspenser 400ka (410x255x180)": {"L": 410, "W": 255, "H": 180, "Waga": 0.0},
    "Zbiorczy na dyspenser 200ka (365x265x285)": {"L": 365, "W": 265, "H": 285, "Waga": 0.0},
    "Zbiorczy na dyspenser 400ka (465x245x190)": {"L": 465, "W": 245, "H": 190, "Waga": 0.0},
    
    "A11 (595x250x180)": {"L": 595, "W": 250, "H": 180, "Waga": 0.0},
    "B12 (595x295x230)": {"L": 595, "W": 295, "H": 230, "Waga": 0.0},
    "C13 (595x230x175)": {"L": 595, "W": 230, "H": 175, "Waga": 0.0},
    "D14 (595x280x205)": {"L": 595, "W": 280, "H": 205, "Waga": 0.0},
    "E15 (595x280x245)": {"L": 595, "W": 280, "H": 245, "Waga": 0.0},
    "F16 (595x360x250)": {"L": 595, "W": 360, "H": 250, "Waga": 0.0},
    "G17 (595x360x265)": {"L": 595, "W": 360, "H": 265, "Waga": 0.0},
    "H18 (595x375x295)": {"L": 595, "W": 375, "H": 295, "Waga": 0.0},
    "I19 (455x325x295)": {"L": 455, "W": 325, "H": 295, "Waga": 0.0},
    "K20 (485x385x295)": {"L": 485, "W": 385, "H": 295, "Waga": 0.0},
    "L21 (485x430x295)": {"L": 485, "W": 430, "H": 295, "Waga": 0.0},

    "Karton na folię (350x350x600)": {"L": 350, "W": 350, "H": 600, "Waga": 0.0},
    "Karton na folię (600x600x500)": {"L": 600, "W": 600, "H": 500, "Waga": 0.0},
    "Karton na folię (300x300x1220)": {"L": 300, "W": 300, "H": 1220, "Waga": 0.0},
    "Karton na folię (470x470x200)": {"L": 470, "W": 470, "H": 200, "Waga": 0.0},
    "Karton na folię (470x470x300)": {"L": 470, "W": 470, "H": 300, "Waga": 0.0},
    "Karton na folię (470x470x400)": {"L": 470, "W": 470, "H": 400, "Waga": 0.0},
    "Karton na folię (470x470x500)": {"L": 470, "W": 470, "H": 500, "Waga": 0.0},

    "Wypełniacz 295x295 (H:210)": {"L": 295, "W": 295, "H": 210, "Waga": 0.0},
    "Wypełniacz 295x295 (H:310)": {"L": 295, "W": 295, "H": 310, "Waga": 0.0},
    "Wypełniacz 295x295 (H:340)": {"L": 295, "W": 295, "H": 340, "Waga": 0.0},
    "Wypełniacz 295x295 (H:360)": {"L": 295, "W": 295, "H": 360, "Waga": 0.0},
    "Wypełniacz 295x295 (H:410)": {"L": 295, "W": 295, "H": 410, "Waga": 0.0},
    "Wypełniacz 230x230 (H:210)": {"L": 230, "W": 230, "H": 210, "Waga": 0.0},
    "Wypełniacz 230x230 (H:310)": {"L": 230, "W": 230, "H": 310, "Waga": 0.0},
    "Wypełniacz 230x230 (H:410)": {"L": 230, "W": 230, "H": 410, "Waga": 0.0},

    "Karton 90x90 (H:210)": {"L": 90, "W": 90, "H": 210, "Waga": 0.0},
    "Karton 90x90 (H:310)": {"L": 90, "W": 90, "H": 310, "Waga": 0.0},
    "Karton 90x90 (H:410)": {"L": 90, "W": 90, "H": 410, "Waga": 0.0},
    "Karton 90x90 (H:510)": {"L": 90, "W": 90, "H": 510, "Waga": 0.0},
    "Karton 90x90 (H:610)": {"L": 90, "W": 90, "H": 610, "Waga": 0.0},
    "Karton 110x110 (H:210)": {"L": 110, "W": 110, "H": 210, "Waga": 0.0},
    "Karton 110x110 (H:310)": {"L": 110, "W": 110, "H": 310, "Waga": 0.0},
    "Karton 110x110 (H:410)": {"L": 110, "W": 110, "H": 410, "Waga": 0.0},
    "Karton 110x110 (H:510)": {"L": 110, "W": 110, "H": 510, "Waga": 0.0},
    "Karton 110x110 (H:610)": {"L": 110, "W": 110, "H": 610, "Waga": 0.0},
    "Karton 160x160 (H:210)": {"L": 160, "W": 160, "H": 210, "Waga": 0.0},
    "Karton 160x160 (H:310)": {"L": 160, "W": 160, "H": 310, "Waga": 0.0},
    "Karton 160x160 (H:410)": {"L": 160, "W": 160, "H": 410, "Waga": 0.0},
    "Karton 160x160 (H:510)": {"L": 160, "W": 160, "H": 510, "Waga": 0.0},
    "Karton 160x160 (H:610)": {"L": 160, "W": 160, "H": 610, "Waga": 0.0},
    "Karton 230x230 (H:210)": {"L": 230, "W": 230, "H": 210, "Waga": 0.0},
    "Karton 230x230 (H:310)": {"L": 230, "W": 230, "H": 310, "Waga": 0.0},
    "Karton 230x230 (H:410)": {"L": 230, "W": 230, "H": 410, "Waga": 0.0},
    "Karton 230x230 (H:510)": {"L": 230, "W": 230, "H": 510, "Waga": 0.0},
    "Karton 230x230 (H:610)": {"L": 230, "W": 230, "H": 610, "Waga": 0.0},

    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

KOLOR_KARTONU = "#D2A679"

st.set_page_config(page_title="Gropak - Super Optymalizator (mm)", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek (mm)")

with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Wybierz karton z bazy:", list(PUDEŁKA_GROPAK.keys()))
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
        h_max = st.number_input("Maksymalna wysokość palety (mm):", 200, 2500, 1600)

# --- WIZUALIZACJA 3D ---
def rysuj_layout_3d(bloki, is_pallet=False):
    fig = go.Figure()
    if is_pallet:
        fig.add_trace(go.Mesh3d(x=[0,1200,1200,0,0,1200,1200,0], y=[0,0,800,800,0,0,800,800], z=[-144,-144,-144,-144,0,0,0,0], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=1, color="#8B4513"))

    for b in bloki:
        x0, y0, z0 = b['pos']
        l, w, h = b['dims']
        nx, ny, nz = b['count']
        fL, fW, fH = l*nx, w*ny, h*nz
        fig.add_trace(go.Mesh3d(x=[x0, x0+fL, x0+fL, x0, x0, x0+fL, x0+fL, x0], y=[y0, y0, y0+fW, y0+fW, y0, y0, y0+fW, y0+fW], z=[z0, z0, z0, z0, z0+fH, z0+fH, z0+fH, z0+fH], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=1, color=KOLOR_KARTONU))
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

# --- LOGIKA ---
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
                    ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"])
                else:
                    ok = (ds[0] <= k["max_L"] and girth <= k["max_G"])
                if ok:
                    wyniki.append({"conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth, "stab": abs(nx-ny)+abs(ny-nz)})
    return sorted(wyniki, key=lambda x: x['stab'])[0] if wyniki else None

def optymalizuj_palete(L, W, H, h_max):
    best_total = 0
    best_layout = []
    for ol, ow, oh in [(L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)]:
        nz = h_max // oh
        if nz == 0: continue
        for split in range(0, 1201, 50):
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
            st.success(f"Układ: **{nx} x {ny} x {nz}**")
            st.write(f"- Wymiary paczki: {res['dims'][0]}x{res['dims'][1]}x{res['dims'][2]} mm")
        with c2:
            st.plotly_chart(rysuj_layout_3d([{'pos': (0,0,0), 'dims': (L, W, H), 'count': (nx, ny, nz)}]), use_container_width=True)
    else:
        st.error("❌ Paczki nie da się spiąć w tym limicie kuriera.")
else:
    layout, total = optymalizuj_palete(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Instrukcja Palety")
            st.success(f"Razem: **{total} sztuk**")
            st.write(f"- Wysokość ładunku: {layout[0]['dims'][2] * layout[0]['count'][2]} mm")
            for i, b in enumerate(layout):
                if b['count'][0]*b['count'][1] > 0:
                    st.write(f"**Sekcja {i+1}:** {b['count'][0]*b['count'][1]*b['count'][2]} szt. ({b['dims'][0]}x{b['dims'][1]} mm)")
        with c2:
            st.plotly_chart(rysuj_layout_3d(layout, is_pallet=True), use_container_width=True)
    else:
        st.error("❌ Karton nie mieści się na palecie.")
