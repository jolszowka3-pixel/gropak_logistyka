import streamlit as st
import plotly.graph_objects as go
import numpy as np
import hashlib

try:
    from py3dbp import Packer, Bin, Item
except ImportError:
    st.error("🚨 Brak wymaganej biblioteki! Wpisz w terminalu: pip install py3dbp")
    st.stop()

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
    "Zbiorczy na dyspenser 200 (370x270x290)": {"L": 370, "W": 270, "H": 290},
    "Zbiorczy na dyspenser 400 (470x250x195)": {"L": 470, "W": 250, "H": 195},
    "Karton na folię (475x475x505)": {"L": 475, "W": 475, "H": 505},
    "Wypełniacz 295 (300x300x415)": {"L": 300, "W": 300, "H": 415},
    "Karton 90x90 (95x95x615)": {"L": 95, "W": 95, "H": 615},
    "Karton 160x160 (165x165x615)": {"L": 165, "W": 165, "H": 615},
    "Karton 230x230 (235x235x615)": {"L": 235, "W": 235, "H": 615},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0}
}

KOLOR_BAZOWY = "#C19A6B"
PALETA_KOLOROW = ["#C19A6B", "#D2B48C", "#E6C280", "#B8860B", "#CD853F", "#DEB887", "#F4A460", "#D2691E", "#A0522D"]

def generuj_kolor(nazwa):
    # Generuje stały odcień z palety na podstawie nazwy kartonu (dla wizualnego odróżnienia miksu)
    idx = int(hashlib.sha256(nazwa.encode('utf-8')).hexdigest(), 16) % len(PALETA_KOLOROW)
    return PALETA_KOLOROW[idx]

# --- INICJALIZACJA KOSZYKA W SESJI ---
if 'koszyk' not in st.session_state:
    st.session_state['koszyk'] = []

st.set_page_config(page_title="Gropak Master Pro", layout="wide")
st.title("📦 Gropak: Optymalizacja Wysyłek")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Tryb Pracy")
    tryb = st.radio("Metoda:", ["📦 Paczka Kurierska (1 rodzaj)", "🚛 Paleta EURO (Miks Kartonów)"])
    st.divider()

    if tryb == "📦 Paczka Kurierska (1 rodzaj)":
        st.header("2. Towar i Kurier")
        wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
        if wybrane == "Własny wymiar...":
            L = st.number_input("Dł zew (mm)", 10, value=100); W = st.number_input("Szer zew (mm)", 10, value=100); H = st.number_input("Wys zew (mm)", 10, value=100)
        else:
            p = PUDEŁKA_GROPAK[wybrane]; L, W, H = p["L"], p["W"], p["H"]
        
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 200, 6)

    else:
        st.header("2. Koszyk na Paletę")
        h_max = st.number_input("Maks. wysokość towaru na palecie (mm):", 100, 3500, 2000)
        st.divider()
        
        # Formularz dodawania do koszyka
        with st.form("dodaj_towar"):
            st.subheader("Dodaj asortyment")
            wybrane_miks = st.selectbox("Rodzaj kartonu:", list(PUDEŁKA_GROPAK.keys()))
            col_l, col_w, col_h = st.columns(3)
            with col_l: L_miks = st.number_input("Dł (mm)", 0, value=PUDEŁKA_GROPAK[wybrane_miks]["L"])
            with col_w: W_miks = st.number_input("Sz (mm)", 0, value=PUDEŁKA_GROPAK[wybrane_miks]["W"])
            with col_h: H_miks = st.number_input("Wy (mm)", 0, value=PUDEŁKA_GROPAK[wybrane_miks]["H"])
            
            sztuk_miks = st.number_input("Ilość sztuk:", 1, 1000, 10)
            
            if st.form_submit_button("➕ Dodaj do palety"):
                nazwa = wybrane_miks if wybrane_miks != "Własny wymiar..." else f"Custom {L_miks}x{W_miks}x{H_miks}"
                st.session_state['koszyk'].append({"nazwa": nazwa, "L": L_miks, "W": W_miks, "H": H_miks, "ilosc": sztuk_miks})
                st.rerun()

        # Wyświetlanie zawartości koszyka
        if st.session_state['koszyk']:
            st.write("🛒 **Aktualny załadunek:**")
            for idx, item in enumerate(st.session_state['koszyk']):
                st.caption(f"- {item['ilosc']}x {item['nazwa']}")
            
            if st.button("🗑️ Wyczyść paletę"):
                st.session_state['koszyk'] = []
                st.rerun()

# --- 3. WIZUALIZACJA 3D ---
def rysuj_layout(bloki, is_pallet=False):
    fig = go.Figure()
    
    def dodaj_sciane(x, y, z, kolor, sa):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            surfaceaxis=sa, surfacecolor=kolor,
            opacity=1, line=dict(width=0), 
            showlegend=False, hoverinfo='skip'
        ))

    def dodaj_krawedzie(x, y, z, l, w, h):
        lx = [x, x+l, x+l, x, x, None, x, x+l, x+l, x, x, None, x, x, None, x+l, x+l, None, x+l, x+l, None, x, x]
        ly = [y, y, y+w, y+w, y, None, y, y, y+w, y+w, y, None, y, y, None, y, y, None, y+w, y+w, None, y+w, y+w]
        lz = [z, z, z, z, z, None, z+h, z+h, z+h, z+h, z+h, None, z, z+h, None, z, z+h, None, z, z+h, None, z, z+h]
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), showlegend=False, hoverinfo='skip'))

    def dodaj_bryle(x, y, z, l, w, h, kolor, border=True):
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z+h, z+h, z+h, z+h, z+h], kolor, 2)
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y+w, y+w, y], [z, z, z, z, z], kolor, 2)
        dodaj_sciane([x, x+l, x+l, x, x], [y, y, y, y, y], [z, z, z+h, z+h, z], kolor, 1)
        dodaj_sciane([x, x+l, x+l, x, x], [y+w, y+w, y+w, y+w, y+w], [z, z, z+h, z+h, z], kolor, 1)
        dodaj_sciane([x, x, x, x, x], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, 0)
        dodaj_sciane([x+l, x+l, x+l, x+l, x+l], [y, y, y+w, y+w, y], [z, z+h, z+h, z, z], kolor, 0)
        if border: dodaj_krawedzie(x, y, z, l, w, h)

    if is_pallet:
        pc = "#4E342E"
        for y_off in [0, 350, 700]: dodaj_bryle(0, y_off, -144, 1200, 100, 22, pc, False)
        for x_off in [0, 525, 1050]:
            for y_off in [0, 350, 700]: dodaj_bryle(x_off, y_off, -122, 150, 100, 78, pc, False)
        for y_off in [0, 175, 350, 525, 700]: dodaj_bryle(0, y_off, -44, 1200, 100, 44, pc, False)

    for b in bloki:
        x0, y0, z0, (dl, sz, wy) = b['pos'][0], b['pos'][1], b['pos'][2], b['dims']
        kolor = b.get('color', KOLOR_BAZOWY)
        for ix in range(b['count'][0]):
            for iy in range(b['count'][1]):
                for iz in range(b['count'][2]):
                    dodaj_bryle(x0+ix*dl, y0+iy*sz, z0+iz*wy, dl, sz, wy, kolor)
    
    hide = dict(showbackground=False, visible=False)
    fig.update_layout(
        scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.8, y=1.8, z=1.5)), xaxis=hide, yaxis=hide, zaxis=hide),
        margin=dict(l=5, r=5, b=5, t=5), paper_bgcolor="white",
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#444", width=3))]
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
                    if "Paczkomat" in k_name: ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"])
                    else: ok = (ds[0] <= k["max_L"] and girth <= k["max_G"])
                    if ok:
                        score = abs(fL-fW) + abs(fW-fH) + abs(fL-fH)
                        wyniki.append({"conf": (nx, ny, nz), "dims": (rl, rw, rh), "final": (fL, fW, fH), "score": score})
    return sorted(wyniki, key=lambda x: x['score'])[0] if wyniki else None

def optymalizuj_palete_miks(koszyk, h_max):
    packer = Packer()
    # Ignorujemy wagę fizyczną (999999 kg)
    packer.add_bin(Bin('Paleta EURO', 1200, 800, h_max, 999999.0))

    for item in koszyk:
        for i in range(item['ilosc']):
            # Symboliczna waga 0.1
            packer.add_item(Item(item['nazwa'], item['L'], item['W'], item['H'], 0.1))

    packer.pack()
    paleta = packer.bins[0]
    
    layout = []
    for fitted_item in paleta.items:
        x, y, z = [int(v) for v in fitted_item.position]
        w, h, d = [int(v) for v in fitted_item.get_dimension()]
        layout.append({
            'pos': (x, y, z),
            'dims': (w, h, d),
            'count': (1, 1, 1),
            'color': generuj_kolor(fitted_item.name),
            'name': fitted_item.name
        })
        
    zapakowane = len(paleta.items)
    odrzucone = len(paleta.unfitted_items)
    return layout, zapakowane, odrzucone

# --- 5. INTERFEJS GŁÓWNY ---
c1, c2 = st.columns([1, 2])

if tryb == "📦 Paczka Kurierska (1 rodzaj)":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        with c1:
            st.subheader("📋 Instrukcja")
            st.success(f"Razem: {sztuk} szt.")
            st.write(f"- Ułożenie bazy: {rl}x{rw} mm")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else: st.error("Nie mieści się!")

else:
    if not st.session_state['koszyk']:
        st.info("👈 Dodaj kartony do palety w panelu bocznym.")
    else:
        layout, spakowane, odrzucone = optymalizuj_palete_miks(st.session_state['koszyk'], h_max)
        
        with c1:
            st.subheader("📋 Status Palety")
            st.success(f"Ułożono sztuk: **{spakowane}**")
            if odrzucone > 0:
                st.error(f"⚠️ Nie zmieściło się: **{odrzucone}** szt. (przekroczono limit wysokości {h_max} mm)")
            
            st.divider()
            st.write("**Legenda ułożenia:**")
            # Unikalne nazwy dla legendy
            unikalne_pudelka = {b['name']: b['color'] for b in layout}
            for nazwa, kolor in unikalne_pudelka.items():
                st.markdown(f'<div style="display:flex; align-items:center; margin-bottom:5px;"><div style="width:15px; height:15px; background-color:{kolor}; border:1px solid #000; margin-right:10px;"></div>{nazwa}</div>', unsafe_allow_html=True)
                
        with c2: 
            st.plotly_chart(rysuj_layout(layout, is_pallet=True), use_container_width=True)
