import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. KOMPLEKSOWA BAZA KURIERÓW ---
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

# --- 2. KOMPLEKSOWA BAZA TWOICH KARTONÓW ---
PUDEŁKA_GROPAK = {
    "A11 (595x250x180)": {"L": 595, "W": 250, "H": 180},
    "B12 (595x295x230)": {"L": 595, "W": 295, "H": 230},
    "C13 (595x230x175)": {"L": 595, "W": 230, "H": 175},
    "D14 (595x280x205)": {"L": 595, "W": 280, "H": 205},
    "E15 (595x280x245)": {"L": 595, "W": 280, "H": 245},
    "F16 (595x360x250)": {"L": 595, "W": 360, "H": 250},
    "G17 (595x360x265)": {"L": 595, "W": 360, "H": 265},
    "H18 (595x375x295)": {"L": 595, "W": 375, "H": 295},
    "I19 (455x325x295)": {"L": 455, "W": 325, "H": 295},
    "K20 (485x385x295)": {"L": 485, "W": 385, "H": 295},
    "L21 (485x430x295)": {"L": 485, "W": 430, "H": 295},
    "Karton na wiórka (380x380x240)": {"L": 380, "W": 380, "H": 240},
    "Zbiorczy papier nacinany (390x390x620)": {"L": 390, "W": 390, "H": 620},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275},
    "Karton na folię (470x470x500)": {"L": 470, "W": 470, "H": 500},
    "Wypełniacz 295x295 (H:410)": {"L": 295, "W": 295, "H": 410},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0}
}

KOLOR_KARTONU = "#C19A6B"

st.set_page_config(page_title="Gropak Master Pro vFinal", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek")

with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (mm)", 10); W = st.number_input("Szer (mm)", 10); H = st.number_input("Wys (mm)", 10)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H = p["L"], p["W"], p["H"]
    
    st.divider()
    st.header("2. Metoda")
    tryb = st.radio("Tryb pracy:", ["📦 Paczka Kurierska", "🚛 Paleta EURO (1200x800)"])

    if tryb == "📦 Paczka Kurierska":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość palety (mm):", 200, 2500, 1600)

# --- 3. WIZUALIZACJA 3D (ZABUDOWANA, BEZ TRÓJKĄTÓW) ---
def rysuj_layout_3d(bloki, is_pallet=False):
    fig = go.Figure()
    
    def dodaj_sciane(x, y, z, kolor, border):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=0 if len(set(x)) == 1 else (1 if len(set(y)) == 1 else 2),
            surfacecolor=kolor,
            line=dict(color='black', width=2.5 if border else 0),
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        # 6 płaszczyzn prostokątnych - całkowity brak Mesh3d
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, border) # Góra
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, border) # Dół
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, border) # Front
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, border) # Tył
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border) # Lewo
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border) # Prawo

    if is_pallet:
        pc = "#4E342E" # Drewno palety
        # Konstrukcja palety
        for y in [0, 350, 700]: dodaj_bryle(0, y, -144, 1200, 100, 22, pc, False)
        for x in [0, 525, 1050]:
            for y in [0, 350, 700]: dodaj_bryle(x, y, -122, 150, 100, 78, pc, False)
        for y in [0, 175, 350, 525, 700]: dodaj_bryle(0, y, -44, 1200, 100, 44, pc, False)

    for b in bloki:
        x0, y0, z0, (dl, sz, wy) = b['pos'][0], b['pos'][1], b['pos'][2], b['dims']
        nx, ny, nz = b['count']
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    dodaj_bryle(x0 + ix*dl, y0 + iy*sz, z0 + iz*wy, dl, sz, wy, KOLOR_KARTONU)
    
    fig.update_layout(
        scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.8, y=1.8, z=1.5))),
        margin=dict(l=10, r=10, b=10, t=10), paper_bgcolor="white",
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#e0e0e0", width=2))]
    )
    return fig

# --- 4. LOGIKA OPTYMALIZACJI ---
def get_orientations(L, W, H):
    return list({(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)})

def optymalizuj_paczke(n, L, W, H, k_name):
    k = KURIERZY[k_name]
    wyniki = []
    for rl, rw, rh in get_orientations(L, W, H):
        if rl == 0 or rw == 0 or rh == 0: continue
        for nx in range(1, n + 1):
            for ny in range(1, (n // nx) + 1):
                if n % (nx * ny) == 0:
                    nz = n // (nx * ny)
                    fL, fW, fH = rl*nx, rw*ny, rh*nz
                    ds = sorted([fL, fW, fH], reverse=True)
                    girth = ds[0] + 2*ds[1] + 2*ds[2]
                    if "Paczkomat" in k_name or "Orlen" in k_name: ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"])
                    else: ok = (ds[0] <= k["max_L"] and girth <= k["max_G"])
                    if ok:
                        score = abs(fL-fW) + abs(fW-fH) + abs(fL-fH)
                        wyniki.append({"conf": (nx, ny, nz), "dims": (rl, rw, rh), "final": (fL, fW, fH), "score": score})
    return sorted(wyniki, key=lambda x: x['score'])[0] if wyniki else None

def optymalizuj_palete_stabilna(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = get_orientations(L, W, H)
    best_total = 0
    best_layout = []

    # Szukamy kombinacji rzędów, która daje najwięcej sztuk i jest stabilna
    for o1 in orient:
        for o2 in orient:
            # PW // o1[1] to max liczba rzędów orientacji o1 w szerokości 800mm
            for n1 in range(PW // o1[1] + 1):
                rem_y = PW - (n1 * o1[1])
                n2 = rem_y // o2[1]
                
                # Ilość sztuk w warstwie
                nx1, nx2 = PL // o1[0], PL // o2[0]
                nz1, nz2 = h_max // o1[2], h_max // o2[2]
                
                if nz1 == 0 and n1 > 0: continue
                if nz2 == 0 and n2 > 0: continue

                total = (n1 * nx1 * nz1) + (n2 * nx2 * nz2)
                
                # Tie-breaker: Jeśli total jest taki sam, wybierz ten, który lepiej pokrywa powierzchnię palety (stabilność)
                area_coverage = (n1 * nx1 * o1[0] * o1[1]) + (n2 * nx2 * o2[0] * o2[1])

                if total > best_total or (total == best_total and area_coverage > best_area):
                    best_total = total
                    best_area = area_coverage
                    best_layout = [
                        {'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(n1), int(nz1))},
                        {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(n2), int(nz2))}
                    ]
    return best_layout, best_total

# --- 5. WIDOK ---
c1, c2 = st.columns([1, 1.5])

if tryb == "📦 Paczka Kurierska":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        with c1:
            st.subheader("🛠️ Instrukcja Pakowania")
            st.success(f"Spięto **{sztuk} szt.**")
            st.write(f"- Ułożenie: {rl}x{rw} mm")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout_3d([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else: st.error("❌ Przekroczono limity kuriera.")

else: # PALETA
    layout, total = optymalizuj_palete_stabilna(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Plan Załadunku")
            st.success(f"Razem na palecie: **{total} sztuk**")
            st.info("System wymieszał rzędy (np. 3+1), aby zminimalizować luki.")
            st.divider()
            for i, b in enumerate(layout):
                s = b['count'][0]*b['count'][1]*b['count'][2]
                if s > 0:
                    st.write(f"**Sekcja {i+1} ({s} szt.):**")
                    st.write(f"- Karton: {b['dims'][0]}x{b['dims'][1]} (H:{b['dims'][2]})")
                    st.write(f"- Układ: {b['count'][1]} rzędów, {b['count'][2]} warstw.")
        with c2: st.plotly_chart(rysuj_layout_3d(layout, is_pallet=True), use_container_width=True)
    else: st.error("❌ Karton za duży!")
