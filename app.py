import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- DANE KURIERÓW ---
KURIERZY = {
    "DPD": {"max_L": 175, "max_G": 300, "max_W": 31.5},
    "DHL": {"max_L": 120, "max_G": 300, "max_W": 31.5},
    "InPost (Gabaryt C)": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25},
    "GLS": {"max_L": 200, "max_G": 300, "max_W": 31.5}
}

# --- DANE TWOICH PUDEŁEK ---
PUDEŁKA_GROPAK = {
    "Karton K1": {"L": 40, "W": 30, "H": 20, "Waga": 2.5},
    "Karton K2": {"L": 60, "W": 40, "H": 30, "Waga": 6.0},
    "Karton K3": {"L": 80, "W": 60, "H": 15, "Waga": 10.0},
    "Własny wymiar...": {"L": 0, "W": 0, "H": 0, "Waga": 0.0}
}

st.set_page_config(page_title="Gropak - Instrukcja Pakowania", layout="wide")
st.title("📦 Instrukcja pakowania przesyłki")

# --- PANEL BOCZNY: TYLKO KONKRETY ---
with st.sidebar:
    st.header("1. Wybierz towar")
    wybrane = st.selectbox("Typ pudełka:", list(PUDEŁKA_GROPAK.keys()))
    
    if wybrane == "Własny wymiar...":
        L = st.number_input("Długość (cm)", 1)
        W = st.number_input("Szerokość (cm)", 1)
        H = st.number_input("Wysokość (cm)", 1)
        Waga = st.number_input("Waga (kg)", 0.1)
    else:
        p = PUDEŁKA_GROPAK[wybrane]
        L, W, H, Waga = p["L"], p["W"], p["H"], p["Waga"]
        st.info(f"Rozmiar: {L}x{W}x{H} | Waga: {Waga}kg")

    st.divider()
    st.header("2. Transport")
    kurier = st.selectbox("Firma kurierska:", list(KURIERZY.keys()))
    sztuk_do_sprawdzenia = st.number_input("Ile sztuk chcesz spiąć?", 1, 50, 4)

# --- LOGIKA SZUKANIA NAJLEPSZEGO UKŁADU ---
def znajdz_uklad(n, L, W, H, Waga, kurier):
    wyniki = []
    lim = KURIERZY[kurier]
    
    for nx in range(1, n + 1):
        for ny in range(1, (n // nx) + 1):
            if n % (nx * ny) == 0:
                nz = n // (nx * ny)
                fL, fW, fH = L*nx, W*ny, H*nz
                dims = sorted([fL, fW, fH], reverse=True)
                girth = dims[0] + 2*dims[1] + 2*dims[2]
                total_w = Waga * n
                
                # Sprawdzanie limitów
                if kurier == "InPost (Gabaryt C)":
                    ok = (fL <= 64 and fW <= 41 and fH <= 38 and total_w <= 25)
                else:
                    ok = (dims[0] <= lim["max_L"] and girth <= lim["max_G"] and total_w <= lim["max_W"])
                
                if ok:
                    wyniki.append({"config": (nx, ny, nz), "dims": (fL, fW, fH), "girth": girth})
    
    # Zwróć najbardziej "zbity" układ (najmniejszy obwód)
    return sorted(wyniki, key=lambda x: x['girth'])[0] if wyniki else None

# --- WYNIK I INSTRUKCJA ---
uklad = znajdz_uklad(sztuk_do_sprawdzenia, L, W, H, Waga, kurier)

if uklad:
    nx, ny, nz = uklad['config']
    fL, fW, fH = uklad['dims']
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("📝 Co zrobić:")
        st.markdown(f"""
        1. Połóż obok siebie **{nx} szt.** (na długość).
        2. Dostaw obok **{ny} rzędy**.
        3. Na górę połóż kolejne **{nz-1} warstwy** (łącznie {nz} w górę).
        
        **Finalna paczka:**
        - Wymiary: **{fL} x {fW} x {fH} cm**
        - Waga: **{Waga * sztuk_do_sprawdzenia:.1f} kg**
        """)
        st.warning(f"⚠️ Pamiętaj o solidnym spięciu taśmą lub folią stretch!")

    with col2:
        # Rysowanie 3D
        fig = go.Figure()
        # Ścianki
        fig.add_trace(go.Mesh3d(
            x=[0, fL, fL, 0, 0, fL, fL, 0],
            y=[0, 0, fW, fW, 0, 0, fW, fW],
            z=[0, 0, 0, 0, fH, fH, fH, fH],
            i=[0, 1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 1],
            j=[1, 2, 3, 0, 4, 5, 6, 7, 4, 0, 4, 5],
            k=[4, 5, 6, 7, 1, 2, 3, 0, 5, 6, 1, 2],
            opacity=0.5, color='#004a99'
        ))
        fig.update_layout(scene=dict(aspectmode='data', xaxis_title='L', yaxis_title='W', zaxis_title='H'), margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error(f"❌ TEGO NIE SPPNIESZ: {sztuk_do_sprawdzenia} sztuk przekracza limity {kurier}!")
    st.info("Spróbuj zmniejszyć liczbę sztuk lub wyślij to jako dwie osobne paczki.")
