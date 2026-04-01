import streamlit as st

# Słownik kurierów z ich limitami
KURIERZY = {
    "DPD / DHL Standard": {"max_L": 175, "max_Girth": 300, "max_W": 31.5},
    "InPost Paczkomat C": {"max_L": 64, "max_W": 41, "max_H": 38, "max_Weight": 25}
}

st.set_page_config(page_title="Gropak - Łącznik Paczek", layout="wide")
st.title("📦 Gropak: Optymalizator Paczek Kurierskich")

# --- WEJŚCIE DANYCH ---
with st.sidebar:
    st.header("Parametry kartonu")
    L = st.number_input("Długość (cm)", value=60)
    W = st.number_input("Szerokość (cm)", value=40)
    H = st.number_input("Wysokość (cm)", value=20)
    weight = st.number_input("Waga 1 szt. (kg)", value=5.0)
    st.divider()
    max_sztuk = st.slider("Ile sztuk sprawdzić do połączenia?", 1, 10, 2)

# --- LOGIKA OBLICZENIOWA ---
def check_limits(dim1, dim2, dim3, total_w, courier_name):
    dims = sorted([dim1, dim2, dim3], reverse=True)
    l_max = dims[0]
    girth = l_max + 2*dims[1] + 2*dims[2]
    
    limits = KURIERZY[courier_name]
    
    if courier_name == "DPD / DHL Standard":
        if l_max <= limits["max_L"] and girth <= limits["max_Girth"] and total_w <= limits["max_W"]:
            return True, girth
    return False, girth

# --- ANALIZA ---
st.subheader(f"Analiza łączenia dla kartonu: {L}x{W}x{H} cm ({weight}kg)")

results = []

# Sprawdzamy opcje łączenia (np. 1 sztuka, 2 sztuki spięte w pionie, 2 w poziomie itd.)
for n in range(1, max_sztuk + 1):
    # Możliwe nowe wymiary po złączeniu n sztuk w różnych osiach
    orientations = [
        (L*n, W, H, f"Spięte wzdłuż ({n}xL)"),
        (L, W*n, H, f"Spięte obok siebie ({n}xW)"),
        (L, W, H*n, f"Spięte w pionie ({n}xH)")
    ]
    
    for new_l, new_w, new_h, label in orientations:
        can_send, g = check_limits(new_l, new_w, new_h, weight*n, "DPD / DHL Standard")
        if can_send:
            results.append({
                "Sztuk": n,
                "Układ": label,
                "Wymiary": f"{new_l}x{new_w}x{new_h}",
                "Obwód (Girth)": g,
                "Waga": weight*n
            })

# --- WIZUALIZACJA I WYNIK ---
if results:
    # Sortujemy, żeby pokazać opcję z największą liczbą sztuk na górze
    best_option = sorted(results, key=lambda x: x['Sztuk'], reverse=True)[0]
    
    st.success(f"✅ Najlepsza opcja: Możesz wysłać **{best_option['Sztuk']} szt.** w jednej paczce!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Instrukcja dla magazynu:")
        st.info(f"👉 **{best_option['Układ']}**")
        st.write(f"Wymiary finalne: **{best_option['Wymiary']} cm**")
        st.write(f"Waga finalna: **{best_option['Waga']} kg**")
    
    with col2:
        st.table(results) # Tabela wszystkich pasujących wariantów
else:
    st.error("❌ Nawet pojedynczy karton przekracza limity standardowej paczki!")
