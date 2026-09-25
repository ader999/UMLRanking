import flet as ft
from ..theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
    COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED, COLOR_DANGER,
    status_badge, safe_update
)
from ..components.event_card import format_iso_date
from ..components.dialogs import (
    show_add_criterio_dialog,
    show_add_participante_dialog,
    show_add_jurado_dialog,
    show_confirm_dialog
)


def build_evento_detail_view(
    api_client,
    evento_id: int,
    page: ft.Page,
    on_back,
    on_edit_evento,
    on_evaluate_evento,
    on_results_evento
):
    """
    Construye la vista completa de detalle de un evento.
    Replica todas las opciones de eventos/detalle.html, gestionar_criterios.html,
    gestionar_participantes.html y gestionar_jurado.html.
    """
    evento_state = {}
    loading_ring = ft.ProgressRing(visible=True)
    content_column = ft.Column(spacing=20, visible=False)

    def show_snack(text: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(text, color=ft.Colors.WHITE),
            bgcolor=COLOR_DANGER if is_error else COLOR_SUCCESS,
        )
        page.overlay.append(snack)
        snack.open = True
        safe_update(page)

    def reload_data():
        loading_ring.visible = True
        content_column.visible = False
        safe_update(loading_ring)
        safe_update(content_column)

        res = api_client.get_evento(evento_id)
        if not res.get("success"):
            show_snack("Error al cargar los datos del evento.", is_error=True)
            on_back()
            return

        evento_state.clear()
        evento_state.update(res["data"])
        render_ui()

        loading_ring.visible = False
        content_column.visible = True
        safe_update(loading_ring)
        safe_update(content_column)

    def render_ui():
        content_column.controls.clear()
        evento = evento_state

        is_active = evento.get("esta_activo", False)
        is_finished = evento.get("ha_finalizado", False)
        es_jurado = evento.get("es_jurado", False)
        es_admin = evento.get("es_administrador", False)

        # --------------------------------------------------------------------
        # 1. Barra de Navegación / Migas de pan
        # --------------------------------------------------------------------
        nav_bar = ft.Row(
            controls=[
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_BACK, size=16),
                        ft.Text("Volver a Eventos", weight=ft.FontWeight.BOLD),
                    ]),
                    on_click=lambda _: on_back(),
                ),
                ft.Text("/", color=COLOR_TEXT_MUTED),
                ft.Text(evento.get("nombre", ""), color=COLOR_PRIMARY, weight=ft.FontWeight.W_500),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --------------------------------------------------------------------
        # 2. Header Banner
        # --------------------------------------------------------------------
        if is_active:
            badge = status_badge("En Curso", COLOR_SUCCESS, ft.Icons.PLAY_CIRCLE)
        elif is_finished:
            badge = status_badge("Finalizado", COLOR_MUTED, ft.Icons.CHECK_CIRCLE)
        else:
            badge = status_badge("Próximo", COLOR_WARNING, ft.Icons.ACCESS_TIME)

        action_buttons = []
        if (es_jurado or es_admin) and is_active:
            action_buttons.append(
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.STAR, color=ft.Colors.WHITE, size=18),
                        ft.Text("Evaluar Equipos", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS),
                    height=46,
                    on_click=lambda _: on_evaluate_evento(evento["id"]),
                )
            )

        if is_finished or es_admin:
            action_buttons.append(
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.WHITE, size=18),
                        ft.Text("Ver Tabla de Posiciones", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor="#1E293B"),
                    height=46,
                    on_click=lambda _: on_results_evento(evento["id"]),
                )
            )

        banner = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(evento.get("nombre", ""), size=26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN, expand=True),
                            badge,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(evento.get("descripcion") or "Sin descripción detallada.", size=14, color=COLOR_TEXT_MUTED),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=COLOR_PRIMARY),
                                    ft.Text(f"Inicio: {format_iso_date(evento.get('fecha_inicio'))}", size=12, color=COLOR_TEXT_MAIN),
                                ], spacing=6),
                                ft.Row([
                                    ft.Icon(ft.Icons.EVENT_AVAILABLE, size=14, color=COLOR_DANGER),
                                    ft.Text(f"Cierre: {format_iso_date(evento.get('fecha_fin'))}", size=12, color=COLOR_TEXT_MAIN),
                                ], spacing=6),
                                ft.Row([
                                    ft.Icon(ft.Icons.WORKSPACE_PREMIUM, size=14, color=COLOR_WARNING),
                                    ft.Text(f"Pts Máximos: {evento.get('total_criterios_score', 0)} pts", size=12, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                ], spacing=6),

                            ],
                            wrap=True,
                            spacing=20,
                        ),
                        bgcolor="#F8FAFC",
                        border=ft.Border.all(1, COLOR_BORDER),
                        border_radius=8,
                        padding=12,
                    ),
                    ft.Row(controls=action_buttons, spacing=12) if action_buttons else ft.Container(),
                ],
                spacing=14,
            ),
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=24,
        )

        # --------------------------------------------------------------------
        # 3. Sección de Participantes
        # --------------------------------------------------------------------
        participantes = evento.get("participantes", [])

        def handle_add_participante(data):
            res = api_client.add_participante(evento_id, data)
            if res.get("success"):
                show_snack("Participante registrado con éxito.")
                reload_data()
            else:
                show_snack("Error al registrar participante.", is_error=True)

        def handle_delete_participante(p_id, p_nombre):
            def confirm():
                res = api_client.delete_participante(p_id)
                if res.get("success"):
                    show_snack(f"Participante '{p_nombre}' eliminado.")
                    reload_data()
                else:
                    show_snack("Error al eliminar participante.", is_error=True)

            show_confirm_dialog(
                page,
                "Eliminar Participante",
                f"¿Estás seguro de eliminar a '{p_nombre}'? Se borrarán todas las evaluaciones recibidas.",
                confirm,
                is_danger=True,
            )

        participantes_controls = []
        if participantes:
            for p in participantes:
                p_id = p["id"]
                p_nombre = p["nombre"]
                item_row = ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(p_nombre, weight=ft.FontWeight.BOLD, size=15, color=COLOR_TEXT_MAIN),
                                ft.Text(p.get("descripcion") or "Sin descripción", size=12, color=COLOR_TEXT_MUTED),
                                ft.Row([
                                    ft.Icon(ft.Icons.GROUP, size=14, color=COLOR_PRIMARY),
                                    ft.Text(f"Integrantes: {p.get('integrantes') or 'No especificados'}", size=11, color=COLOR_TEXT_MAIN),
                                ], spacing=4) if p.get("integrantes") else ft.Container(),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                if es_admin:
                    item_row.controls.append(
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=COLOR_DANGER,
                            tooltip="Eliminar Participante",
                            on_click=lambda _, pid=p_id, pnom=p_nombre: handle_delete_participante(pid, pnom),
                        )
                    )

                participantes_controls.append(
                    ft.Container(
                        content=item_row,
                        padding=12,
                        border_radius=8,
                        bgcolor="#F8FAFC",
                        border=ft.Border.all(1, COLOR_BORDER),
                    )
                )
        else:
            participantes_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.GROUP_OFF, size=36, color=ft.Colors.GREY_400),
                            ft.Text("No hay participantes registrados.", size=13, color=COLOR_TEXT_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                )
            )

        participantes_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.GROUPS, color=COLOR_PRIMARY, size=20),
                                ft.Text(f"Equipos / Participantes ({len(participantes)})", weight=ft.FontWeight.BOLD, size=16, color=COLOR_TEXT_MAIN),
                            ], spacing=8),
                            ft.FilledButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                    ft.Text("Agregar Proyecto", size=12, color=ft.Colors.WHITE),
                                ], tight=True),
                                style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
                                on_click=lambda _: show_add_participante_dialog(page, handle_add_participante),
                            ) if es_admin else ft.Container(),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Column(controls=participantes_controls, spacing=10),
                ],
                spacing=14,
            ),
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=20,
            expand=True,
        )

        # --------------------------------------------------------------------
        # 4. Sección de Criterios de Evaluación
        # --------------------------------------------------------------------
        criterios = evento.get("criterios", [])

        def handle_add_criterio(data):
            res = api_client.add_criterio(evento_id, data)
            if res.get("success"):
                show_snack("Criterio agregado exitosamente.")
                reload_data()
            else:
                show_snack("Error al agregar criterio.", is_error=True)

        def handle_delete_criterio(c_id, c_nombre):
            def confirm():
                res = api_client.delete_criterio(c_id)
                if res.get("success"):
                    show_snack(f"Criterio '{c_nombre}' eliminado.")
                    reload_data()
                else:
                    show_snack("Error al eliminar criterio.", is_error=True)

            show_confirm_dialog(
                page,
                "Eliminar Criterio",
                f"¿Estás seguro de eliminar el criterio '{c_nombre}'? Se borrarán las evaluaciones asociadas.",
                confirm,
                is_danger=True,
            )

        criterios_controls = []
        if criterios:
            for c in criterios:
                c_id = c["id"]
                c_nombre = c["nombre"]
                c_pts = c.get("puntaje_maximo", 0)
                item_row = ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(c_nombre, weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT_MAIN),
                                ft.Text(c.get("descripcion") or "Sin descripción", size=12, color=COLOR_TEXT_MUTED),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.Container(
                            content=ft.Text(f"{c_pts} pts", size=13, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                            bgcolor=COLOR_PRIMARY_LIGHT,
                            border_radius=6,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                if es_admin:
                    item_row.controls.append(
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=COLOR_DANGER,
                            tooltip="Eliminar Criterio",
                            on_click=lambda _, cid=c_id, cnom=c_nombre: handle_delete_criterio(cid, cnom),
                        )
                    )

                criterios_controls.append(
                    ft.Container(
                        content=item_row,
                        padding=12,
                        border_radius=8,
                        bgcolor="#F8FAFC",
                        border=ft.Border.all(1, COLOR_BORDER),
                    )
                )
        else:
            criterios_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.CHECKLIST_RTL, size=36, color=ft.Colors.GREY_400),
                            ft.Text("No hay criterios definidos.", size=13, color=COLOR_TEXT_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                )
            )

        criterios_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.CHECKLIST, color=COLOR_WARNING, size=20),
                                ft.Text(f"Criterios de Evaluación ({len(criterios)})", weight=ft.FontWeight.BOLD, size=16, color=COLOR_TEXT_MAIN),
                            ], spacing=8),
                            ft.FilledButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                                    ft.Text("Agregar Criterio", size=12, color=ft.Colors.WHITE),
                                ], tight=True),
                                style=ft.ButtonStyle(bgcolor=COLOR_WARNING),
                                on_click=lambda _: show_add_criterio_dialog(page, handle_add_criterio),
                            ) if es_admin else ft.Container(),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Column(controls=criterios_controls, spacing=10),
                ],
                spacing=14,
            ),
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=20,
            expand=True,
        )

        # --------------------------------------------------------------------
        # 5. Sección Lateral: Jurados y Administración
        # --------------------------------------------------------------------
        sidebar_controls = []

        if evento.get("requiere_jurado"):
            jurados = evento.get("jurados", [])

            def handle_add_jurado(usuario_id):
                res = api_client.add_jurado(evento_id, usuario_id)
                if res.get("success"):
                    show_snack("Jurado asignado exitosamente.")
                    reload_data()
                else:
                    show_snack("Error al asignar jurado.", is_error=True)

            def open_jurado_dialog():
                disponibles = api_client.get_usuarios_disponibles(evento_id)
                show_add_jurado_dialog(page, disponibles, handle_add_jurado)

            def handle_remove_jurado(j_id, j_nombre):
                def confirm():
                    res = api_client.delete_jurado(j_id)
                    if res.get("success"):
                        show_snack(f"Jurado '{j_nombre}' removido.")
                        reload_data()
                    else:
                        show_snack("Error al remover jurado.", is_error=True)

                show_confirm_dialog(
                    page,
                    "Remover Jurado",
                    f"¿Estás seguro de remover a '{j_nombre}' del jurado? Se borrarán sus evaluaciones registradas.",
                    confirm,
                    is_danger=True,
                )

            jurados_list_controls = []
            if jurados:
                for j in jurados:
                    j_id = j["id"]
                    u = j.get("usuario_detalle", {})
                    j_nombre = u.get("full_name") or u.get("username", "Jurado")
                    j_user = u.get("username", "")

                    j_row = ft.Row(
                        controls=[
                            ft.Row([
                                ft.CircleAvatar(
                                    content=ft.Icon(ft.Icons.PERSON, size=14, color=ft.Colors.WHITE),
                                    bgcolor=COLOR_PRIMARY,
                                    radius=14,
                                ),
                                ft.Column([
                                    ft.Text(j_nombre, weight=ft.FontWeight.BOLD, size=13, color=COLOR_TEXT_MAIN),
                                    ft.Text(f"@{j_user}", size=11, color=COLOR_TEXT_MUTED),
                                ], spacing=0),
                            ], spacing=8),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                    if es_admin:
                        j_row.controls.append(
                            ft.IconButton(
                                icon=ft.Icons.PERSON_REMOVE,
                                icon_color=COLOR_DANGER,
                                tooltip="Remover del jurado",
                                on_click=lambda _, jid=j_id, jnom=j_nombre: handle_remove_jurado(jid, jnom),
                            )
                        )

                    jurados_list_controls.append(
                        ft.Container(
                            content=j_row,
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=8,
                            border=ft.Border.all(1, COLOR_BORDER),
                        )
                    )
            else:
                jurados_list_controls.append(
                    ft.Text("No hay jurados asignados aún.", size=12, color=COLOR_TEXT_MUTED)
                )

            jurados_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.GAVEL, color=COLOR_PRIMARY, size=18),
                                    ft.Text("Jurado Asignado", weight=ft.FontWeight.BOLD, size=15, color=COLOR_TEXT_MAIN),
                                ], spacing=6),
                                ft.IconButton(
                                    icon=ft.Icons.PERSON_ADD,
                                    icon_color=COLOR_PRIMARY,
                                    tooltip="Asignar Jurado",
                                    on_click=lambda _: open_jurado_dialog(),
                                ) if es_admin else ft.Container(),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Column(controls=jurados_list_controls, spacing=8),
                    ],
                    spacing=12,
                ),
                bgcolor=COLOR_CARD,
                border=ft.Border.all(1, COLOR_BORDER),
                border_radius=12,
                padding=16,
            )
            sidebar_controls.append(jurados_card)

        # Panel de Administración
        if es_admin:
            def handle_delete_evento():
                def confirm():
                    res = api_client.delete_evento(evento_id)
                    if res.get("success"):
                        show_snack("Evento eliminado permanentemente.")
                        on_back()
                    else:
                        show_snack("Error al eliminar evento.", is_error=True)

                show_confirm_dialog(
                    page,
                    "Eliminar Evento",
                    f"¿Estás seguro de eliminar permanentemente el evento '{evento.get('nombre')}'? Esta acción es irreversible.",
                    confirm,
                    is_danger=True,
                )

            admin_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.SETTINGS, color="#1E293B", size=18),
                            ft.Text("Administración", weight=ft.FontWeight.BOLD, size=15, color=COLOR_TEXT_MAIN),
                        ], spacing=6),
                        ft.Text("Eres creador o administrador de este evento.", size=11, color=COLOR_TEXT_MUTED),
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EDIT, size=16),
                                ft.Text("Editar Evento", weight=ft.FontWeight.BOLD, size=12),
                            ], tight=True),
                            on_click=lambda _: on_edit_evento(evento_id),
                        ),
                        ft.FilledButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DELETE_FOREVER, size=16, color=ft.Colors.WHITE),
                                ft.Text("Eliminar Evento", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                            ], tight=True),
                            style=ft.ButtonStyle(bgcolor=COLOR_DANGER),
                            on_click=lambda _: handle_delete_evento(),
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor=COLOR_CARD,
                border=ft.Border.all(1, COLOR_BORDER),
                border_radius=12,
                padding=16,
            )
            sidebar_controls.append(admin_card)

        # Ensamble de Columnas
        main_columns = ft.Row(
            controls=[
                ft.Column(
                    controls=[participantes_card, criterios_card],
                    expand=7,
                    spacing=20,
                ),
                ft.Column(
                    controls=sidebar_controls,
                    expand=4,
                    spacing=20,
                ) if sidebar_controls else ft.Container(),
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        content_column.controls.extend([
            nav_bar,
            banner,
            main_columns,
        ])

    view_container = ft.Container(
        content=ft.Column(
            controls=[
                loading_ring,
                content_column,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=24,
        expand=True,
    )

    view_container.load_data = reload_data
    return view_container
