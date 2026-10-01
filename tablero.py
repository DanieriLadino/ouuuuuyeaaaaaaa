import random
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Mi Tablero Mágico", page_icon="🖍️", layout="wide")

# ---------- Estilos infantiles ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, label, p, span, div {
        font-family: 'Baloo 2', 'Comic Sans MS', cursive !important;
    }

    /* Fondo de la página: cielo con puntitos de colores */
    .stApp {
        background-color: #FFF6D6;
        background-image:
            radial-gradient(#FF8FAB 2.5px, transparent 2.5px),
            radial-gradient(#7BDFF2 2.5px, transparent 2.5px);
        background-size: 46px 46px;
        background-position: 0 0, 23px 23px;
    }

    /* Título arcoíris con letras que saltan */
    .titulo {
        text-align: center;
        font-size: 3.4rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0.2rem 0 0.4rem 0;
    }
    .titulo span {
        display: inline-block;
        text-shadow: 3px 3px 0 #ffffff, 5px 5px 0 rgba(0,0,0,0.12);
        animation: saltito 1.6s ease-in-out infinite;
    }
    @keyframes saltito {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    @media (prefers-reduced-motion: reduce) {
        .titulo span { animation: none; }
    }

    .subtitulo {
        text-align: center;
        font-size: 1.3rem;
        color: #5A4FCF;
        margin-bottom: 1rem;
    }

    /* Tarjeta del reto */
    .reto {
        background: #ffffff;
        border: 5px solid #FFB703;
        border-radius: 30px;
        padding: 0.6rem 1rem;
        text-align: center;
        box-shadow: 6px 6px 0 #FB8500;
    }
    .reto .texto { font-size: 1.3rem; color: #3D348B; }
    .reto .numero {
        font-size: 6rem;
        font-weight: 800;
        line-height: 1;
        color: #F15BB5;
        text-shadow: 4px 4px 0 #FEE440;
    }

    /* El tablero: marco tipo crayón */
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border: 8px dashed #00BBF9 !important;
        border-radius: 28px;
        box-shadow: 8px 8px 0 #9B5DE5;
        background: #fff;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #CDB4DB 0%, #FFC8DD 50%, #BDE0FE 100%);
        border-right: 6px solid #ffffff;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #3D348B;
    }

    /* Botones gorditos */
    .stButton > button {
        background: #06D6A0;
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
        border: 4px solid #ffffff;
        border-radius: 999px;
        padding: 0.4rem 1.4rem;
        box-shadow: 4px 4px 0 #118AB2;
        transition: transform 0.1s;
    }
    .stButton > button:hover { transform: scale(1.06); color: white; border-color: #fff; }
    .stButton > button:active { transform: scale(0.96); }
    .stButton > button:focus-visible { outline: 4px solid #FFB703; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Título ----------
letras = "Mi Tablero Mágico"
colores = ["#F15BB5", "#FB8500", "#FFB703", "#06D6A0", "#00BBF9", "#9B5DE5"]
titulo_html = "".join(
    f'<span style="color:{colores[i % len(colores)]}; animation-delay:{i * 0.08:.2f}s">'
    f'{"&nbsp;" if c == " " else c}</span>'
    for i, c in enumerate(letras)
)
st.markdown(f'<div class="titulo">🖍️ {titulo_html} 🌈</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">¡Escribe un número con tu dedo o con el ratón!</div>',
            unsafe_allow_html=True)

# ---------- Barra lateral ----------
COLORES_CRAYON = {
    "🍓 Fresa": "#F15BB5",
    "🍊 Naranja": "#FB8500",
    "🌞 Sol": "#FFB703",
    "🐸 Rana": "#06D6A0",
    "🐳 Ballena": "#00BBF9",
    "🍇 Uva": "#9B5DE5",
    "🐻 Oso": "#6D4C41",
}

FONDOS = {
    "☁️ Nube blanca": "#FFFFFF",
    "🍦 Vainilla": "#FFF8E1",
    "🌸 Rosita": "#FFE5EC",
    "💧 Cielo": "#E0F7FF",
    "🌙 Noche": "#2B2D42",
}

HERRAMIENTAS = {
    "✏️ Lápiz mágico": "freedraw",
    "📏 Línea": "line",
    "🟦 Cuadrado": "rect",
    "🟣 Círculo": "circle",
    "✋ Mover": "transform",
}

with st.sidebar:
    st.header("🎨 Mis colores")
    color_nombre = st.radio("Elige tu crayón:", list(COLORES_CRAYON.keys()), index=0)
    stroke_color = COLORES_CRAYON[color_nombre]

    with st.expander("🌈 Quiero otro color"):
        if st.checkbox("Usar mi propio color"):
            stroke_color = st.color_picker("Color especial", stroke_color)

    st.header("✨ Grosor")
    grosores = {"🐜 Fino": 8, "🐱 Mediano": 18, "🐘 Gordote": 30}
    grosor_nombre = st.radio("¿Qué tan gordo?", list(grosores.keys()), index=1, horizontal=True)
    stroke_width = grosores[grosor_nombre]

    st.header("🖼️ Fondo")
    fondo_nombre = st.selectbox("Color del papel:", list(FONDOS.keys()))
    bg_color = FONDOS[fondo_nombre]

    st.header("🛠️ Herramienta")
    herramienta_nombre = st.selectbox("¿Con qué dibujo?", list(HERRAMIENTAS.keys()))
    drawing_mode = HERRAMIENTAS[herramienta_nombre]

    with st.expander("📐 Tamaño del tablero"):
        canvas_width = st.slider("Ancho", 300, 700, 500, 50)
        canvas_height = st.slider("Alto", 200, 600, 400, 50)

# ---------- Reto de números ----------
if "reto" not in st.session_state:
    st.session_state.reto = random.randint(0, 9)
if "intento" not in st.session_state:
    st.session_state.intento = 0

col_tablero, col_reto = st.columns([3, 1.3], gap="large")

with col_reto:
    st.markdown(
        f"""
        <div class="reto">
            <div class="texto">⭐ ¿Puedes escribir el número…?</div>
            <div class="numero">{st.session_state.reto}</div>
            <div class="texto">¡Tú puedes! 💪</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🎉 ¡Terminé!", use_container_width=True):
        st.balloons()
        st.success("¡Muy bien! ¡Eres un artista! 🌟")
    if st.button("🎲 Otro número", use_container_width=True):
        st.session_state.reto = random.randint(0, 9)
        st.session_state.intento += 1
        st.rerun()
    if st.button("🧽 Borrar todo", use_container_width=True):
        st.session_state.intento += 1
        st.rerun()

# ---------- Tablero ----------
with col_tablero:
    canvas_result = st_canvas(
        fill_color="rgba(255, 183, 3, 0.35)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        key=f"canvas_{canvas_width}_{canvas_height}_{st.session_state.intento}",
    )
