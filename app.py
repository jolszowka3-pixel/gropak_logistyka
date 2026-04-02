import streamlit as st
import plotly.graph_objects as go

# --- 1. BAZA KURIERÓW ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 1750, "max_G": 3000, "max_W": 31.5},
    "DHL (Standard)": {"max_L": 1200, "max_G": 3000, "max_W": 31.5},
    "InPost Paczkomat C": {"L": 640, "W": 380, "H": 410, "max_W": 25.0},
    "InPost Kurier": {"max_L": 1200, "max_G": 2200, "max_W": 30.0},
    "GLS (Polska)": {"max_L": 2000, "max_G": 3000, "max_W": 31.5},
    "Ambro Express": {"max_L": 3000, "max_G": 5000, "max_W": 50.0}
}

# --- 2. BAZA KARTONÓW (Zew: wew + 5mm) ---
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
    "Wypełniacz 295 (300x300x415)": {"L": 300, "W": 300, "H": 415},
    "Karton 90x90 (95x95x615)": {"L": 95, "W": 95, "H": 615},
    "Karton 160x160 (165x165x615)": {"L": 165, "W": 165, "H": 615},
    "Karton 230x230 (235x235x615)": {"L": 235, "W": 235, "H": 615}
}

KOLOR_KARTONU = "#C19A6B"
TOLERANCJA_H = 50 
MIX_COLORS = ["#C19A6B", "#8D6E63", "#78909C", "#5D4037", "#455A64", "#D7CCC8", "#A1887F", "#37474F"]

st.set_page_config(page_title="Gropak Master Pro - Mix Logistic", layout="wide")
st.title("📦 Gropak: System Optymalizacji Wysyłek")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Tryb Pracy")
    tryb = st.radio("Metoda:", ["📦 Paczka Kurierska", "🚛 Paleta (Jeden typ)", "🏗️ Mix Towarowy"])
    st.divider()
    
    if tryb == "🏗️ Mix Towarowy":
        h_max = st.number_input("Maks. wysokość towaru (mm):", 100, 2500, 2000)
        st.subheader("Lista do zapakowania")
        df_input = st.data_editor(
            [{"Karton": k, "Sztuk": 0} for k in PUDEŁKA_GROPAK.keys()],
            column_config={"Karton": st.column_config.TextColumn(disabled=True), "Sztuk": st.column_config.NumberColumn(min_value=0, step=1)},
            hide_index=True, use_container_width=True
        )
    else:
        wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
        L, W, H = PUDEŁKA_GROPAK[wybrane]["L"], PUDEŁKA_GROPAK[wybrane]["W"], PUDEŁKA_GROPAK[wybrane]["H"]
        if tryb == "📦 Paczka Kurierska":
            kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
            sztuk = st.number_input("Ilość sztuk:", 1, 200, 6)
        else:
            h_max = st.number_input("Maks. wysokość towaru (mm):", 100, 2500, 2000)

# --- 3. WIZUALIZACJA (PANCERNA: ZERO TRÓJKĄTÓW, ZERO SIATKI) ---
def rysuj_layout(bloki, is_pallet=False, title=""):
    fig = go.Figure()
    
    def dodaj_sciane(x, y, z, kolor, sa):
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode='lines', surfaceaxis=sa, surfacecolor=kolor,
            opacity=1, line=dict(width=0), showlegend=False, hoverinfo='skip'
        ))

    def dodaj_krawedzie(x, y, z, l, w, h):
        lx = [x, x+l, x+l, x, x, None, x, x+l, x+l, x, x, None, x, x, None, x, x+l, x+l, None, x+l, x+l, None, x, x]
        ly = [y, y, y+w, y+w, y, None, y, y, y+w, y+w, y, None, y, y, None, y, y, None, y+w, y+w, None, y+w, y+w]
        lz = [z, z, z, z, z, None, z+h, z+h, z+h, z+h, z+h, None, z, z+h, None, z, z+h, None, z, z+h, None, z, z+h]
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=1.5), showlegend=False, hoverinfo='skip'))

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
        x0, y0, z0 = b['pos']
        dl, sz, wy = b['dims']
        kol = b.get('color', KOLOR_KARTONU)
        if 'count' in b:
            for ix in range(b['count'][0]):
                for iy in range(b['count'][1]):
                    for iz in range(b['count'][2]):
                        dodaj_bryle(x0+ix*dl, y0+iy*sz, z0+iz*wy, dl, sz, wy, kol)
        else:
            dodaj_bryle(x0, y0, z0, dl, sz, wy, kol)
    
    hide = dict(showbackground=False, visible=False)
    fig.update_layout(
        scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.6, y=1.6, z=1.3)), xaxis=hide, yaxis=hide, zaxis=hide),
        margin=dict(l=5, r=5, b=5, t=30), paper_bgcolor="white", title=title,
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="#444", width=3))]
    )
    return fig

# --- 4. LOGIKA OBLICZEŃ ---
def get_orientations(L, W, H):
    return list({(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)})

def optymalizuj_palete_maksymalna(L, W, H, h_max):
    PL, PW = 1200, 800
    orient = get_orientations(L, W, H)
    best_total, best_layout = 0, []
    for o1 in orient:
        for o2 in orient:
            for n1 in range(PW // o1[1] + 1):
                rem_y = PW - n1*o1[1]
                n2 = rem_y // o2[1]
                nx1, nx2 = PL // o1[0], PL // o2[0]
                nz1, nz2 = (h_max + TOLERANCJA_H) // o1[2], (h_max + TOLERANCJA_H) // o2[2]
                total = (nx1 * n1 * nz1) + (nx2 * n2 * nz2)
                if total > best_total:
                    best_total = total
                    best_layout = [{'pos': (0, 0, 0), 'dims': o1, 'count': (int(nx1), int(n1), int(nz1))},
                                   {'pos': (0, n1*o1[1], 0), 'dims': o2, 'count': (int(nx2), int(n2), int(nz2))}]
    return best_layout, best_total

# --- NOWY SILNIK MIX: LOGIKA BLOKOWA I WARSTWOWA ---
def optymalizuj_mix_logiczny(items_to_pack, h_max):
    pallets = []
    current_pallet_blocks = []
    
    # Sortowanie: największy rzut poziomy na dół (fundament)
    items_to_pack.sort(key=lambda x: (x['dims'][0]*x['dims'][1]), reverse=True)
    
    curr_z = 0
    while items_to_pack:
        if curr_z >= h_max:
            pallets.append(current_pallet_blocks)
            current_pallet_blocks = []; curr_z = 0
            
        curr_x, curr_y = 0, 0
        layer_h = 0
        
        # Próbujemy wypełnić aktualną warstwę (Z)
        while curr_x < 1200 and items_to_pack:
            # Szukamy towaru, który najlepiej wypełni szerokość palety (800mm)
            best_item_idx = -1
            best_orient = None
            best_rows = 0
            
            for idx, item in enumerate(items_to_pack):
                if item['qty'] <= 0: continue
                # Sprawdzamy wszystkie orientacje dla tego towaru
                orients = get_orientations(*item['dims'])
                for o in orients:
                    if o[0] + curr_x <= 1200 and o[1] <= 800:
                        rows = 800 // o[1]
                        if rows > 0:
                            best_item_idx = idx
                            best_orient = o
                            best_rows = rows
                            break
                if best_item_idx != -1: break
            
            if best_item_idx == -1: # Nic już nie wejdzie w ten pas X
                break
                
            item = items_to_pack[best_item_idx]
            l, w, h = best_orient
            
            # Ile sztuk mieści się w tym bloku (X=l, Y=800, Z=h)
            max_in_x = (1200 - curr_x) // l
            sztuk_na_warstwe_bloku = max_in_x * best_rows
            
            # Ile warstw tego towaru możemy dać w górę w tej sekcji?
            max_layers_z = (h_max + TOLERANCJA_H - curr_z) // h
            if max_layers_z <= 0: # Za wysokie
                items_to_pack.pop(best_item_idx)
                continue
                
            total_possible = sztuk_na_warstwe_bloku * max_layers_z
            to_take = min(item['qty'], total_possible)
            
            # Przeliczamy rzeczywiste wymiary bloku
            actual_layers = (to_take + sztuk_na_warstwe_bloku - 1) // sztuk_na_warstwe_bloku
            
            # Rozmieszczamy w blokach
            taken_count = 0
            for iz in range(int(actual_layers)):
                for ix in range(int(max_in_x)):
                    for iy in range(int(best_rows)):
                        if taken_count < to_take:
                            current_pallet_blocks.append({
                                'pos': (curr_x + ix*l, iy*w, curr_z + iz*h),
                                'dims': (l, w, h),
                                'color': item['color']
                            })
                            taken_count += 1
            
            item['qty'] -= to_take
            if item['qty'] <= 0: items_to_pack.pop(best_item_idx)
            
            curr_x += l # Przesuwamy się wzdłuż palety
            layer_h = max(layer_h, actual_layers * h)

        if layer_h == 0: # Fail-safe
            if items_to_pack: pallets.append(current_pallet_blocks); current_pallet_blocks = []; curr_z = 0
            else: break
        else:
            curr_z += layer_h

    if current_pallet_blocks: pallets.append(current_pallet_blocks)
    return pallets

# --- 5. INTERFEJS GŁÓWNY ---
if tryb == "🏗️ Mix Towarowy":
    to_pack = []
    for i, row in enumerate(df_input):
        if row["Sztuk"] > 0:
            d = PUDEŁKA_GROPAK[row["Karton"]]
            to_pack.append({"dims": (d["L"], d["W"], d["H"]), "qty": int(row["Sztuk"]), "color": MIX_COLORS[i % len(MIX_COLORS)]})
            
    if to_pack:
        # Kopia do obliczeń, żeby nie psuć tabeli wejściowej
        pallets = optymalizuj_mix_logiczny([dict(x) for x in to_pack], h_max)
        st.subheader(f"Wymagana liczba palet: {len(pallets)}")
        for idx, p_blocks in enumerate(pallets):
            c1, c2 = st.columns([1, 2.5])
            with c1: 
                st.info(f"### Paleta {idx+1}")
                st.write(f"Łącznie sztuk: **{len(p_blocks)}**")
                p_h = max([b['pos'][2]+b['dims'][2] for b in p_blocks]) if p_blocks else 0
                st.write(f"Wysokość: **{p_h} mm**")
            with c2: st.plotly_chart(rysuj_layout(p_blocks, is_pallet=True, title=f"Paleta {idx+1}"), use_container_width=True)
    else: st.info("Podaj ilości w tabeli.")

elif tryb == "🚛 Paleta (Jeden typ)":
    layout, total = optymalizuj_palete_maksymalna(L, W, H, h_max)
    c1, c2 = st.columns([1, 2.5])
    with c1:
        st.success(f"Razem: {total} sztuk")
        real_h = max([b['count'][2]*b['dims'][2] for b in layout if b['count'][2] > 0]) if total > 0 else 0
        st.write(f"Wysokość towaru: {real_h} mm")
    with c2: st.plotly_chart(rysuj_layout(layout, is_pallet=True), use_container_width=True)

else: # PACZKA
    def optymalizuj_paczke(n, L, W, H, k_name):
        k = KURIERZY[k_name]; wyniki = []
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
                        if ok: wyniki.append({"conf": (nx, ny, nz), "dims": (rl, rw, rh), "final": (fL, fW, fH), "score": abs(fL-fW)+abs(fW-fH)})
        return sorted(wyniki, key=lambda x: x['score'])[0] if wyniki else None
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']; rl, rw, rh = res['dims']
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.success(f"Razem: {sztuk} sztuk")
            st.write(f"Układ: {nx} x {ny} x {nz}")
            st.info(f"Finał: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2: st.plotly_chart(rysuj_layout([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else: st.error("Nie mieści się!")
