import streamlit as st
import plotly.graph_objects as go
import hashlib
import numpy as np
import math

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

# --- 2. BAZA KARTONÓW ---
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

PALETA_KOLOROW = ["#C19A6B", "#D2B48C", "#E6C280", "#B8860B", "#CD853F", "#DEB887", "#F4A460", "#D2691E", "#A0522D"]

def generuj_kolor(nazwa):
    idx = int(hashlib.sha256(nazwa.encode('utf-8')).hexdigest(), 16) % len(PALETA_KOLOROW)
    return PALETA_KOLOROW[idx]

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
            st.info(f"📏 Wymiary z bazy: **{L} x {W} x {H} mm**")
        
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 200, 6)

    else:
        st.header("2. Koszyk na Paletę")
        h_max = st.number_input("Maks. wysokość towaru na palecie (mm):", 100, 3500, 2000)
        st.divider()
        
        st.subheader("Dodaj asortyment")
        wybrane_miks = st.selectbox("Rodzaj kartonu:", list(PUDEŁKA_GROPAK.keys()))
        
        if wybrane_miks == "Własny wymiar...":
            col_l, col_w, col_h = st.columns(3)
            with col_l: L_miks = st.number_input("Dł (mm)", 1, value=100)
            with col_w: W_miks = st.number_input("Sz (mm)", 1, value=100)
            with col_h: H_miks = st.number_input("Wy (mm)", 1, value=100)
        else:
            L_miks = PUDEŁKA_GROPAK[wybrane_miks]["L"]
            W_miks = PUDEŁKA_GROPAK[wybrane_miks]["W"]
            H_miks = PUDEŁKA_GROPAK[wybrane_miks]["H"]
            st.info(f"📏 Wymiary z bazy: **{L_miks} x {W_miks} x {H_miks} mm**")
            
        sztuk_miks = st.number_input("Ilość sztuk:", 1, 1000, 10)
        
        if st.button("➕ Dodaj do palety", use_container_width=True):
            nazwa = wybrane_miks if wybrane_miks != "Własny wymiar..." else f"Custom {L_miks}x{W_miks}x{H_miks}"
            st.session_state['koszyk'].append({"nazwa": nazwa, "L": L_miks, "W": W_miks, "H": H_miks, "ilosc": sztuk_miks})
            st.rerun()

        st.divider()
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
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3), showlegend=False, hoverinfo='skip'))

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
        kolor = b.get('color', "#C19A6B")
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

# --- 4. LOGIKA: Z-MAP ENGINE (GRAVITY & STABILITY) ---
class PaletaZMap:
    def __init__(self, w=1200, d=800, h_max=2000):
        self.w = w
        self.d = d
        self.h_max = h_max
        # Wirtualna siatka palety: każda komórka to kwadrat 10x10 mm
        self.grid_w = w // 10
        self.grid_d = d // 10
        self.height_map = np.zeros((self.grid_w, self.grid_d), dtype=int)
        self.items = []

    def check_fit(self, gw, gd, h):
        best_z = float('inf')
        best_pos = None

        for x in range(self.grid_w - gw + 1):
            for y in range(self.grid_d - gd + 1):
                # Patrzymy na wybrany prostokąt na palecie
                subgrid = self.height_map[x:x+gw, y:y+gd]
                # Zawsze opieramy się o najwyższy punkt pod spodem (GRAWITACJA)
                max_z = np.max(subgrid)

                if max_z + h <= self.h_max:
                    # WYMÓG STABILNOŚCI: Przynajmniej 60% kartonu musi leżeć na płaskim, stabilnym gruncie (max_z)
                    support_area = np.sum(subgrid == max_z)
                    total_area = gw * gd
                    
                    if support_area / total_area >= 0.6:
                        # Oceniamy pozycję: chcemy spakować jak najniżej, a w przypadku remisu dosunąć do rogu palety
                        score = max_z * 10000 + (x**2 + y**2)
                        if score < best_z:
                            best_z = score
                            best_pos = (x, y, max_z)
        return best_pos

    def pack_item(self, item):
        L, W, H = item['L'], item['W'], item['H']
        # Rezerwacja przestrzeni: zaokrąglamy ułamki w górę co 10mm (symuluje milimetrowe odstępy na karton)
        gw_L = int(math.ceil(L / 10.0))
        gd_W = int(math.ceil(W / 10.0))
        
        gw_W = int(math.ceil(W / 10.0))
        gd_L = int(math.ceil(L / 10.0))

        # Symulacja dwóch ułożeń na płasko (Zawsze H do góry!)
        pos1 = self.check_fit(gw_L, gd_W, H)
        pos2 = self.check_fit(gw_W, gd_L, H)

        best_pos = None
        best_dim = None
        gw, gd = 0, 0

        # Wybieramy ułożenie, które ląduje niżej w przestrzeni palety
        if pos1 and pos2:
            if pos1[2] <= pos2[2]:
                best_pos, best_dim, gw, gd = pos1, (L, W, H), gw_L, gd_W
            else:
                best_pos, best_dim, gw, gd = pos2, (W, L, H), gw_W, gd_L
        elif pos1:
            best_pos, best_dim, gw, gd = pos1, (L, W, H), gw_L, gd_W
        elif pos2:
            best_pos, best_dim, gw, gd = pos2, (W, L, H), gw_W, gd_L

        if best_pos:
            x, y, z = best_pos
            # Rzutujemy pudło z powrotem na siatkę - aktualizujemy wysokości
            self.height_map[x:x+gw, y:y+gd] = z + H

            self.items.append({
                'pos': (x * 10, y * 10, z),
                'dims': best_dim, # Rysujemy dokładny wymiar z bazy
                'count': (1, 1, 1),
                'name': item['nazwa'],
                'color': item['color']
            })
            return True
        return False

def optymalizuj_palety_wielokrotne(koszyk, h_max):
    elementy = []
    odrzucone_lista = []

    for wpis in koszyk:
        # Skrajne przypadki błędu ludzkiego (karton większy niż paleta)
        if wpis['H'] > h_max or max(wpis['L'], wpis['W']) > 1200 or min(wpis['L'], wpis['W']) > 800:
            odrzucone_lista.append(wpis)
            continue
        for _ in range(wpis['ilosc']):
            elementy.append({
                'nazwa': wpis['nazwa'], 'L': wpis['L'], 'W': wpis['W'], 'H': wpis['H'],
                'color': generuj_kolor(wpis['nazwa'])
            })

    # KLUCZ SUKCESU: Sortujemy kartony od największego "poligona" (Dł x Szer).
    # To zapewnia, że budujemy stabilną bazę a małe pudełka wypełniają dziury u góry!
    elementy.sort(key=lambda x: (x['L'] * x['W'], x['H']), reverse=True)

    palety = []
    aktualna_paleta = PaletaZMap(h_max=h_max)
    niezapakowane_teraz = []

    for item in elementy:
        if not aktualna_paleta.pack_item(item):
            niezapakowane_teraz.append(item)

    if aktualna_paleta.items:
        palety.append(aktualna_paleta.items)

    # Generowanie kolejnych palet aż do skutku
    while niezapakowane_teraz:
        aktualna_paleta = PaletaZMap(h_max=h_max)
        elementy_do_spakowania = niezapakowane_teraz
        niezapakowane_teraz = []

        for item in elementy_do_spakowania:
            if not aktualna_paleta.pack_item(item):
                niezapakowane_teraz.append(item)
                
        if len(aktualna_paleta.items) == 0:
            # Odcięcie nieskończonej pętli - kartony nie do wciśnięcia
            odrzucone_lista.extend(niezapakowane_teraz)
            break
            
        palety.append(aktualna_paleta.items)

    return palety, odrzucone_lista

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
        with st.spinner("📦 Składanie palet... Pracuje silnik fizyczny Z-Map (to może chwilę potrwać)"):
            palety, odrzucone = optymalizuj_palety_wielokrotne(st.session_state['koszyk'], h_max)
        
        with c1:
            st.subheader("📋 Podsumowanie Zlecenia")
            st.success(f"📦 Zbudowano stabilnych palet: **{len(palety)}**")
            
            if odrzucone:
                st.error("⚠️ Odrzucono (nie fizyczne do ułożenia):")
                for err in odrzucone:
                    st.caption(f"- {err['nazwa']} ({err['L']}x{err['W']}x{err['H']})")
            
            st.divider()
            st.write("**Legenda asortymentu:**")
            unikalne = {}
            for p in palety:
                for b in p: unikalne[b['name']] = b['color']
            for nazwa, kolor in unikalne.items():
                st.markdown(f'<div style="display:flex; align-items:center; margin-bottom:5px;"><div style="width:15px; height:15px; background-color:{kolor}; border:1px solid #000; margin-right:10px;"></div>{nazwa}</div>', unsafe_allow_html=True)
                
        with c2:
            if palety:
                zakladki = st.tabs([f"🚛 Paleta {i+1}" for i in range(len(palety))])
                for i, paleta_layout in enumerate(palety):
                    with zakladki[i]:
                        st.write(f"**Zawartość: {len(paleta_layout)} sztuk** na tej palecie.")
                        st.plotly_chart(rysuj_layout(paleta_layout, is_pallet=True), use_container_width=True)
