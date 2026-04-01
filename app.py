import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURACJA ---
KURIERZY_DATA = {
    "DPD (Standard)": {"max_L": 175, "max_Girth": 300, "max_W": 31.5, "color": "#FF4B4B"},
    "DHL (Standard)": {"max_L": 120, "max_Girth": 300, "max_W": 31.5, "color": "#FFCC00"},
    "InPost Paczkomat C": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25, "color": "#FFD700"},
    "UPS (Standard)": {"max_L": 274, "max_Girth": 400, "max_W": 32.0, "color": "#331100"}
}

STANDARDOWE_KARTONY = {
    "Karton K1 (Mały)": {"L": 40, "W": 30, "H": 20, "weight": 3.0},
    "Karton K2 (Średni)": {"L": 60, "W": 40, "H": 40, "weight": 8.0},
    "Karton K3 (Płaski)": {"L": 80, "W": 60, "H": 15, "weight": 10.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "weight": 0.0}
}

st.set_page_config(page_title="Gropak - Optymalizator Blokowy", layout="wide")
st.title("📦 Gropak: Zaawansowany Optymalizator Blokowy")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ustawienia")
    wybrany_kurier = st.selectbox("Przewoźnik:", list(KURIERZY_DATA.keys()))
    k_limits = KURIERZY_DATA[wybrany_kurier]
    
    wybrany_karton = st.selectbox("Wybierz karton:", list(STANDARDOWE_KARTONY.keys()))
    dv = STANDARDOWE_KARTONY[wybrany_karton]
    
    L = st.number_input("Długość (cm)", value=int(dv["L"]) if dv["L"]>0 else 60)
    W = st.number_input("Szerokość (cm)", value=int(dv["W"]) if dv["W"]>0 else 40)
    H = st.number_input("Wysokość (cm)", value=int(dv["H"]) if dv["H"]>0 else 20)
    weight = st.number_input("Waga 1szt (kg)", value=float(dv["weight"]) if dv["weight"]>0 else 5.0)
    
    st.divider()
    max_sztuk = st.slider("Max sztuk w paczce:", 1, 24, 8)

# --- FUNKCJA RYSOWANIA GRUPY (BLOKU) ---
def rysuj_blok(orig_dims, nx, ny, nz, color):
    L_f, W_f, H_f = orig_dims[0]*nx, orig_dims[1]*ny, orig_dims[2]*nz
    fig = go.Figure()

    # Główna bryła
    v = np.array([[0,0,0], [L_f,0,0], [L_f,W_f,0], [0,W_f,0], [0,0,H_f], [L_f,0,H_f], [L_f,W_f,H_f], [0,W_f,H_f]])
    i, j, k = [0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], [1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], [4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2]
    fig.add_trace(go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=i, j=j, k=k, opacity=0.3, color=color))

    # Linie siatki (podziały między kartonami)
    lines_x, lines_y, lines_z = [], [], []
    # Linie wzdłuż X
    for x in range(nx + 1):
        curr_x = x * orig_dims[0]
        for y in [0, W_f]:
            lines_x.extend([curr_x, curr_x]); lines_y.extend([y, y]); lines_z.extend([0, H_f]); lines_x.append(None); lines_y.append(None); lines_z.append(None)
        for z in [0, H_f]:
            lines_x.extend([curr_x, curr_x]); lines_y.extend([0, W_f]); lines_z.extend([z, z]); lines_x.append(None); lines_y.append(None); lines_z.append(None)
    # Linie wzdłuż Y
    for y in range(ny + 1):
        curr_y = y * orig_dims[1]
        for x in [0, L_f]:
            lines_x.extend([x, x]); lines_y.extend([curr_y, curr_y]); lines_z.extend([0, H_f]); lines_x.append(None); lines_y.append(None); lines_z.append(None)
    # Linie wzdłuż Z
    for z in range(nz + 1):
        curr_z = z * orig_dims[2]
        for x in [0, L_f]:
            lines_x.extend([x, x]); lines_y.extend([0, W_f]); lines_z.extend([curr_z, curr_z]); lines_x.append(None); lines_y.append(None); lines_z.append(None)

    fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='#333', width=3)))
    fig.update_layout(scene=dict(xaxis_title='L', yaxis_title='W', zaxis_title='H', aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- LOGIKA SZUKANIA NAJLEPSZEGO BLOKU ---
results = []
for n in range(1, max_sztuk + 1):
    # Szukamy dzielników liczby n, aby stworzyć prostopadłościan nx * ny * nz = n
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                
                final_L, final_W, final_H = L*nx, W*ny, H*nz
                dims_sorted = sorted([final_L, final_W, final_H], reverse=True)
                l_max = dims_sorted[0]
                girth = l_max + 2*dims_sorted[1] + 2*dims_sorted[2]
                total_w = weight * n
                
                # Walidacja
                is_ok = False
                if wybrany_kurier == "InPost Paczkomat C":
                    if final_L <= 64 and final_W <= 41 and final_H <= 38 and total_w <= 25: is_ok = True
                else:
                    if l_max <= k_limits["max_L"] and girth <= k_limits["max_Girth"] and total_w <= k_limits["max_W"]: is_ok = True
                
                if is_ok:
                    results.append({"sztuk": n, "config": (nx, ny, nz), "dims": (final_L, final_W, final_H), "girth": girth, "waga": total_w})

# --- WYŚWIETLANIE ---
col1, col2 = st.columns([1, 2])

with col1:
    if results:
        # Sortujemy: najpierw po ilości sztuk (desc), potem po najmniejszym obwodzie (asc)
        best = sorted(results, key=lambda x: (x['sztuk'], -x['girth']), reverse=True)[0]
        nx, ny, nz = best['config']
        
        st.success(f"🚀 Najlepszy układ: **{best['sztuk']} szt.**")
        st.metric("Konfiguracja (Szer x Głęb x Wys)", f"{nx} x {ny} x {nz}")
        st.write(f"📏 Wymiary: **{best['dims'][0]} x {best['dims'][1]} x {best['dims'][2]} cm**")
        st.write(f"⚖️ Waga: **{best['waga']} kg**")
        st.write(f"🔄 Obwód: **{int(best['girth'])} cm**")
        
        st.divider()
        st.info("💡 **Instrukcja dla magazynu:**")
        st.write(f"1. Ułóż podstawę: **{nx}** szt. obok siebie i **{ny}** szt. w głąb.")
        st.write(f"2. Zrób taką samą drugą warstwę (łącznie **{nz}** warstw w górę).")
    else:
        st.error("Nie da się spiąć nawet 1 sztuki w tych limitach.")

with col2:
    if results:
        fig = rysuj_blok((L, W, H), nx, ny, nz, k_limits['color'])
        st.plotly_chart(fig, use_container_width=True)

with st.expander("Wszystkie możliwe układy dla tej ilości sztuk"):
    if results:
        st.write(results)
