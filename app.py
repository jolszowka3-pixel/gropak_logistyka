import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

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

# --- 2. PEŁNA BAZA TWOICH KARTONÓW ---
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
    "Zbiorczy papier 620 (390x390x620)": {"L": 390, "W": 390, "H": 620},
    "Zbiorczy papier 420 (390x390x420)": {"L": 390, "W": 390, "H": 420},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275},
    "Dyspenser 400ka (410x255x180)": {"L": 410, "W": 255, "H": 180},
    "Zbiorczy na dyspenser 200 (365x265x285)": {"L": 365, "W": 265, "H": 285},
    "Zbiorczy na dyspenser 400 (465x245x190)": {"L": 465, "W": 245, "H": 190},
    "Karton na folię (470x470x500)": {"L": 470, "W": 470, "H": 500},
    "Karton na folię (350x350x600)": {"L": 350, "W": 350, "H": 600},
    "Karton na folię (600x600x500)": {"L": 600, "W": 600, "H": 500},
    "Karton na folię (300x300x1220)": {"L": 300, "W": 300, "H": 1220},
    "Wypełniacz 295x295 (H:410)": {"L": 295, "W": 295, "H": 410},
    "Wypełniacz 230x230 (H:410)": {"L": 230, "W": 230, "H": 410},
    "Karton 90x90 (H:610)": {"L": 90, "W": 90, "H": 610},
    "Karton 160x160 (H:610)": {"L": 160, "W": 160, "H": 610},
    "Karton 230x230 (H:610)": {"L": 230, "W": 230, "H": 610},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0}
}

KOLOR_KARTONU = "#C19A6B"

st.set_page_config(page_title="Gropak - System Optymalizacji", layout="wide")

# CSS do drukowania - wymusza widoczność grafik
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, [data-testid="stToolbar"] { display: none !important; }
        .main { background-color: white !important; }
        .stPlotlyChart { visibility: visible !important; display: block !important; }
    }
    </style>
    """, unsafe_allow_html=True)

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
    tryb = st.radio("Metoda:", ["📦 Paczka Kurierska", "🚛 Paleta EURO"])

    if tryb == "📦 Paczka Kurierska":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość towaru (mm):", 100, 2500, 1600)

# --- 3. WIZUALIZACJA BEZ TRÓJKĄTÓW (ONLY SCATTER3D SURFACES) ---
def rysuj_layout(bloki, is_pallet=False, view_type="3d"):
    fig = go.Figure()
    
    def dodaj_sciane(x, y, z, kolor, border=True):
        # Scatter3d z surfaceaxis to jedyny sposób na 100% płaskie ściany bez skosów
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=0 if len(set(x)) == 1 else (1 if len(set(y)) == 1 else 2),
            surfacecolor=kolor,
            line=dict(color='black', width=2.5 if border else 0),
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        # Góra i Dół
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, border)
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, border)
        # Boki
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, border)
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, border)
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border)
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, border)

    if is_pallet:
        pc = "#4E342E" # Ciemne drewno
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
    
    camera_config = {
        "3d": dict(eye=dict(x=1.8, y=1.8, z=1.5), projection=dict(type='perspective')),
        "top": dict(eye=dict(x=0, y=0, z=2.5), up=dict(x=0, y=1, z=0), projection=dict(type='orthographic')),
        "front": dict(eye=dict(x=0, y=3, z=0), up=dict(x=0, y=0, z=1), projection=dict(type='orthographic')),
        "side": dict(eye=dict(x=3, y=0, z=0), up=dict(x=0, y=0, z=1), projection=dict(type='orthographic'))
    }
    
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            camera=camera_config.get(view_type, camera_config["3d"]),
            xaxis=dict(visible=True if view_type=="3d" else False),
            yaxis=dict(visible=True if view_type=="3d" else False),
            zaxis=dict(visible=True if view_type=="3d" else False)
        ),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor="white"
    )
    return fig

# --- 4. LOGIKA ---
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

def optymalizuj_palete_plecakowa(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = get_orientations(L, W, H)
    best_total = 0; best_layout = []
    for o1 in orient:
        for o2 in orient:
            for n1 in range(PW // o1[1] + 1):
                rem_y = PW - n1*o1[1]
                n2 = rem_y // o2[1]
                nx1, nx2 = PL // o1[0], PL // o2[0]
                nz1, nz2 = h_max // o1[2], h_max // o2[2]
                if (nz1 == 0 and n1 > 0) or (nz2 == 0 and n2 > 0): continue
                total = (n1 * nx1 * nz1) + (n2 * nx2 * nz2)
                if total > best_total:
                    best_total = total
                    best_layout = [{'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(n1), int(nz1))},
                                   {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(n2), int(nz2))}]
    return best_layout, best_total

# --- 5. INTERFEJS ---
c1, c2 = st.columns([1, 1.5])

if tryb == "📦 Paczka Kurierska":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        with c1:
            st.subheader("📋 Instrukcja")
            st.success(f"Razem: {sztuk} szt. | Ułożenie: {rl}x{rw} mm")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else: st.error("Nie mieści się!")
else:
    layout, total = optymalizuj_palete_plecakowa(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Plan Palety")
            st.success(f"Suma: **{total} szt.**")
            st.write(f"Wysokość towaru: {h_max} mm")
            st.divider()
            for i, b in enumerate(layout):
                s = b['count'][0]*b['count'][1]*b['count'][2]
                if s > 0: st.write(f"**Sekcja {i+1}**: {s} szt. ({b['dims'][0]}x{b['dims'][1]} mm)")
        with c2: st.plotly_chart(rysuj_layout(layout, is_pallet=True), use_container_width=True)

        # --- KARTA ZAŁADUNKU (Wersja 100% do druku) ---
        st.markdown("<br><hr style='border: 2px solid black;'><br>", unsafe_allow_html=True)
        st.header("📄 KARTA ZAŁADUNKU DLA MAGAZYNU")
        st.markdown(f"### **PRODUKT:** {wybrane} | **SUMA:** {total} SZTUK")
        
        # Klucz do druku: staticPlot=True zamienia wykres w obrazek
        col_t, col_f, col_s = st.columns(3)
        with col_t:
            st.write("**RZUT Z GÓRY**")
            st.plotly_chart(rysuj_layout(layout, is_pallet=True, view_type="top"), use_container_width=True, config={'staticPlot': True})
        with col_f:
            st.write("**RZUT OD FRONTU**")
            st.plotly_chart(rysuj_layout(layout, is_pallet=True, view_type="front"), use_container_width=True, config={'staticPlot': True})
        with col_s:
            st.write("**RZUT Z BOKU**")
            st.plotly_chart(rysuj_layout(layout, is_pallet=True, view_type="side"), use_container_width=True, config={'staticPlot': True})
        
        st.subheader("📝 INSTRUKCJA")
        for i, b in enumerate(layout):
            s = b['count'][0]*b['count'][1]*b['count'][2]
            if s > 0:
                st.markdown(f"**SEKCJA {i+1}:** {s} szt. Połóż karton na boku **{b['dims'][0]}x{b['dims'][1]}**. Ułóż {b['count'][1]} rzędów po {b['count'][0]} szt. w {b['count'][2]} warstwach.")

        if st.button("🖨️ DRUKUJ KARTĘ ZAŁADUNKU"):
            components.html("<script>window.print();</script>", height=0)
    else: st.error("Nie mieści się!")
