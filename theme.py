import flet as ft

# Paleta de colores UMLRanking
COLOR_PRIMARY = "#2563EB"       # Azul vibrante institucional
COLOR_PRIMARY_DARK = "#1E40AF"  # Azul profundo
COLOR_PRIMARY_LIGHT = "#DBEAFE" # Azul suave de fondo
COLOR_ACCENT = "#3B82F6"
COLOR_BG = "#F8FAFC"           # Fondo moderno slate-50
COLOR_CARD = "#FFFFFF"         # Tarjeta blanca pura
COLOR_TEXT_MAIN = "#0F172A"    # Slate 900
COLOR_TEXT_MUTED = "#64748B"   # Slate 500
COLOR_BORDER = "#E2E8F0"       # Slate 200

# Estados y Podio
COLOR_SUCCESS = "#10B981"      # Verde (Activo / Completado)
COLOR_WARNING = "#F59E0B"      # Ámbar (Próximo / Incompleto)
COLOR_MUTED = "#64748B"        # Gris (Finalizado / Pendiente)
COLOR_DANGER = "#EF4444"       # Rojo (Eliminar / Error)

# Metales de Cuadro de Honor
COLOR_GOLD = "#F59E0B"
COLOR_SILVER = "#64748B"
COLOR_BRONZE = "#B45309"


def safe_update(control):
    """Actualiza el control solo si ya está adjunto a una página."""
    try:
        if getattr(control, "page", None) is not None:
            control.update()
    except Exception:
        pass


def status_badge(status_text: str, bg_color: str, icon_name):
    """
    Retorna un contenedor badge estilizado con icono y texto.
    """
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon_name, size=14, color=ft.Colors.WHITE),
                ft.Text(status_text, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        bgcolor=bg_color,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


def section_header(title: str, subtitle: str = None, action_button=None):
    """
    Encabezado de sección elegante con título, subtítulo y botón opcional.
    """
    left_controls = [
        ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
    ]
    if subtitle:
        left_controls.append(ft.Text(subtitle, size=13, color=COLOR_TEXT_MUTED))

    header_row = ft.Row(
        controls=[
            ft.Column(controls=left_controls, spacing=2),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    if action_button:
        header_row.controls.append(action_button)

    return ft.Container(
        content=header_row,
        margin=ft.Padding.only(bottom=16),
    )
