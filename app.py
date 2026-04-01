import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- BAZA WIEDZY: STANDARDOWE GABARYTY ---
KURIERZY_DATA = {
    "DPD (Standard)": {"max_L": 175, "max_Girth": 300, "max_W": 31.5, "color": "#FF4B4B"},
    "DHL (Standard)": {"max_L": 120, "max_Girth": 300, "max_W": 31.5, "color": "#FFCC00"},
    "InPost Paczkomat C": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25, "color": "#FFD700"},
    "UPS (Standard)": {"max_L": 274, "max_Girth": 400, "max_W": 32.0, "color": "#331100"},
    "GLS (Standard)": {"max_L": 200, "max_Girth": 300, "max_W": 31.5, "color": "#003399"}
}

STANDARDOWE_KARTONY = {
    "Karton K1 (Mały)": {"L": 40, "W": 30, "H": 20, "weight": 3.0},
    "Karton K2 (Średni)": {"L": 60, "W": 40, "H": 40, "weight": 8.0},
    "Karton K3 (Duży/Płaski)": {"L": 80, "W": 60, "H": 15, "weight": 12.0},
    "Karton Fasonowy F1": {"L": 35, "W": 25, "H": 10, "weight": 1.5},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "weight": 0.0}
}

st.set_page_config(page_title="Gropak - Optymalizator", layout="wide", page_icon="📦")
st.title("📦 Gropak: Optymalizacja Wysyłek Kurierskich")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    # Wybór Kuriera
    wybrany_kurier = st.selectbox("Wybierz przewoźnika:", list(KURIERZY_DATA.keys()))
    k_limits = KURIERZY_DATA[wybrany_kurier]
    
    st.divider()
    
    # Wybór Kartonu
    wybrany_karton = st.selectbox("Wybierz standardowy karton:", list(STANDARDOWE_KARTONY.keys()))
    
    # Logika autouzupełniania
    default_vals = STANDARDOWE_KARTONY[wybrany_karton]
    
    st.subheader("Wymiary jednostkowe")
    L = st.number_input("Długość (cm)", value=default_vals["L"] if default_vals["L"] > 0 else 60)
    W = st.number_input("Szerokość (cm)", value=default_vals["W"] if default_vals["W"] > 0 else 40)
    H = st.number_input("Wysokość (cm)", value=default_vals["H"] if default_vals["H"] > 0 else 20)
    weight = st.number_input("Waga (kg)", value=default_vals["weight"] if default_vals["weight"] > 0 else 5.0)
    
    st.divider()
    max_sztuk = st.slider("Maksymalnie połącz razem:", 1, 15, 6)

# --- LOGIKA OBLICZENIOWA (WIZUALIZACJA) ---
def rysuj_paczke(orig_dims, n_sztuk, axis_index, label, color):
    final_dims = list(orig_dims)
    final_dims[axis_index] *= n_sztuk
    L_f, W_f, H_f = final_dims

    fig = go.Figure()

    # Bryła
    v = np.array([[0,0,0], [L_f,0,0], [L_f,W_f,0], [0,W_f,0], [0,0,H_f], [L_f,0,H_f], [L_f,W_f,H_f], [0,W_f,H_f]])
    i, j, k = [0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1], [1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5], [4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2]

    fig.add_trace(go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=i, j=j, k=k, opacity=0.3, color=color, showscale=False))

    # Linie podziału między kartonami
    lines_x, lines_y, lines_z = [], [], []
    for s in range(1, n_sztuk):
        shift = s * orig_dims[axis_index]
        if axis_index == 0: temp_v = [[shift,0,0], [shift,W_f,0], [shift,W_f,H_f], [shift,0,H_f], [shift,0,0]]
        elif axis_index == 1: temp_v = [[0,shift,0], [L_f,shift,0], [L_f,shift,H_f], [0,shift,H_f], [0,shift,0]]
        else: temp_v = [[0,0,shift], [L_f,0,shift], [L_f,W_f,shift], [0,W_f,shift], [0,0,shift]]
        lines_x.extend([p[0] for p in temp_v]); lines_x.append(None)
        lines_y.extend([p[1] for p in temp_v]); lines_y.append(None)
        lines_z.extend([p[2] for p in temp_v]); lines_z.append(None)

    fig.add_trace(go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color='#222', width=4)))

    fig.update_layout(
        scene=dict(xaxis_title='Dł (cm)', yaxis_title='Szer (cm)', zaxis_title='Wys (cm)', aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=30), showlegend=False
    )
    return fig

# --- ANALIZA LIMITÓW ---
def check_limits(d1, d2, d3, w_total, courier_name):
    dims = sorted([d1, d2, d3], reverse=True)
    l_max = dims[0]
    girth = l_max + 2*dims[1] + 2*dims[2]
    lim = KURIERZY_DATA[courier_name]
    
    if courier_name == "InPost Paczkomat C":
        return (d1 <= 64 and d2 <= 41 and d3 <= 38 and w_total <= 25), girth
    
    return (l_max <= lim["max_L"] and girth <= lim["max_Girth"] and w_total <= lim["max_W"]), girth

# --- WYNIKI ---
results = []
orig_dims = (L, W, H)

for n in range(1, max_sztuk + 1):
    opts = [(L*n, W, H, 0, f"Spięte wzdłuż ({n}xL)"), (L, W*n, H, 1, f"Spięte obok siebie ({n}xW)"), (L, W, H*n, 2, f"Spięte w pionie ({n}xH)")]
    for nl, nw, nh, axis, lbl in opts:
        ok, g = check_limits(nl, nw, nh, weight*n, wybrany_kurier)
        if ok:
            results.append({"Sztuk": n, "Układ": lbl, "Wymiary": (nl, nw, nh), "Obwód": g, "Waga": weight*n, "axis": axis})

col1, col2 = st.columns([1, 2
