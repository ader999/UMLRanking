import flet as ft
from ..theme import (
    COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED, COLOR_DANGER,
    status_badge
)



def format_iso_date(iso_str: str) -> str:
    """Formatea fechas ISO a formato legible dd/mm/aaaa HH:MM"""
    if not iso_str:
        return "-"
    try:
        clean = iso_str.replace("Z", "").split(".")[0]
        parts = clean.split("T")
        date_parts = parts[0].split("-")
        time_part = parts[1][:5] if len(parts) > 1 else ""
        return f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]} {time_part}"
    except Exception:
        return iso_str[:16]


def create_event_card(evento: dict, on_view_details, on_evaluate=None, on_view_results=None):
    """
    Construye la tarjeta de evento que replica fielmente el diseño de event_card.html.
    """
    is_active = evento.get("esta_activo", False)
    is_finished = evento.get("ha_finalizado", False)
    es_jurado = evento.get("es_jurado", False)
    es_admin = evento.get("es_administrador", False)

    # Determinación de Badge
    if is_active:
        badge = status_badge("En Curso", COLOR_SUCCESS, ft.Icons.PLAY_CIRCLE)
    elif is_finished:
        badge = status_badge("Finalizado", COLOR_MUTED, ft.Icons.CHECK_CIRCLE)
    else:
        badge = status_badge("Próximo", COLOR_WARNING, ft.Icons.ACCESS_TIME)

    # Imagen o Placeholder visual
    imagen_url = evento.get("imagen")
    if imagen_url:
        img_control = ft.Image(
            src=imagen_url,
            width=360,
            height=130,
            fit=ft.BoxFit.COVER,
            border_radius=ft.BorderRadius.vertical(top=10),
        )
    else:
        img_control = ft.Container(
            content=ft.Icon(ft.Icons.CALENDAR_MONTH, size=50, color=COLOR_PRIMARY),
            bgcolor=COLOR_PRIMARY_LIGHT,
            height=120,
            alignment=ft.Alignment(0, 0),
            border_radius=ft.BorderRadius.vertical(top=10),
        )

    # Cabecera de la tarjeta con imagen y badge encima
    banner_stack = ft.Stack(
        controls=[
            img_control,
            ft.Container(
                content=badge,
                top=10,
                right=10,
            ),
        ]
    )

    # Información del creador
    creador_info = evento.get("creado_por_detalle") or {}
    creador_nombre = creador_info.get("full_name") or creador_info.get("username", "Admin")

    # Fechas
    fecha_inicio_str = format_iso_date(evento.get("fecha_inicio", ""))
    fecha_fin_str = format_iso_date(evento.get("fecha_fin", ""))

    # Métricas
    participantes_count = evento.get("participantes_count", 0)
    jurados_count = evento.get("jurados_count", 0) if evento.get("requiere_jurado") else "N/A"
    max_pts = evento.get("total_criterios_score", 0)

    # Bloques de métricas pequeñas
    def stat_box(value, label, value_color=COLOR_TEXT_MAIN):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(str(value), size=14, weight=ft.FontWeight.BOLD, color=value_color),
                    ft.Text(label, size=10, color=COLOR_TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=COLOR_PRIMARY_LIGHT if value_color == COLOR_PRIMARY else "#F1F5F9",
            border_radius=6,
            padding=ft.Padding.symmetric(vertical=6, horizontal=8),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    # Botones de Acción
    action_buttons = [
        ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16),
                    ft.Text("Ver Detalles", weight=ft.FontWeight.BOLD, size=12),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            style=ft.ButtonStyle(
                color=COLOR_PRIMARY,
                side=ft.BorderSide(1, COLOR_PRIMARY),
            ),
            on_click=lambda _: on_view_details(evento["id"]),
            expand=True,
        )
    ]

    # Botón Evaluar si está activo y es jurado o admin
    if is_active and (es_jurado or es_admin) and on_evaluate:
        action_buttons.append(
            ft.FilledButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.STAR, size=16, color=ft.Colors.WHITE),
                        ft.Text("Evaluar", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS),
                on_click=lambda _: on_evaluate(evento["id"]),
                expand=True,
            )
        )

    # Botón Resultados si finalizó o es admin
    if (is_finished or es_admin) and on_view_results:
        action_buttons.append(
            ft.FilledButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.EMOJI_EVENTS, size=16, color=ft.Colors.WHITE),
                        ft.Text("Resultados", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                style=ft.ButtonStyle(bgcolor="#1E293B"),
                on_click=lambda _: on_view_results(evento["id"]),
                expand=True,
            )
        )

    # Construir tarjeta completa
    card_content = ft.Column(
        controls=[
            banner_stack,
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Creado por
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PERSON_OUTLINE, size=13, color=COLOR_PRIMARY),
                                ft.Text(f"Por: {creador_nombre}", size=11, color=COLOR_TEXT_MUTED),
                            ],
                            spacing=4,
                        ),
                        # Nombre del evento
                        ft.Text(
                            evento.get("nombre", "Sin Nombre"),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXT_MAIN,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        # Descripción
                        ft.Text(
                            evento.get("descripcion") or "Sin descripción para este evento.",
                            size=12,
                            color=COLOR_TEXT_MUTED,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        # Fechas Inicio y Fin
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=12, color=COLOR_PRIMARY),
                                            ft.Text(f"Inicio: {fecha_inicio_str}", size=11, color=COLOR_TEXT_MAIN),
                                        ],
                                        spacing=6,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.EVENT_AVAILABLE, size=12, color=COLOR_DANGER),
                                            ft.Text(f"Cierre: {fecha_fin_str}", size=11, color=COLOR_TEXT_MAIN),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                spacing=4,
                            ),
                            bgcolor="#F8FAFC",
                            border=ft.Border.all(1, COLOR_BORDER),
                            border_radius=6,
                            padding=8,
                        ),
                        # Fila de métricas
                        ft.Row(
                            controls=[
                                stat_box(participantes_count, "Proyectos"),
                                stat_box(jurados_count, "Jurados"),
                                stat_box(f"{max_pts}p", "Pts Máx", COLOR_PRIMARY),
                            ],
                            spacing=8,
                        ),
                        # Fila de botones de acción
                        ft.Row(
                            controls=action_buttons,
                            spacing=6,
                        ),
                    ],
                    spacing=10,
                ),
                padding=14,
            ),
        ],
        spacing=0,
    )

    return ft.Container(
        content=card_content,
        width=360,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=10,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
