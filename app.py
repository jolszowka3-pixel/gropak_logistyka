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

# --- TWOJA BAZA KARTONÓW ---
PUDEŁKA_GROPAK = {
    "Karton na wiórka (380x380x240)": {"L": 380, "W": 380, "H": 240, "Waga": 0.0},
    "Zbiorczy na papier nacinany (390x390x620)": {"L": 390, "W": 390, "H": 620, "Waga": 0.0},
    "Dyspenser 200ka (210x350x275)": {"L": 210, "W": 350, "H": 275, "Waga": 0.0},
    "A11 (595x250x180)": {"L": 595, "W": 250, "H": 180, "Waga": 0.0},
    "B12 (595x295x230)": {"L": 595, "W": 295, "H": 230, "Waga": 0.0},
    "K20 (485x385x295)": {"L": 485, "W": 385, "H": 295, "Waga": 0.0},
    "L21 (485x430x295)": {"L": 485, "W": 430, "H": 295, "Waga": 0.0},
    "Karton na folię (470x470x500)": {"L": 470, "W": 470, "H": 500, "Waga": 0.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

KOLOR_KARTONU = "#D2A679"

st.set_page_config(page_title="Gropak Master Optymalizator", layout="wide")
st.title("📦 Gropak: Zaawansowany System Paletyzacji i Bundlingu")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Towar")
    wybrane = st.selectbox("Wybierz karton:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (mm)", 10); W = st.number_input("Szer (mm)", 10); H = st.number_input("Wys (mm)", 10); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Tryb Pracy")
    tryb = st.radio("Metoda wysyłki:", ["📦 Paczka Kurierska", "🚛 Paleta EURO (1200x800)"])

    if tryb == "📦 Paczka Kurierska":
        kurier_name = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk:", 1, 100, 6)
    else:
        h_max = st.number_input("Maks. wysokość palety (mm):", 200, 2500, 1600)

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
        # Karton solidny
        fig.add_trace(go.Mesh3d(x=[x0, x0+fL, x0+fL, x0, x0, x0+fL, x0+fL, x0], y=[y0, y0, y0+fW, y0+fW, y0, y0, y0+fW, y0+fW], z=[z0, z0, z0, z0, z0+fH, z0+fH, z0+fH, z0+fH], i=[0,1,2,3,0,4,5,6,7,4,0,1], j=[1,2,3,0,4,5,6,7,4,0,4,5], k=[4,5,6,7,1,2,3,0,5,6,1,2], opacity=1, color=KOLOR_KARTONU))
        # Siatka
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
    
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='L', yaxis_title='W', zaxis_title='H'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- SILNIK PACZKI (BUNDLING) ---
def optymalizuj_paczke(n, L, W, H, k_name):
    k = KURIERZY[k_name]
    wyniki = []
    # Sprawdzamy wszystkie rotacje bazy
    for rl, rw, rh in {(L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)}:
        if rl == 0 or rw == 0 or rh == 0: continue
        for nx in range(1, n + 1):
            for ny in range(1, (n // nx) + 1):
                if n % (nx * ny) == 0:
                    nz = n // (nx * ny)
                    fL, fW, fH = rl*nx, rw*ny, rh*nz
                    ds = sorted([fL, fW, fH], reverse=True)
                    girth = ds[0] + 2*ds[1] + 2*ds[2]
                    if "Paczkomat" in k_name or "Orlen Paczka" in k_name:
                        ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"])
                    else:
                        ok = (ds[0] <= k["max_L"] and girth <= k["max_G"])
                    if ok:
                        stab = abs(fL-fW) + abs(fW-fH) + abs(fL-fH)
                        wyniki.append({"conf": (nx, ny, nz), "dims": (rl, rw, rh), "final": (fL, fW, fH), "score": stab})
    return sorted(wyniki, key=lambda x: x['score'])[0] if wyniki else None

# --- SILNIK PALETY (EKSTREMALNA OPTYMALIZACJA) ---
def optymalizuj_palete_full(L, W, H, h_max):
    PL, PW = 1200, 800
    najlepsza_sztuk = 0
    najlepszy_layout = []
    orientacje = list({(L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)})

    # Testujemy podział gilotynowy z niezależnymi rotacjami w obu sekcjach
    for ol1, ow1, oh1 in orientacje:
        nz1 = h_max // oh1
        if nz1 == 0: continue
        
        for ol2, ow2, oh2 in orientacje:
            nz2 = h_max // oh2
            if nz2 == 0: continue

            # Podział pionowy (wzdłuż 1200)
            for split_x in range(0, PL + 1, 10):
                nxa = split_x // ol1
                nya = PW // ow1
                nxb = (PL - (nxa * ol1)) // ol2
                nyb = PW // ow2
                
                sztuk = (nxa * nya * nz1) + (nxb * nyb * nz2)
                if sztuk > najlepsza_sztuk:
                    najlepsza_sztuk = sztuk
                    najlepszy_layout = [
                        {'pos': (0,0,0), 'dims': (ol1, ow1, oh1), 'count': (int(nxa), int(nya), int(nz1))},
                        {'pos': (nxa*ol1, 0, 0), 'dims': (ol2, ow2, oh2), 'count': (int(nxb), int(nyb), int(nz2))}
                    ]

            # Podział poziomy (wzdłuż 800)
            for split_y in range(0, PW + 1, 10):
                nxa = PL // ol1
                nya = split_y // ow1
                nxb = PL // ol2
                nyb = (PW - (nya * ow1)) // ow2
                
                sztuk = (nxa * nya * nz1) + (nxb * nyb * nz2)
                if sztuk > najlepsza_sztuk:
                    najlepsza_sztuk = sztuk
                    najlepszy_layout = [
                        {'pos': (0,0,0), 'dims': (ol1, ow1, oh1), 'count': (int(nxa), int(nya), int(nz1))},
                        {'pos': (0, nya*ow1, 0), 'dims': (ol2, ow2, oh2), 'count': (int(nxb), int(nyb), int(nz2))}
                    ]
                    
    return najlepszy_layout, najlepsza_sztuk

# --- WIDOK ---
c1, c2 = st.columns([1, 1.5])

if tryb == "📦 Paczka Kurierska":
    res = optymalizuj_paczke(sztuk, L, W, H, kurier_name)
    if res:
        nx, ny, nz = res['conf']
        rl, rw, rh = res['dims']
        with c1:
            st.subheader("🛠️ Instrukcja Bundlingu")
            st.success(f"Optymalne spięcie: **{sztuk} sztuk**")
            st.write(f"- Karton ułożony na boku: **{rl}x{rw} mm**")
            st.write(f"- Układ: **{nx} rz. x {ny} kol. x {nz} warstw**")
            st.divider()
            st.info(f"Finalny gabaryt: {res['final'][0]}x{res['final'][1]}x{res['final'][2]} mm")
        with c2:
            st.plotly_chart(rysuj_layout_3d([{'pos': (0,0,0), 'dims': (rl, rw, rh), 'count': (nx, ny, nz)}]), use_container_width=True)
    else:
        st.error("❌ Przekroczono limity kuriera.")

else: # PALETA
    layout, total = optymalizuj_palete_full(L, W, H, h_max)
    if total > 0:
        with c1:
            st.subheader("📋 Instrukcja Palety")
            st.success(f"Łącznie na palecie: **{total} szt.**")
            st.divider()
            for i, b in enumerate(layout):
                szt_sek = b['count'][0] * b['count'][1] * b['count'][2]
                if szt_sek > 0:
                    st.write(f"**Sekcja {i+1} ({szt_sek} szt.):**")
                    st.write(f"- Ułożenie kartonu: **{b['dims'][0]}x{b['dims'][1]} mm** (H: {b['dims'][2]})")
                    st.write(f"- W rzędzie: {b['count'][0]}, Kolumn: {b['count'][1]}, Warstw: {b['count'][2]}")
        with c2:
            st.plotly_chart(rysuj_layout_3d(layout, is_pallet=True), use_container_width=True)
    else:
        st.error("❌ Karton za duży na paletę.")
