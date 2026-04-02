import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- 1. KOMPLEKSOWA BAZA KURIERÓW ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 1750, "max_G": 3000, "max_W": 31.5},
    "DHL (Standard)": {"max_L": 1200, "max_G": 3000, "max_W": 31.5},
    "InPost Paczkomat C": {"L": 640, "W": 380, "H": 410, "max_W": 25.0},
    "InPost Kurier": {"max_L": 1200, "max_G": 2200, "max_W": 30.0},
    "GLS (Polska)": {"max_L": 2000, "max_G": 3000, "max_W": 31.5},
    "UPS Standard": {"max_L": 2740, "max_G": 4000, "max_W": 32.0},
    "Ambro Express": {"max_L": 3000, "max_G": 5000, "max_W": 50.0}
}

# --- 2. BAZA KARTONÓW (Wymiary Zew: wew + 5mm) ---
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
    "Zbiorczy papier (395x395x625)": {"L": 395, "W": 395, "H": 625},
    "Karton na folię (475x475x505)": {"L": 475, "W": 475, "H": 505},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0}
}

KOLOR_KARTONU = "#C19A6B"
TOLERANCJA_H = 50  # 50mm naddatku wysokości (klucz do 64 sztuk A11)

st.set_page_config(page_title="Gropak Master Pro", layout="wide")
st.title("📦 Gropak: Optymalizacja Wysyłek")

with st.sidebar:
    st.header("1. Wybór towaru")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł zew (mm)", 10); W = st.number_input("Szer zew (mm)", 10); H = st.number_input("Wys zew (mm)", 10)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H = p["L"], p["W"], p["H"]
    
    st.divider()
    st.header("2. Parametry")
    tryb = st.radio("Tryb:", ["📦 Paczka", "🚛 Paleta EURO"])
    if tryb == "📦 Paczka":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość towaru (mm):", 100, 2500, 2000)

# --- 3. WIZUALIZACJA (PANCERNA, BEZ TRÓJKĄTÓW I SIATKI) ---
def rysuj_layout(bloki, is_pallet=False):
    fig = go.Figure()
    
    def dodaj_sciane(x, y, z, kolor, border=True, sa=2):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=sa, surfacecolor=kolor,
            line=dict(color='black', width=2.5 if border else 0),
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        # 6 płaszczyzn - zero siatek, zero trójkątów
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, border, 2)
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, border, 2)
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, border, 1)
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, border, 1)
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z, z+h, z+h, z], kolor, border, 0)
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z, z+h, z+h, z], kolor, border, 0)

    if is_pallet:
        pc = "#4E342E"
        for y in [0, 350, 700]: dodaj_bryle(0, y, -144, 1200, 100, 22, pc, False)
        for x in [0, 525, 1050]:
            for y in [0, 350, 700]: dodaj_bryle(x, y, -122, 150, 100, 78, pc, False)
        for y in [0, 175, 350, 525, 700]: dodaj_bryle(0, y, -44, 1200, 100, 44, pc, False)

    for b in bloki:
        x0, y0, z0, (dl, sz, wy) = b['pos'][0], b['pos'][1], b['pos'][2], b['dims']
        for ix in range(b['count'][0]):
            for iy in range(b['count'][1]):
                for iz in range(b['count'][2]):
                    dodaj_bryle(x0+ix*dl, y0+iy*sz, z0+iz*wy, dl, sz, wy, KOLOR_KARTONU)
    
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

# --- 4. LOGIKA (NASTAWIONA NA MAKSYMALNĄ LICZBĘ SZTUK) ---
def get_orientations(L, W, H):
    return list({(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)})

def optymalizuj_palete_maksymalna(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = get_orientations(L, W, H)
    best_total = 0
    best_layout = []

    for o1 in orient:
        for o2 in orient:
            for n1 in range(PW // o1[1] + 1):
                rem_y = PW - n1*o1[1]
                n2 = rem_y // o2[1]
                nx1, nx2 = PL // o1[0], PL // o2[0]
                
                # Tolerancja wysokości pozwala na ułożenie warstwy, która wystaje max o 50mm
                nz1 = (h_max + TOLERANCJA_H) // o1[2]
                nz2 = (h_max + TOLERANCJA_H) // o2[2]
                
                total = (nx1 * n1 * nz1) + (nx2 * n2 * nz2)
                if total > best_total:
                    best_total = total
                    best_layout = [
                        {'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(n1), int(nz1))},
                        {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(n2), int(nz2))}
                    ]
    return best_layout, best_total

# --- 5. INTERFEJS ---
c1, c2 = st.columns([1, 1.5])
if tryb == "🚛 Paleta EURO":
    layout, total = optymalizuj_palete_maksymalna(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Plan Palety")
            st.success(f"Suma: **{total} sztuk**")
            st.info(f"Wysokość ładunku: {max([b['count'][2]*b['dims'][2] for b in layout if b['count'][2]>0])} mm")
            st.divider()
            for i, b in enumerate(layout):
                s = b['count'][0]*b['count'][1]*b['count'][2]
                if s > 0:
                    st.write(f"**Sekcja {i+1}** ({s} szt.):")
                    st.write(f"- Orientacja: {b['dims'][0]}x{b['dims'][1]} mm")
                    st.write(f"- Układ: {b['count'][1]} rz. x {b['count'][0]} szt. x {b['count'][2]} warstw")
        with c2: st.plotly_chart(rysuj_layout(layout, is_pallet=True), use_container_width=True)
