import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURACJA KURIERÓW ---
KURIERZY = {
    "DPD (Standard)": {"max_L": 175, "max_G": 300, "max_W": 31.5, "color": "#dc0032"},
    "DHL (Standard)": {"max_L": 120, "max_G": 300, "max_W": 31.5, "color": "#ffcc00"},
    "InPost Paczkomat C": {"L": 64, "W": 38, "H": 41, "max_W": 25.0, "color": "#ffcc00"},
    "InPost Kurier": {"max_L": 120, "max_G": 220, "max_W": 30.0, "color": "#ffcc00"},
    "GLS (Polska)": {"max_L": 200, "max_G": 300, "max_W": 31.5, "color": "#003399"},
    "UPS Standard": {"max_L": 274, "max_G": 400, "max_W": 32.0, "color": "#351c15"},
    "FedEx Polska": {"max_L": 175, "max_G": 330, "max_W": 35.0, "color": "#4d148c"},
    "Pocztex": {"max_L": 150, "max_G": 300, "max_W": 30.0, "color": "#ee1d23"},
    "TNT (Express)": {"max_L": 240, "max_G": 400, "max_W": 30.0, "color": "#ff6600"}
}

PUDEŁKA_GROPAK = {
    "Karton K1 (40x30x20)": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2 (60x40x30)": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3 (80x60x15)": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Karton Fasonowy (35x25x10)": {"L": 35, "W": 25, "H": 10, "Waga": 1.2},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Optymalizator", layout="wide")
st.title("📦 Gropak: System Pakowania (Paczki i Palety)")

with st.sidebar:
    st.header("1. Wybór towaru")
    wybrane = st.selectbox("Typ pudełka:", list(PUDEŁKA_GROPAK.keys()))
    if wybrane == "Własny wymiar...":
        L = st.number_input("Dł (cm)", 1); W = st.number_input("Szer (cm)", 1)
        H = st.number_input("Wys (cm)", 1); Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]; L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
    
    st.divider()
    st.header("2. Sposób wysyłki")
    tryb = st.radio("Wybierz tryb:", ["Paczka Kurierska", "Paleta EURO (120x80)"])

    if tryb == "Paczka Kurierska":
        kurier_name = st.selectbox("Kurier:", list(KURIERZY.keys()))
        sztuk = st.number_input("Ilość sztuk do spięcia:", 1, 100, 4)
    else:
        h_max = st.number_input("Docelowa wysokość palety (cm):", 50, 250, 160)
        st.info("Wymiary palety: 120 x 80 cm")

# --- FUNKCJA WIZUALIZACJI ---
def rysuj_blok_3d(orig_dims, nx, ny, nz, color, is_pallet=False):
    l, w, h = orig_dims
    fL, fW, fH = l*nx, w*ny, h*nz
    fig = go.Figure()

    # Jeśli paleta, dorysowujemy podstawę palety
    if is_pallet:
        fig.add_trace(go.Mesh3d(
            x=[0, 120, 120, 0, 0, 120, 120, 0], y=[0, 0, 80, 80, 0, 0, 80, 80], z=[-15, -15, -15, -15, 0, 0, 0, 0],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            opacity=1, color="#8B4513"
        ))

    # Mesh3d dla kartonów
    fig.add_trace(go.Mesh3d(
        x=[0, fL, fL, 0, 0, fL, fL, 0], y=[0, 0, fW, fW, 0, 0, fW, fW], z=[0, 0, 0, 0, fH, fH, fH, fH],
        i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
        opacity=0.25, color=color
    ))

    # Linie siatki kartonów
    lines_x, lines_y, lines_z = [], [], []
    for i in range(nx + 1):
        for j in range(ny + 1):
            lines_x.extend([i*l, i*l, None]); lines_y.extend([j*w, j*w, None]); lines_z.extend([0, fH, None])
    for i in range(nx + 1):
        for k in range(nz + 1):
            lines_x.extend([i*l, i*l, None]); lines_y.extend([0, fW, None]); lines_z.extend([k*h, k*h, None])
    for j in range(ny + 1):
        for k in range(nz + 1):
            lines_x.extend([0, fL, None]); lines_y.extend([j*w, j*w, None]); lines_z.extend([k*h, k*h, None])

    fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='#000', width=4)))
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='Dł', yaxis_title='Szer', zaxis_title='Wys'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- LOGIKA PACZKI ---
def szukaj_paczki(n, L, W, H, w_jedn, k_name):
    mozliwe = []
    k = KURIERZY[k_name]
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                fL, fW, fH = L*nx, W*ny, H*nz
                ds = sorted([fL, fW, fH], reverse=True)
                girth = ds[0] + 2*ds[1] + 2*ds[2]
                if "Paczkomat" in k_name:
                    ok = (fL <= k["L"] and fW <= k["W"] and fH <= k["H"] and w_jedn*n <= k["max_W"])
                else:
                    ok = (ds[0] <= k["max_L"] and girth <= k["max_G"] and w_jedn*n <= k["max_W"])
                if ok:
                    mozliwe.append({"conf": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth, "stab": abs(nx-ny)+abs(ny-nz)})
    return sorted(mozliwe, key=lambda x: x['stab'])[0] if mozliwe else None

# --- LOGIKA PALETY ---
def szukaj_palety(L, W, H, h_max):
    # Sprawdzamy wszystkie orientacje pudełka (na którym boku leży)
    orientacje = [(L,W,H), (L,H,W), (W,L,H), (W,H,L), (H,L,W), (H,W,L)]
    wyniki = []
    
    for ol, ow, oh in orientacje:
        # Ile sztuk na warstwie 120x80
        nx = 120 // ol
        ny = 80 // ow
        if nx > 0 and ny > 0:
            sztuk_warstwa = nx * ny
            ile_warstw = h_max // oh
            total = sztuk_warstwa * ile_warstw
            # Obliczamy wolną przestrzeń (im mniej tym lepiej)
            wolne = (120 * 80) - (f"{nx*ol}" * f"{ny*ow}") # uproszczone
            wyniki.append({"conf": (int(nx), int(ny), int(ile_warstw)), "dims": (ol, ow, oh), "total": int(total)})
            
    return sorted(wyniki, key=lambda x: x['total'], reverse=True)[0] if wyniki else None

# --- WYSWIETLANIE ---
if tryb == "Paczka Kurierska":
    res = szukaj_paczki(sztuk, L, W, H, Waga, kurier_name)
    if res:
        nx, ny, nz = res['conf']
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.subheader("🛠️ Instrukcja Paczki")
            st.write(f"Układ: **{nx} x {ny} x {nz}**")
            st.write(f"Wymiary: {res['dims'][0]}x{res['dims'][1]}x{res['dims'][2]} cm")
            st.write(f"Waga: {Waga*sztuk:.1f} kg")
        with c2:
            st.plotly_chart(rysuj_blok_3d((L, W, H), nx, ny, nz, KURIERZY[kurier_name]['color']), use_container_width=True)
    else:
        st.error("❌ Przekroczono limity kuriera!")

else:
    res = szukaj_palety(L, W, H, h_max)
    if res:
        nx, ny, nz = res['conf']
        ol, ow, oh = res['dims']
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.subheader("🛠️ Instrukcja Palety")
            st.success(f"Razem na palecie: **{res['total']} sztuk**")
            st.write(f"1. Połóż karton na boku: **{ol} x {ow} cm** (wysokość kartonu: {oh} cm)")
            st.write(f"2. Na jednej warstwie ułóż: **{nx}** (dł) x **{ny}** (szer) = **{nx*ny} szt.**")
            st.write(f"3. Ułóż **{nz} warstw** w górę.")
            st.divider()
            st.write(f"Wysokość ładunku: {nz * oh} cm")
            st.write(f"Waga towaru: {res['total'] * Waga:.1f} kg")
        with c2:
            st.plotly_chart(rysuj_blok_3d((ol, ow, oh), nx, ny, nz, "#2ca02c", is_pallet=True), use_container_width=True)
    else:
        st.error("❌ Karton jest za duży, aby zmieścić się na palecie lub przekracza wysokość!")
