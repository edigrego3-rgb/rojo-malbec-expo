import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random
import json
import urllib.parse

# =============================================
# CONFIGURACIÓN
# =============================================
ADMIN_PASSWORD = "rojomalbec2026"
BLENDS = [
    {"nombre": "Sal del Desierto", "emoji": "🌿", "ingrediente": "Pimienta Larga"},
    {"nombre": "Nanami Tōgarashi", "emoji": "⚡", "ingrediente": "Pimienta de Sichuan"},
    {"nombre": "Panch Phoron", "emoji": "🌑", "ingrediente": "Kalonji (Ajenuz)"},
    {"nombre": "Za'atar", "emoji": "🍒", "ingrediente": "Sumac (Zumaque)"},
]
EVENT_DAYS = {
    "2026-05-08": 1,
    "2026-05-09": 2,
    "2026-05-10": 3,
}
PREMIO = "Glühwein Rojo Malbec"

# =============================================
# CONEXIÓN GOOGLE SHEETS
# =============================================
@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Rojo Malbec Expo Votos").sheet1
    return sheet


def get_event_day():
    """Retorna el día del evento (1, 2, 3) o 0 si no es día de evento."""
    today = datetime.now().strftime("%Y-%m-%d")
    return EVENT_DAYS.get(today, 0)


def already_voted(sheet, telefono, dia):
    """Verifica si un teléfono ya votó hoy."""
    try:
        records = sheet.get_all_records()
        for r in records:
            if str(r.get("Telefono", "")) == str(telefono) and str(r.get("Dia", "")) == str(dia):
                return True
    except Exception:
        pass
    return False


def save_vote(sheet, blend, telefono, dia):
    """Guarda un voto en Google Sheets."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, blend, telefono, dia, "FALSE"])


def get_stats(sheet, dia=None):
    """Obtiene estadísticas de votos."""
    records = sheet.get_all_records()
    if dia:
        records = [r for r in records if str(r.get("Dia", "")) == str(dia)]

    stats = {}
    total = 0
    for r in records:
        blend = r.get("Blend", "")
        if blend:
            stats[blend] = stats.get(blend, 0) + 1
            total += 1
    return stats, total, records


# =============================================
# ESTILOS CSS
# =============================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    .main { background-color: #1a0a0a; }
    .stApp { background-color: #1a0a0a; }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #C8A020 !important;
    }

    p, div, span, label {
        font-family: 'Lato', sans-serif !important;
    }

    .brand-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }

    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #B71C1C;
        line-height: 1;
        margin-bottom: 0.2rem;
    }

    .brand-sub {
        font-family: 'Lato', sans-serif;
        font-size: 0.7rem;
        color: #C8A020;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .expo-title {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #f5f0e8 !important;
        margin: 1rem 0;
    }

    .expo-subtitle {
        text-align: center;
        font-family: 'Lato', sans-serif;
        font-size: 0.9rem;
        color: #9A8070;
        margin-bottom: 1.5rem;
    }

    .blend-card {
        background: linear-gradient(135deg, #2a1515 0%, #1a0a0a 100%);
        border: 1px solid #C8A02040;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .blend-card:hover {
        border-color: #C8A020;
        box-shadow: 0 0 15px #C8A02030;
    }

    .blend-emoji {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }

    .blend-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        color: #f5f0e8;
        font-weight: 700;
    }

    .blend-ingrediente {
        font-family: 'Lato', sans-serif;
        font-size: 0.8rem;
        color: #9A8070;
        font-style: italic;
    }

    .success-box {
        background: linear-gradient(135deg, #1a3a1a 0%, #0a2a0a 100%);
        border: 1px solid #4CAF5060;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }

    .success-box h2 {
        color: #4CAF50 !important;
        font-size: 1.5rem;
    }

    .success-box p {
        color: #a0d0a0;
    }

    .premio-text {
        font-family: 'Playfair Display', serif;
        color: #C8A020;
        font-size: 1.1rem;
        text-align: center;
        margin: 1rem 0;
        font-style: italic;
    }

    .footer-expo {
        text-align: center;
        color: #5a4a3a;
        font-size: 0.7rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #3a2a1a;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stButton > button {
        background: linear-gradient(135deg, #B71C1C, #8B0000) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-family: 'Lato', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #d32f2f, #B71C1C) !important;
        box-shadow: 0 4px 15px rgba(183, 28, 28, 0.4) !important;
    }

    .stat-card {
        background: #2a1515;
        border: 1px solid #C8A02040;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        color: #C8A020;
        font-weight: 700;
    }

    .stat-label {
        font-family: 'Lato', sans-serif;
        font-size: 0.8rem;
        color: #9A8070;
    }

    .winner-box {
        background: linear-gradient(135deg, #3a2a00 0%, #1a1500 100%);
        border: 2px solid #C8A020;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }

    .winner-box h2 {
        color: #C8A020 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================
# VISTA PÚBLICA - VOTACIÓN
# =============================================
def show_voting_page(sheet):
    # Header
    st.markdown("""
    <div class="brand-header">
        <div class="brand-name">Rojo Malbec</div>
        <div class="brand-sub">Sales & Blends de Especias y Té</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="expo-title">🌿 Experiencia Sensorial</div>', unsafe_allow_html=True)
    st.markdown('<div class="expo-subtitle">Votá por tu aroma favorito y participá del sorteo diario</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="premio-text">🏆 Premio: {PREMIO}</div>', unsafe_allow_html=True)

    # Determinar día del evento
    dia = get_event_day()
    if dia == 0:
        dia = 1  # Modo prueba fuera de fechas del evento

    # Selección de blend
    st.markdown("### ¿Cuál es tu favorito?")

    selected_blend = None
    for blend in BLENDS:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="blend-card">
                <span class="blend-emoji">{blend['emoji']}</span>
                <span class="blend-name">{blend['nombre']}</span><br>
                <span class="blend-ingrediente">Ingrediente estrella: {blend['ingrediente']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Votar", key=f"vote_{blend['nombre']}"):
                selected_blend = blend['nombre']

    if selected_blend:
        st.session_state.selected_blend = selected_blend

    if "selected_blend" in st.session_state:
        st.markdown("---")
        st.markdown(f"**Tu elección:** {st.session_state.selected_blend}")

        telefono = st.text_input(
            "📱 Tu número de celular (para el sorteo)",
            placeholder="Ej: 3544308380",
            max_chars=15
        )

        if st.button("✅ Confirmar voto y participar"):
            if not telefono or len(telefono) < 8:
                st.error("⚠️ Ingresá un número de teléfono válido para participar.")
            elif not telefono.replace(" ", "").replace("-", "").replace("+", "").isdigit():
                st.error("⚠️ El teléfono solo puede contener números.")
            else:
                telefono_clean = telefono.replace(" ", "").replace("-", "")
                if already_voted(sheet, telefono_clean, dia):
                    st.warning("🙌 ¡Ya votaste hoy! Volvé mañana para votar de nuevo.")
                else:
                    save_vote(sheet, st.session_state.selected_blend, telefono_clean, dia)
                    st.markdown(f"""
                    <div class="success-box">
                        <h2>🎉 ¡Gracias por votar!</h2>
                        <p>Votaste por <strong>{st.session_state.selected_blend}</strong></p>
                        <p>Ya estás participando del sorteo de hoy.</p>
                        <p style="color: #C8A020; margin-top: 1rem;">
                            🏆 El ganador se anuncia al cierre del stand
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    del st.session_state.selected_blend

    # Footer
    st.markdown("""
    <div class="footer-expo">
        Rojo Malbec · Ruta 14 S/N, Los Hornillos, Traslasierra – Córdoba<br>
        📞 3544 308380 · rojomalbec.com.ar
    </div>
    """, unsafe_allow_html=True)


# =============================================
# VISTA ADMIN - PANEL DE CONTROL
# =============================================
def show_admin_page(sheet):
    st.markdown("""
    <div class="brand-header">
        <div class="brand-name">Rojo Malbec</div>
        <div class="brand-sub">Panel de Control · Expo</div>
    </div>
    """, unsafe_allow_html=True)

    dia = get_event_day()
    if dia == 0:
        dia = st.selectbox("Seleccionar día (modo prueba):", [1, 2, 3])

    st.markdown(f"### 📊 Día {dia} del evento")

    stats, total, records = get_stats(sheet, dia)

    # Estadísticas generales
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total}</div>
            <div class="stat-label">Votos hoy</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_general = len(sheet.get_all_records())
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_general}</div>
            <div class="stat-label">Votos totales</div>
        </div>
        """, unsafe_allow_html=True)

    # Votos por blend
    st.markdown("### 🏆 Ranking del día")
    if stats:
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        for i, (blend, count) in enumerate(sorted_stats):
            medal = ["🥇", "🥈", "🥉", ""][min(i, 3)]
            pct = int(count / total * 100) if total > 0 else 0
            st.markdown(f"{medal} **{blend}** — {count} votos ({pct}%)")
            st.progress(pct / 100)
    else:
        st.info("Todavía no hay votos para hoy.")

    # Sorteo
    st.markdown("---")
    st.markdown("### 🎰 Sorteo del día")

    day_records = [r for r in records if str(r.get("Ganador", "")) != "TRUE"]

    if len(day_records) == 0:
        st.warning("No hay participantes para sortear.")
    else:
        st.write(f"**{len(day_records)} participantes** disponibles para el sorteo.")

        # Verificar si ya hubo ganador hoy
        all_records = sheet.get_all_records()
        winners_today = [r for r in all_records
                         if str(r.get("Dia", "")) == str(dia)
                         and str(r.get("Ganador", "")) == "TRUE"]

        if winners_today:
            winner = winners_today[0]
            st.markdown(f"""
            <div class="winner-box">
                <h2>🏆 Ganador del Día {dia}</h2>
                <p style="color: #f5f0e8; font-size: 1.3rem;">📱 {winner.get('Telefono', '')}</p>
                <p style="color: #9A8070;">Votó por: {winner.get('Blend', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            tel = str(winner.get("Telefono", ""))
            if not tel.startswith("+"):
                tel = "+54" + tel
            wa_msg = urllib.parse.quote(
                f"🎉 ¡Felicitaciones! Ganaste un {PREMIO} en la Expo Rojo Malbec. "
                f"Pasá por nuestro stand a retirarlo. 🍷"
            )
            wa_link = f"https://wa.me/{tel}?text={wa_msg}"
            st.markdown(f"[📲 Enviar WhatsApp al ganador]({wa_link})")

        else:
            if st.button("🎰 ¡SORTEAR GANADOR DEL DÍA!"):
                winner = random.choice(day_records)
                # Marcar como ganador en la sheet
                try:
                    all_values = sheet.get_all_values()
                    for idx, row in enumerate(all_values[1:], start=2):
                        if (row[2] == str(winner.get("Telefono", ""))
                                and row[3] == str(dia)):
                            sheet.update_cell(idx, 5, "TRUE")
                            break
                except Exception as e:
                    st.error(f"Error al marcar ganador: {e}")

                st.markdown(f"""
                <div class="winner-box">
                    <h2>🏆 ¡GANADOR!</h2>
                    <p style="color: #f5f0e8; font-size: 1.3rem;">📱 {winner.get('Telefono', '')}</p>
                    <p style="color: #9A8070;">Votó por: {winner.get('Blend', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                st.rerun()

    # Lista de todos los votos del día
    with st.expander(f"📋 Todos los votos del Día {dia}"):
        if records:
            for r in records:
                ganador = " 🏆" if str(r.get("Ganador", "")) == "TRUE" else ""
                st.write(f"📱 {r.get('Telefono', '')} → {r.get('Blend', '')}{ganador}")
        else:
            st.write("Sin votos.")


# =============================================
# MAIN
# =============================================
def main():
    st.set_page_config(
        page_title="Rojo Malbec · Votación Expo",
        page_icon="🍷",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    inject_css()

    # Check for admin mode via session state or sidebar
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    with st.sidebar:
        st.markdown("<h3 style='color: #C8A020;'>Panel de Control</h3>", unsafe_allow_html=True)
        password = st.text_input("Contraseña:", type="password", key="admin_pass")
        if password == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("Acceso concedido")
        elif password:
            st.error("Incorrecta")

    if st.session_state.is_admin:
        try:
            sheet = get_sheet()
            show_admin_page(sheet)
        except Exception as e:
            st.error(f"Error conectando a Google Sheets: {e}")
            st.info("Verificá las credenciales en Streamlit Secrets.")
    else:
        try:
            sheet = get_sheet()
            show_voting_page(sheet)
        except Exception as e:
            st.error(f"Error conectando a Google Sheets: {e}")
            st.info("La votación estará disponible pronto. ¡Volvé en unos minutos!")


if __name__ == "__main__":
    main()
