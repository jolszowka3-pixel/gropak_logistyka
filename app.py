import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KURIERZY (mm i kg) ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 1750, "max_G": 3000, "max_W": 31.5},
    "DHL (Standard)": {"max_L": 1200, "max_G": 3000, "max_W": 31.5},
    "InPost Paczkomat C": {"L": 640, "W": 380, "H": 410, "max_W": 25.0},
    "InPost Kurier": {"max_L": 1200, "max_G": 2200, "max_W": 30.0},
    "Orlen Paczka L": {"L": 600, "W": 380, "H": 410, "max_W": 20.0},
    "GLS (Polska)": {"max_L": 2000, "max_G": 3000, "max_W": 31.5},
    "UPS Standard": {"max_L": 2740, "max_G": 4000, "max_W": 32.0},
    "Ambro Express": {"max_L": 3000, "max_G": 5000, "max_W": 50.0}
}

# --- TWOJA KOMPLETNA BAZA KARTONÓW ---
PUDEŁKA_GROPAK = {
    "Karton na wiórka (380x380x240)": {"L": 380, "W": 380, "H": 240, "Waga": 0.0},
    "Zbiorczy papier nacinany (390x390x620)": {"L": 390, "W": 390, "H": 620, "Waga": 0.0},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275, "Waga": 0.0},
    "A11 (595x250x180)": {"L": 595, "W": 250, "H": 180, "Waga": 0.0},
    "B12 (595x295x230)": {"L": 595, "W": 295, "H": 230, "Waga": 0.0},
    "K20 (485x385x295)": {"L": 485, "W": 385, "H": 295, "Waga": 0.0},
    "L21 (485x430x295)": {"L": 485, "W": 430, "H": 295, "Waga": 0.0},
    "Karton na folię (470x470x500)": {"L": 470, "W": 470, "H": 500, "Waga": 0.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

KOLOR_KARTONU = "#C19A6B"

st.set_page_config(page_title="Gropak Master Pro v8", layout="wide")
st.title("📦 Gropak: Ekstremalne Wypełnienie Palety")

with st.sidebar:
    st.header("1. Wybór towaru")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (mm)", 10); W = st.number_input("Szer (mm)", 10); H = st.number_input("Wys (mm)", 10)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H = p["L"], p["W"], p["H"]
    
    st.divider()
    h_max = st.number_input("Maks. wysokość palety (mm):", 200, 2500, 1600)

# --- GRAFIKA 3D (BEZ TRÓJKĄTÓW - PURE SURFACES) ---
def rysuj_layout_3d(bloki, is_pallet=False):
    fig = go.Figure()

    def dodaj_sciane(x, y, z, kolor, border=True):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=0 if len(set(x))==1 else (1 if len(set(y))==1 else 2),
            surfacecolor=kolor, line=dict(color='black', width=2.5 if border else 0),
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        # 6 płaszczyzn sześcianu - brak Mesh3d = brak trójkątów
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, border) # Góra
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, border) # Dół
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, border) # Front
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, border) # Tył
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border) # Lewo
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border) # Prawo

    if is_pallet:
        pc = "#4E342E"
        for y in [0, 350, 700]: dodaj_bryle(0, y, -144, 1200, 100, 22, pc, False) # Płozy
        for x in [0, 525, 1050]:
            for y in [0, 350, 700]: dodaj_bryle(x, y, -122, 150, 100, 78, pc, False) # Klocki
        for y in [0, 175, 350, 525, 700]: dodaj_bryle(0, y, -44, 1200, 100, 44, pc, False) # Deski

    for b in bloki:
        x0, y0, z0, l, w, h = b['pos'][0], b['pos'][1], b['pos'][2], b['dims'][0], b['dims'][1], b['dims'][2]
        nx, ny, nz = b['count']
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    dodaj_bryle(x0 + ix*l, y0 + iy*w, z0 + iz*h, l, w, h, KOLOR_KARTONU)

    fig.update_layout(
        scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.8, y=1.8, z=1.5))),
        margin=dict(l=10, r=10, b=10, t=10), paper_bgcolor="white",
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#e0e0e0", width=2))]
    )
    return fig

# --- LOGIKA EKSTREMALNEJ OPTYMALIZACJI (MIESZANE RZĘDY) ---
def optymalizuj_palete_plecakowa(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = list({(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)})
    
    best_n = 0
    best_layout = []

    # Sprawdzamy każdą orientację jako bazową dla rzędu
    # System próbuje wypełnić 800mm szerokości różnymi kombinacjami rzędów
    for o1 in orient:
        for o2 in orient:
            # Szukamy kombinacji n1 rzędów orientacji o1 i n2 rzędów orientacji o2
            for n1 in range(PW // o1[1] + 1):
                for n2 in range((PW - n1*o1[1]) // o2[1] + 1):
                    
                    # Liczymy sztuki w pionie dla każdej orientacji niezależnie!
                    nz1 = h_max // o1[2]
                    nz2 = h_max // o2[2]
                    
                    # Liczymy sztuki wzdłuż długości 1200mm
                    nx1 = PL // o1[0]
                    nx2 = PL // o2[0]
                    
                    total = (n1 * nx1 * nz1) + (n2 * nx2 * nz2)
                    
                    if total > best_n:
                        best_n = total
                        best_layout = [
                            {'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(n1), int(nz1))},
                            {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(n2), int(nz2))}
                        ]
    return best_layout, best_n

# --- WIDOK ---
c1, c2 = st.columns([1, 1.5])
layout, total = optymalizuj_palete_plecakowa(L, W, H, h_max)

if total > 0:
    with c1:
        st.subheader("📋 Plan Załadunku")
        st.success(f"Razem na palecie: **{total} sztuk**")
        st.info("System wymieszał orientacje rzędów, aby zredukować puste przestrzenie (np. 3+1).")
        st.divider()
        for i, b in enumerate(layout):
            s = b['count'][0]*b['count'][1]*b['count'][2]
            if s > 0:
                st.write(f"**Sekcja {i+1}:** {s} sztuk")
                st.write(f"- Ułożenie: {b['dims'][0]}x{b['dims'][1]} (H:{b['dims'][2]})")
                st.write(f"- Układ: {b['count'][1]} rzędów po {b['count'][0]} szt.")
    with c2:
        st.plotly_chart(rysuj_layout_3d(layout, is_pallet=True), use_container_width=True)
else:
    st.error("Karton nie mieści się na palecie!")
