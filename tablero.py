import random
import numpy as np
import streamlit as st
from PIL import Image, ImageFilter
from sklearn.datasets import load_digits
from sklearn.svm import SVC
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
    .stApp {
        background-color: #FFF6D6;
        background-image:
            radial-gradient(#FF8FAB 2.5px, transparent 2.5px),
            radial-gradient(#7BDFF2 2.5px, transparent 2.5px);
        background-size: 46px 46px;
        background-position: 0 0, 23px 23px;
    }
    .titulo { text-align: center; font-size: 3.4rem; font-weight: 800; line-height: 1.1; margin: 0.2rem 0 0.4rem 0; }
    .titulo span {
        display: inline-block;
        text-shadow: 3px 3px 0 #ffffff, 5px 5px 0 rgba(0,0,0,0.12);
        animation: saltito 1.6s ease-in-out infinite;
    }
    @keyframes saltito { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    @media (prefers-reduced-motion: reduce) { .titulo span { animation: none; } }
    .subtitulo { text-align: center; font-size: 1.3rem; color: #5A4FCF; margin-bottom: 1rem; }

    .reto {
        background: #ffffff; border: 5px solid #FFB703; border-radius: 30px;
        padding: 0.6rem 1rem; text-align: center; box-shadow: 6px 6px 0 #FB8500;
    }
    .reto .texto { font-size: 1.3rem; color: #3D348B; }
    .reto .numero { font-size: 6rem; font-weight: 800; line-height: 1; color: #F15BB5; text-shadow: 4px 4px 0 #FEE440; }

    /* Globo de respuesta del robot */
    .respuesta {
        border-radius: 30px; padding: 0.8rem 1rem; text-align: center;
        font-size: 1.5rem; font-weight: 700; margin-top: 1rem; border: 5px solid #fff;
    }
    .respuesta .grande { font-size: 4.5rem; line-height: 1; display: block; }
    .bien     { background: #D8F8E1; color: #1B7F4B; box-shadow: 6px 6px 0 #06D6A0; }
    .casi     { background: #FFF1C1; color: #9A5B00; box-shadow: 6px 6px 0 #FFB703; }
    .otra_vez { background: #FFE0EC; color: #B0175F; box-shadow: 6px 6px 0 #F15BB5; }

    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border: 8px dashed #00BBF9 !important; border-radius: 28px;
        box-shadow: 8px 8px 0 #9B5DE5; background: #fff;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #CDB4DB 0%, #FFC8DD 50%, #BDE0FE 100%);
        border-right: 6px solid #ffffff;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #3D348B; }

    .stButton > button {
        background: #06D6A0; color: white; font-size: 1.3rem; font-weight: 700;
        border: 4px solid #ffffff; border-radius: 999px; padding: 0.4rem 1.4rem;
        box-shadow: 4px 4px 0 #118AB2; transition: transform 0.1s;
    }
    .stButton > button:hover { transform: scale(1.06); color: white; border-color: #fff; }
    .stButton > button:active { transform: scale(0.96); }
    .stButton > button:focus-visible { outline: 4px solid #FFB703; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- El "cerebro" que reconoce números ----------
def normalizar(gris, margen=1.15):
    """Recorta el número, lo centra en un cuadrado y lo achica a 8x8 (valores de 0 a 16)."""
    trazo = gris > 40
    if trazo.sum() == 0:
        return None
    filas = np.where(trazo.any(axis=1))[0]
    cols = np.where(trazo.any(axis=0))[0]
    recorte = gris[filas[0]:filas[-1] + 1, cols[0]:cols[-1] + 1]
    alto, ancho = recorte.shape
    lado = int(max(alto, ancho) * margen) + 1
    cuadro = np.zeros((lado, lado), dtype=np.uint8)
    y0, x0 = (lado - alto) // 2, (lado - ancho) // 2
    cuadro[y0:y0 + alto, x0:x0 + ancho] = recorte
    pequeno = Image.fromarray(cuadro).resize((8, 8), Image.BOX)
    return np.asarray(pequeno, dtype=float) / 255.0 * 16.0


@st.cache_resource(show_spinner="🧠 Enseñándole números al robot…")
def entrenar_modelo():
    """Entrena con los números escritos a mano que trae scikit-learn (no descarga nada)."""
    digitos = load_digits()
    X, y = [], []
    for imagen, numero in zip(digitos.images, digitos.target):
        grande = Image.fromarray((imagen / 16 * 255).astype(np.uint8)).resize((64, 64), Image.BILINEAR)
        # Variaciones: inclinado a los lados y con trazo más gordo, como escriben los niños
        variantes = [
            grande,
            grande.rotate(-12, resample=Image.BILINEAR),
            grande.rotate(12, resample=Image.BILINEAR),
            grande.filter(ImageFilter.MaxFilter(5)),
        ]
        for v in variantes:
            datos = normalizar(np.asarray(v))
            if datos is not None:
                X.append(datos.ravel())
                y.append(numero)
    modelo = SVC(gamma=0.001, C=10, probability=True)
    modelo.fit(X, y)
    return modelo


def hex_a_rgb(color_hex):
    color_hex = color_hex.lstrip("#")
    return np.array([int(color_hex[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def reconocer(image_data, bg_color):
    """Devuelve (número, seguridad) o (None, 0) si el tablero está vacío."""
    if image_data is None:
        return None, 0.0
    img = np.asarray(image_data).astype(float)
    rgb, alpha = img[:, :, :3], img[:, :, 3]
    # Un píxel es "dibujo" si no es transparente y no es del color del fondo
    distancia = np.linalg.norm(rgb - hex_a_rgb(bg_color), axis=2)
    trazo = (alpha > 0) & (distancia > 60)
    if trazo.sum() < 30:
        return None, 0.0
    datos = normalizar(trazo.astype(np.uint8) * 255)
    probabilidades = entrenar_modelo().predict_proba(datos.reshape(1, -1))[0]
    numero = int(np.argmax(probabilidades))
    return numero, float(probabilidades[numero])


# ---------- Título ----------
letras = "Mi Tablero Mágico"
colores = ["#F15BB5", "#FB8500", "#FFB703", "#06D6A0", "#00BBF9", "#9B5DE5"]
titulo_html = "".join(
    f'<span style="color:{colores[i % len(colores)]}; animation-delay:{i * 0.08:.2f}s">'
    f'{"&nbsp;" if c == " " else c}</span>'
    for i, c in enumerate(letras)
)
st.markdown(f'<div class="titulo">🖍️ {titulo_html} 🌈</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">¡Escribe un número grande y yo te digo cuál es!</div>',
            unsafe_allow_html=True)

# ---------- Barra lateral ----------
COLORES_CRAYON = {
    "🍓 Fresa": "#F15BB5", "🍊 Naranja": "#FB8500", "🌞 Sol": "#FFB703",
    "🐸 Rana": "#06D6A0", "🐳 Ballena": "#00BBF9", "🍇 Uva": "#9B5DE5", "🐻 Oso": "#6D4C41",
}
FONDOS = {
    "☁️ Nube blanca": "#FFFFFF", "🍦 Vainilla": "#FFF8E1", "🌸 Rosita": "#FFE5EC",
    "💧 Cielo": "#E0F7FF", "🌙 Noche": "#2B2D42",
}
HERRAMIENTAS = {
    "✏️ Lápiz mágico": "freedraw", "📏 Línea": "line", "🟦 Cuadrado": "rect",
    "🟣 Círculo": "circle", "✋ Mover": "transform",
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

# ---------- Estado ----------
if "reto" not in st.session_state:
    st.session_state.reto = random.randint(0, 9)
if "intento" not in st.session_state:
    st.session_state.intento = 0

col_tablero, col_reto = st.columns([3, 1.3], gap="large")

# ---------- Tablero (va primero para poder leer el dibujo) ----------
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

# ---------- Reto y respuesta ----------
with col_reto:
    reto = st.session_state.reto
    st.markdown(
        f"""
        <div class="reto">
            <div class="texto">⭐ ¿Puedes escribir el número…?</div>
            <div class="numero">{reto}</div>
            <div class="texto">¡Tú puedes! 💪</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    if st.button("🔍 ¿Qué número es?", use_container_width=True):
        numero, seguridad = reconocer(canvas_result.image_data, bg_color)

        if numero is None:
            st.markdown(
                '<div class="respuesta otra_vez"><span class="grande">🙈</span>'
                '¡No veo nada! Dibuja un número grandote en el tablero.</div>',
                unsafe_allow_html=True,
            )
        elif seguridad < 0.5:
            st.markdown(
                '<div class="respuesta otra_vez"><span class="grande">🤔</span>'
                'Mmm… no estoy seguro de qué número es.<br>¡Bórralo e inténtalo de nuevo!</div>',
                unsafe_allow_html=True,
            )
        elif numero == reto:
            st.balloons()
            st.markdown(
                f'<div class="respuesta bien"><span class="grande">{numero}</span>'
                f'¡Muy bien! 🌟 ¡Ese es el {numero}!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="respuesta casi"><span class="grande">{numero}</span>'
                f'¡Qué bonito {numero}! 😊<br>Pero el reto era el {reto}. ¿Lo intentas?</div>',
                unsafe_allow_html=True,
            )

    if st.button("🎲 Otro número", use_container_width=True):
        st.session_state.reto = random.randint(0, 9)
        st.session_state.intento += 1
        st.rerun()
    if st.button("🧽 Borrar todo", use_container_width=True):
        st.session_state.intento += 1
        st.rerun()
