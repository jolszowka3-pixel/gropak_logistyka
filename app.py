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

# --- 2. PEŁNA BAZA TWOICH KARTONÓW (Wymiary Zew: wew + 5mm) ---
PUDEŁKA_GROPAK = {
    "A11 (600x255x185)": {"L": 600, "W": 255, "H": 185},
    "B12 (600x300x235)": {"L": 600, "W": 300, "H": 235},
    "C13 (600x235x180)": {"L": 600, "W": 235, "H": 180},
    "D14 (600x285x210)": {"L": 600, "W": 285, "H": 210},
    "E15 (600x285x250)": {"L": 600, "W": 285, "H": 250},
    "F16 (600x365x255)": {"L": 600, "W": 365, "H": 255},
    "G17 (600x365x270)": {"L": 600, "W": 365, "H": 270},
    "H18 (600x380x300)": {"L": 600, "W": 380, "H": 300},
    "I19 (460x330x300)": {"L": 460, "W": 330, "H": 300},
    "K20 (490x390x300)": {"L": 490, "W": 390, "H": 300},
    "L21 (490x435x300)": {"L": 490, "W": 435, "H": 300},
    "Karton na wiórka (385x385x245)": {"L": 385, "W": 385, "H": 245},
    "Zbiorczy papier 625 (395x395x625)": {"L": 395, "W": 395, "H": 625},
    "Zbiorczy papier 425 (395x395x425)": {"L": 395, "W": 395, "H": 425},
    "Dyspenser 200ka (215x355x280)": {"L": 215, "W": 355, "H": 280},
    "Dyspenser 400ka (415x260x185)": {"L": 415, "W": 260, "H": 185},
    "Zbiorczy dyspenser 200 (370x270x290)": {"L": 370, "W": 270, "H": 290},
    "Zbiorczy dyspenser 400 (470x250x195)": {"L": 470, "W": 250, "H": 195},
    "Karton na folię (475x475x505)": {"L": 475, "W": 475, "H": 505},
    "Karton na folię (355x355x605)": {"L": 355, "W": 355, "H": 605},
    "Karton na folię (605x605x505)": {"L": 605, "W": 605, "H": 505},
    "Karton na folię (305x305x1225)": {"L": 305, "W": 305, "H": 1225},
    "Wypełniacz 295 (300x300x415)": {"L": 300, "W": 300, "H": 415},
    "Karton 90x90 (95x95x615)": {"L": 95, "W": 95, "H": 615},
    "Karton 160x160 (165x165x615)": {"L": 165, "W": 165, "H": 615},
    "Karton 230x230 (235x235x615)": {"L": 235, "W": 235, "H": 615},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0}
}

KOLOR_KARTONU = "#C19A6B"
TOLERANCJA_H = 50  # 50mm naddatku wysokości (klucz do 64 sztuk A11)

st.set_page_config(page_title="Gropak Master Pro", layout="wide")
st.title("📦 Gropak: Optymalizacja Wysyłek")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł zew (mm)", 10); W = st.number_input("Szer zew (mm)", 10); H = st.number_input("Wys zew (mm)", 10)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H = p["L"], p["W"], p["H"]
    
    st.divider()
    st.header("2. Metoda")
    tryb = st.radio("Tryb:", ["📦 Paczka Kurierska", "🚛 Paleta EURO"])

    if tryb == "📦 Paczka Kurierska":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość towaru (mm):", 100, 2500, 2000)

# --- 3. WIZUALIZACJA (PANCERNA, BEZ TRÓJKĄTÓW I BEZ SIATKI) ---
def rysuj_layout(bloki, is_pallet=False):
    fig = go.Figure()
    
    # Mikroskopijna przerwa między kartonami, aby wyeliminować błędy renderowania styku
    gap = 0.1 

    def dodaj_sciane(x, y, z, kolor, border=True, sa=2):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=sa, surfacecolor=kolor,
            line=dict(color='black', width=2.5 if border else 0),
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        # 6 płaszczyzn budowanych metodą surfaceaxis - czyste, płaskie ściany bez triangulacji
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, border, 2) # Góra
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, border, 2) # Dół
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, border, 1) # Front
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, border, 1) # Tył
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z, z+h, z+h, z], kolor, border, 0) # Lewo
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z, z+h, z+h, z], kolor, border, 0) # Prawo

    if is_pallet:
        pc = "#4E342E" # Ciemne drewno
        # Płozy i klocki palety rysujemy bez przerw, bo ich orientacja jest stała
        for y in [0, 350, 700]: dodaj_bryle(0, y, -144, 1200, 100, 22, pc, False) # Płozy
        for x in [0, 525, 1050]:
            for y in [0, 350, 700]: dodaj_bryle(x, y, -122, 150, 100, 78, pc, False) # Klocki
        for y in [0, 175, 350, 525, 700]: dodaj_bryle(0, y, -44, 1200, 100, 44, pc, False) # Deski

    for b in bloki:
        x0, y0, z0, (dl, sz, wy) = b['pos'][0], b['pos'][1], b['pos'][2], b['dims']
        for ix in range(b['count'][0]):
            for iy in range(b['count'][1]):
                for iz in range(b['count'][2]):
                    # Aplikujemy mikroszczelinę podczas rysowania pudełek
                    cx = x0 + ix*dl + gap
                    cy = y0 + iy*sz + gap
                    cz = z0 + iz*wy + gap
                    cdl = dl - 2*gap
                    csz = sz - 2*gap
                    cwy = wy - 2*gap
                    
                    # Rysujemy pudełko z naddatkiem wolnej przestrzeni
                    if cdl > 0 and csz > 0 and cwy > 0:
                        dodaj_bryle(cx, cy, cz, cdl, csz, cwy, KOLOR_KARTONU)
    
    hide_axis = dict(showbackground=False, visible=False)
    fig.update_layout(
        scene=dict(
            aspectmode='data', camera=dict(eye=dict(x=1.8, y=1.8, z=1.5)),
            xaxis=hide_axis, yaxis=hide_axis, zaxis=hide_axis
        ),
        margin=dict(l=10, r=10, b=10, t=10), paper_bgcolor="white",
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#444", width=3))]
    )
    return fig

# --- 4. LOGIKA OBLICZEŃ (STABILNA I MAKSYMALNA) ---
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

def optymalizuj_palete_maksymalna(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = get_orientations(L, W, H)
    best_total = 0
    best_footprint_score = 0
    best_layout = []

    # Szukamy absolutnego maksimum sztuk sprawdzając każdą możliwą orientację warstwy
    for o1 in orient:
        for o2 in orient:
            for n1 in range(PW // o1[1] + 1):
                rem_y = PW - n1*o1[1]
                n2 = rem_y // o2[1]
                
                # Ilość sztuk w JEDNEJ warstwie dla obu orientacji
                layer_n1 = (PL // o1[0]) * n1
                layer_n2 = (PL // o2[0]) * n2
                
                # Warstwy (nz) - zastosowanie tolerancji wysokości dla maksymalnego upchnięcia
                nz1 = (h_max + TOLERANCJA_H) // o1[2]
                nz2 = (h_max + TOLERANCJA_H) // o2[2]
                
                total = (layer_n1 * nz1) + (layer_n2 * nz2)
                # Wynik pokrycia podłogi (mm2) dla stabilizacji przy takim samym totalu
                footprint = (layer_n1 * o1[0] * o1[1]) + (layer_n2 * o2[0] * o2[1])
                
                # Wybieramy układ, który daje WIĘCEJ SZTUK TOTALNIE LUB lepiej kryje podłogę
                if total > best_total or (total == best_total and footprint > best_footprint_score):
                    best_total = total
                    best_footprint_score = footprint
                    best_layout = [
                        {'pos': (0, 0, 0), 'dims': o1, 'count': (int(PL // o1[0]), int(n1), int(nz1))},
                        {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(PL // o2[0]), int(n2), int(nz2))}
                    ]
    return best_layout, best_total

# --- 5. INTERFEJS ---
c1, c2 = st.columns([1, 1.5])

if tryb == "📦 Paczka Kurierska":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        with c1:
            st.subheader("📋 Instrukcja")
            st.success(f"Razem: {sztuk} szt.")
            st.write(f"- Ułożenie kartonu: {rl}x{rw} mm")
            st.write(f"- Układ: {nx} rz. x {ny} kol. x {nz} warstw")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else: st.error("Nie mieści się w limitach przewoźnika!")

else:
    layout, total = optymalizuj_palete_maksymalna(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Plan Palety")
            st.success(f"Suma: **{total} sztuk**")
            st.divider()
            for i, b in enumerate(layout):
                s = b['count'][0]*b['count'][1]*b['count'][2]
                if s > 0:
                    st.write(f"**Sekcja {i+1}** ({s} szt.):")
                    st.write(f"- Karton bokiem: {b['dims'][0]}x{b['dims'][1]} mm")
                    st.write(f"- Układ: {b['count'][1]} rz. x {b['count'][0]} szt. ({b['count'][2]} warstw)")
        with c2: st.plotly_chart(rysuj_layout(layout, is_pallet=True), use_container_width=True)
    else: st.error("Nie mieści się!")
