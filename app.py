import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KURIERZY (mm i kg) ---
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
    "TNT Express": {"max_L": 2400, "max_G": 4000, "max_W": 30.0},
    "Ambro Express": {"max_L": 3000, "max_G": 5000, "max_W": 50.0}
}

# --- TWOJA KOMPLETNA BAZA KARTONÓW ---
PUDEŁKA_GROPAK = {
    "Karton na wiórka (380x380x240)": {"L": 380, "W": 380, "H": 240, "Waga": 0.0},
    "Zbiorczy papier nacinany (390x390x620)": {"L": 390, "W": 390, "H": 620, "Waga": 0.0},
    "Zbiorczy papier nacinany (390x390x420)": {"L": 390, "W": 390, "H": 420, "Waga": 0.0},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275, "Waga": 0.0},
    "Dyspenser 400ka (410x255x180)": {"L": 410, "W": 255, "H": 180, "Waga": 0.0},
    "Zbiorczy dyspenser 200ka (365x265x285)": {"L": 365, "W": 265, "H": 285, "Waga": 0.0},
    "Zbiorczy dyspenser 400ka (465x245x190)": {"L": 465, "W": 245, "H": 190, "Waga": 0.0},
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
    "Karton 230x230 (H:510)": {"L": 230, "W": 230, "H": 510, "Waga": 0.0},
    "Karton 230x230 (H:610)": {"L": 230, "W": 230, "H": 610, "Waga": 0.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

KOLOR_KARTONU = "#C19A6B"

st.set_page_config(page_title="Gropak Master Pro v7", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Wybór towaru")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (mm)", 10); W = st.number_input("Szer (mm)", 10); H = st.number_input("Wys (mm)", 10); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Metoda")
    tryb = st.radio("Tryb pracy:", ["Paczka Kurierska", "Paleta EURO (1200x800)"])

    if tryb == "Paczka Kurierska":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość palety (mm):", 200, 2500, 1600)

# --- ZAAWANSOWANA WIZUALIZACJA 3D (Solidne bryły + Realistyczna Paleta) ---
def rysuj_layout_3d(bloki, is_pallet=False):
    fig = go.Figure()
    
    def dodaj_bryle(x, y, z, l, w, h, kolor, show_edges=True):
        fig.add_trace(go.Mesh3d(
            x=[x, x+l, x+l, x, x, x+l, x+l, x],
            y=[y, y, y+w, y+w, y, y, y+w, y+w],
            z=[z, z, z, z, z+h, z+h, z+h, z+h],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            opacity=1, color=kolor, flatshading=True, showlegend=False, hoverinfo='skip'
        ))
        if show_edges:
            lx = [x, x+l, x+l, x, x, None, x, x+l, x+l, x, x, None, x, x, None, x+l, x+l, None, x+l, x+l, None, x, x]
            ly = [y, y, y+w, y+w, y, None, y, y, y+w, y+w, y, None, y, y, None, y, y, None, y+w, y+w, None, y+w, y+w]
            lz = [z, z, z, z, z, None, z+h, z+h, z+h, z+h, z+h, None, z, z+h, None, z, z+h, None, z, z+h, None, z, z+h]
            fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2.5), showlegend=False, hoverinfo='skip'))

    if is_pallet:
        pallet_color = "#4E342E"
        for y_off in [0, 350, 700]: dodaj_bryle(0, y_off, -144, 1200, 100, 22, pallet_color, False) # Płozy
        for x_off in [0, 525, 1050]: 
            for y_off in [0, 350, 700]: dodaj_bryle(x_off, y_off, -122, 150, 100, 78, pallet_color, False) # Klocki
        for y_off in [0, 175, 350, 525, 700]: dodaj_bryle(0, y_off, -44, 1200, 100, 44, pallet_color, False) # Deski

    for b in bloki:
        x0, y0, z0 = b['pos']
        l, w, h = b['dims']
        nx, ny, nz = b['count']
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    dodaj_bryle(x0 + ix*l, y0 + iy*w, z0 + iz*h, l, w, h, KOLOR_KARTONU)
    
    fig.update_layout(
        scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.8, y=1.8, z=1.5))),
        margin=dict(l=10, r=10, b=10, t=10),
        paper_bgcolor="white",
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#e0e0e0", width=2))]
    )
    return fig

# --- LOGIKA OPTYMALIZACJI ---
def get_orientations(L, W, H):
    return list({(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)})

def optymalizuj_paczke(n, L, W, H, k_name):
    k = KURIERZY[k_name]
    wyniki = []
    for rl, rw, rh in get_orientations(L, W, H):
        for nx in range(1, n + 1):
            for ny in range(1, (n // nx) + 1):
                if n % (nx * ny) == 0:
                    nz = n // (nx * ny)
                    fL, fW, fH = rl*nx, rw*ny, rh*nz
                    ds = sorted([fL, fW, fH], reverse=True)
                    girth = ds[0] + 2*ds[1] + 2*ds[2]
                    if "Paczkomat" in k_name: ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"])
                    else: ok = (ds[0] <= k["max_L"] and girth <= k["max_G"])
                    if ok:
                        score = abs(fL-fW) + abs(fW-fH) + abs(fL-fH)
                        wyniki.append({"conf": (nx, ny, nz), "dims": (rl, rw, rh), "final": (fL, fW, fH), "score": score})
    return sorted(wyniki, key=lambda x: x['score'])[0] if wyniki else None

# --- NOWY SILNIK: MIESZANE RZĘDY (Agresywne wypełnianie) ---
def optymalizuj_palete_zaawansowana(L, W, H, h_max):
    PL, PW = 1200, 800
    best_n = 0
    best_layout = []
    orient = get_orientations(L, W, H)

    for ol_base, ow_base, oh_base in orient:
        nz = h_max // oh_base
        if nz == 0: continue
        
        # Testujemy mieszanie orientacji wzdłuż osi Y (800mm)
        # i1 rzędów boku A + i2 rzędów boku B
        for o1 in orient:
            if o1[2] != oh_base: continue
            for o2 in orient:
                if o2[2] != oh_base: continue
                
                # Próbujemy różnych kombinacji rzędów wzdłuż szerokości palety (800)
                max_r1 = PW // o1[1]
                for r1 in range(max_r1 + 1):
                    rem_y = PW - (r1 * o1[1])
                    r2 = rem_y // o2[1]
                    
                    # Ile sztuk wejdzie wzdłuż długości (1200)?
                    nx1 = PL // o1[0]
                    nx2 = PL // o2[0]
                    
                    total = (r1 * nx1 + r2 * nx2) * nz
                    if total > best_n:
                        best_n = total
                        best_layout = [
                            {'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(r1), int(nz))},
                            {'pos': (0, r1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(r2), int(nz))}
                        ]
                        
        # Powtarzamy test dla osi X (1200mm)
        for o1 in orient:
            if o1[2] != oh_base: continue
            for o2 in orient:
                if o2[2] != oh_base: continue
                max_c1 = PL // o1[0]
                for c1 in range(max_c1 + 1):
                    rem_x = PL - (c1 * o1[0])
                    c2 = rem_x // o2[0]
                    ny1 = PW // o1[1]
                    ny2 = PW // o2[1]
                    total = (c1 * ny1 + c2 * ny2) * nz
                    if total > best_n:
                        best_n = total
                        best_layout = [
                            {'pos': (0, 0, 0), 'dims': o1, 'count': (int(c1), int(ny1), int(nz))},
                            {'pos': (c1*o1[0], 0, 0), 'dims': o2, 'count': (int(c2), int(ny2), int(nz))}
                        ]

    return best_layout, best_n

# --- WIDOK ---
c1, c2 = st.columns([1, 1.5])
if tryb == "Paczka Kurierska":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        with c1:
            st.subheader("📋 Instrukcja")
            st.success(f"Spięto: **{sztuk} szt.**")
            st.write(f"- Ułożenie bazy: {rl}x{rw} mm")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout_3d([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
else:
    layout, total = optymalizuj_palete_zaawansowana(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Plan Palety")
            st.success(f"Razem: **{total} szt.**")
            st.write("Algorytm dobrał mieszane rzędy, aby zminimalizować luki.")
            st.divider()
            for i, b in enumerate(layout):
                szt = b['count'][0]*b['count'][1]*b['count'][2]
                if szt > 0:
                    st.write(f"**Sekcja {i+1} ({szt} szt.):** {b['dims'][0]}x{b['dims'][1]} mm")
        with c2: st.plotly_chart(rysuj_layout_3d(layout, is_pallet=True), use_container_width=True)
