import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- KONFIGURACJA ---
KURIERZY = {
    "DPD / DHL Standard": {"max_L": 175, "max_Girth": 300, "max_W": 31.5, "kolor": "#FF4B4B"},
    "InPost Paczkomat C": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25, "kolor": "#FFD700"}
}

st.set_page_config(page_title="Gropak Wizualizator", layout="wide", page_icon="📦")
st.title("📦 Gropak: Optymalizator i Wizualizacja Paczek")

# --- SIDEBAR: WEJŚCIE DANYCH ---
with st.sidebar:
    st.header("1. Parametry bazowego kartonu")
    orig_L = st.number_input("Długość (cm)", value=60, min_value=1)
    orig_W = st.number_input("Szerokość (cm)", value=40, min_value=1)
    orig_H = st.number_input("Wysokość (cm)", value=20, min_value=1)
    weight = st.number_input("Waga 1 szt. (kg)", value=5.0, min_value=0.1)
    st.divider()
    st.header("2. Opcje łączenia")
    max_sztuk = st.slider("Maksymalnie spiąć razem:", 1, 12, 4)
    wybrany_kurier = st.selectbox("Przewoźnik:", list(KURIERZY.keys()))

# --- FUNKCJA RYSOWANIA 3D (Plotly) ---
def rysuj_paczke(orig_dims, n_sztuk, axis_index, label):
    # orig_dims: (L, W, H)
    # axis_index: 0=L, 1=W, 2=H (wzdłuż której osi łączymy)
    
    # Obliczamy wymiary finalnej bryły
    final_dims = list(orig_dims)
    final_dims[axis_index] *= n_sztuk
    L_f, W_f, H_f = final_dims

    fig = go.Figure()

    # 1. Rysujemy finalny obrys (półprzezroczysty)
    # Definicja wierzchołków prostopadłościanu
    v = np.array([
        [0,0,0], [L_f,0,0], [L_f,W_f,0], [0,W_f,0], # dół
        [0,0,H_f], [L_f,0,H_f], [L_f,W_f,H_f], [0,W_f,H_f] # góra
    ])
    # Definicja ścian (trójkąty dla Plotly Mesh3d)
    i = [0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1]
    j = [1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5]
    k = [4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2]

    # Kolor obrysu zależny od kuriera
    color_main = KURIERZY[wybrany_kurier]["kolor"]

    # Główna bryła
    fig.add_trace(go.Mesh3d(
        x=v[:,0], y=v[:,1], z=v[:,2], i=i, j=j, k=k,
        opacity=0.2, color=color_main, name='Finalna Paczka', showscale=False
    ))

    # 2. Rysujemy linie podziału (pokazujemy poszczególne kartony)
    lines_x, lines_y, lines_z = [], [], []
    
    for s in range(1, n_sztuk):
        shift = s * orig_dims[axis_index]
        
        # Płaszczyzny cięcia w zależności od osi łączenia
        if axis_index == 0: # Cięcie wzdłuż L (płaszczyzny YZ)
            temp_v = np.array([[shift,0,0], [shift,W_f,0], [shift,W_f,H_f], [shift,0,H_f], [shift,0,0]])
        elif axis_index == 1: # Cięcie wzdłuż W (płaszczyzny XZ)
            temp_v = np.array([[0,shift,0], [L_f,shift,0], [L_f,shift,H_f], [0,shift,H_f], [0,shift,0]])
        else: # Cięcie wzdłuż H (płaszczyzny XY)
            temp_v = np.array([[0,0,shift], [L_f,0,shift], [L_f,W_f,shift], [0,W_f,shift], [0,0,shift]])
            
        lines_x.extend(temp_v[:,0]); lines_x.append(None)
        lines_y.extend(temp_v[:,1]); lines_y.append(None)
        lines_z.extend(temp_v[:,2]); lines_z.append(None)

    # Dodajemy linie siatki wewnętrznej
    fig.add_trace(go.Scatter3d(
        x=lines_x, y=lines_y, z=lines_z,
        mode='lines', line=dict(color='#444', width=3), name='Podział'
    ))
    
    # 3. Rysujemy krawędzie zewnętrzne (kontur)
    current_L, current_W, current_H = L_f, W_f, H_f
    contour_v = np.array([
        [0,0,0], [current_L,0,0], [current_L,current_W,0], [0,current_W,0], [0,0,0], # dół
        [0,0,current_H], [current_L,0,current_H], [current_L,current_W,current_H], [0,current_W,current_H], [0,0,current_H], # góra
        [0,0,0], [0,0,current_H], [None,None,None],
        [current_L,0,0], [current_L,0,current_H], [None,None,None],
        [current_L,current_W,0], [current_L,current_W,current_H], [None,None,None],
        [0,current_W,0], [0,current_W,current_H]
    ])
    fig.add_trace(go.Scatter3d(
        x=contour_v[:,0], y=contour_v[:,1], z=contour_v[:,2],
        mode='lines', line=dict(color='black', width=5), name='Kontur'
    ))

    # Ustawienia sceny (kamery, osi)
    fig.update_layout(
        title=f"Schemat: {label} ({L_f}x{W_f}x{H_f} cm)",
        scene=dict(
            xaxis=dict(title='L (cm)', range=[0, max(final_dims)+10]),
            yaxis=dict(title='W (cm)', range=[0, max(final_dims)+10]),
            zaxis=dict(title='H (cm)', range=[0, max(final_dims)+10]),
            aspectmode='data' # Ważne: zachowuje proporcje 1:1:1
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False
    )
    return fig

# --- LOGIKA KONTROLI LIMITÓW ---
def check_limits(dim1, dim2, dim3, total_w, courier_name):
    dims = sorted([dim1, dim2, dim3], reverse=True)
    l_max = dims[0]
    girth = l_max + 2*dims[1] + 2*dims[2]
    
    limits = KURIERZY[courier_name]
    
    if courier_name == "DPD / DHL Standard":
        if l_max <= limits["max_L"] and girth <= limits["max_Girth"] and total_w <= limits["max_W"]:
            return True, girth
    return False, girth

# --- GŁÓWNA ANALIZA ---
col_input, col_viz = st.columns([1, 2]) # Podział ekranu: Lewo dane, Prawo grafika

results = []
orig_dims = (orig_L, orig_W, orig_H)

# Pętla obliczeniowa
for n in range(1, max_sztuk + 1):
    orientations = [
        (orig_L*n, orig_W, orig_H, 0, f"Spięte wzdłuż (os L) - {n} szt."),
        (orig_L, orig_W*n, orig_H, 1, f"Spięte obok siebie (os W) - {n} szt."),
        (orig_L, orig_W, orig_H*n, 2, f"Spięte w pionie (os H) - {n} szt.")
    ]
    
    for new_l, new_w, new_h, axis_index, label in orientations:
        can_send, g = check_limits(new_l, new_w, new_h, weight*n, wybrany_kurier)
        if can_send:
            results.append({
                "Sztuk": n,
                "Układ": label,
                "Wymiary": (new_l, new_w, new_h),
                "Obwód": g,
                "Waga": weight*n,
                "axis_index": axis_index
            })

# --- PREZENTACJA WYNIKÓW ---
with col_viz:
    if results:
        # Najlepsza opcja (najwięcej sztuk)
        best = sorted(results, key=lambda x: x['Sztuk'], reverse=True)[0]
        
        st.success(f"✅ Najlepsza opcja dla {wybrany_kurier}: Wyślij **{best['Sztuk']} szt.** w jednej paczce!")
        
        # Generujemy i wyświetlamy wykres 3D
        fig_3d = rysuj_paczke(orig_dims, best['Sztuk'], best['axis_index'], best['Układ'])
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Detale pod wykresem
        st.info(f"👉 Instrukcja: **{best['Układ']}**. Finalna waga: {best['Waga']} kg.")

    else:
        st.error(f"❌ Nawet pojedynczy karton przekracza limity standardowej paczki u kuriera {wybrany_kurier}!")

# Tabela na dole
with st.expander("Zobacz wszystkie poprawne warianty łączenia"):
    if results:
        st.table(results)
    else:
        st.write("Brak wariantów.")
