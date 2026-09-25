import flet as ft
from ..theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
    COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED, COLOR_DANGER,
    status_badge, safe_update
)


def build_evaluar_lista_view(api_client, evento_id: int, on_back, on_select_project):
    """
    Construye la vista de lista de proyectos a evaluar por el jurado.
    Replica todas las opciones de eventos/evaluar_lista.html.
    """
    loading_ring = ft.ProgressRing(visible=True)
    content_column = ft.Column(spacing=20, visible=False)
    participantes_list_container = ft.Column(spacing=12)
    header_subtitle = ft.Text("", size=14, color=COLOR_TEXT_MAIN)

    def load_data():
        loading_ring.visible = True
        content_column.visible = False
        safe_update(loading_ring)
        safe_update(content_column)

        res = api_client.get_evaluar_lista(evento_id)
        loading_ring.visible = False
        safe_update(loading_ring)

        if not res.get("success"):
            err = res.get("error", {})
            msg = err.get("detail") or "No se pudo cargar la lista de evaluación."
            content_column.controls.clear()
            content_column.controls.extend([
                ft.TextButton(
                    content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Volver al Evento")]),
                    on_click=lambda _: on_back(),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=COLOR_DANGER),
                        ft.Text(msg, size=16, weight=ft.FontWeight.BOLD, color=COLOR_DANGER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                ),
            ])
            content_column.visible = True
            safe_update(content_column)
            return

        data = res["data"]
        ev_nombre = data.get("evento_nombre", "")
        participantes = data.get("participantes", [])
        user_name = (api_client.user.get("full_name") or api_client.user.get("username", "Jurado")) if api_client.user else "Jurado"

        header_subtitle.value = f"Bienvenido/a {user_name}. Como jurado asignado para el evento {ev_nombre}, evalúa cada equipo participante según los criterios."

        participantes_list_container.controls.clear()
        if participantes:
            for p in participantes:
                p_id = p["id"]
                p_nombre = p["nombre"]
                p_desc = p.get("descripcion") or "Sin descripción"
                p_integrantes = p.get("integrantes", "")
                p_estado = p.get("estado_evaluacion", "Pendiente")

                if p_estado == "Completado":
                    badge = status_badge("Completado", COLOR_SUCCESS, ft.Icons.CHECK_CIRCLE)
                    btn_text = "Modificar"
                    btn_style = ft.ButtonStyle(color=COLOR_SUCCESS, side=ft.BorderSide(1, COLOR_SUCCESS))
                    btn_filled = False
                elif p_estado == "Incompleto":
                    badge = status_badge("Incompleto", COLOR_WARNING, ft.Icons.WARNING)
                    btn_text = "Completar"
                    btn_style = ft.ButtonStyle(bgcolor=COLOR_WARNING)
                    btn_filled = True
                else:
                    badge = status_badge("Pendiente", COLOR_MUTED, ft.Icons.RADIO_BUTTON_UNCHECKED)
                    btn_text = "Evaluar"
                    btn_style = ft.ButtonStyle(bgcolor=COLOR_SUCCESS)
                    btn_filled = True

                action_btn = (
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.STAR, size=16, color=ft.Colors.WHITE),
                            ft.Text(btn_text, weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                        ], tight=True),
                        style=btn_style,
                        on_click=lambda _, pid=p_id: on_select_project(pid),
                    )
                    if btn_filled
                    else ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.EDIT, size=16),
                            ft.Text(btn_text, weight=ft.FontWeight.BOLD, size=12),
                        ], tight=True),
                        style=btn_style,
                        on_click=lambda _, pid=p_id: on_select_project(pid),
                    )
                )

                item_card = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row([
                                        ft.Text(p_nombre, size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                                        badge,
                                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    ft.Text(p_desc, size=12, color=COLOR_TEXT_MUTED),
                                    ft.Row([
                                        ft.Icon(ft.Icons.GROUP, size=14, color=COLOR_PRIMARY),
                                        ft.Text(f"Integrantes: {p_integrantes}", size=11, color=COLOR_TEXT_MAIN),
                                    ], spacing=4) if p_integrantes else ft.Container(),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            action_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=COLOR_CARD,
                    border=ft.Border.all(1, COLOR_BORDER),
                    border_radius=10,
                    padding=16,
                )
                participantes_list_container.controls.append(item_card)
        else:
            participantes_list_container.controls.append(
                ft.Container(
                    content=ft.Text("No hay proyectos participantes para evaluar en este evento.", color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                )
            )

        content_column.visible = True
        safe_update(content_column)

    # Construir Esqueleto
    banner_jurado = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.STAR, color=COLOR_SUCCESS, size=24),
                    ft.Text("Panel de Evaluación del Jurado", size=20, weight=ft.FontWeight.BOLD, color=COLOR_SUCCESS),
                ], spacing=8),
                header_subtitle,
            ],
            spacing=8,
        ),
        bgcolor="#ECFDF5",
        border=ft.Border.all(1, "#A7F3D0"),
        border_radius=12,
        padding=20,
    )

    content_column.controls.extend([
        ft.Row([
            ft.TextButton(
                content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Volver al Evento")]),
                on_click=lambda _: on_back(),
            ),
        ]),
        banner_jurado,
        ft.Container(
            content=ft.Column([
                ft.Text("Equipos a Evaluar", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                participantes_list_container,
            ], spacing=14),
        ),
    ])

    view_container = ft.Container(
        content=ft.Column([loading_ring, content_column], scroll=ft.ScrollMode.AUTO),
        padding=24,
        expand=True,
    )

    view_container.load_data = load_data
    return view_container


def build_evaluar_proyecto_view(api_client, evento_id: int, participante_id: int, page: ft.Page, on_back):
    """
    Construye la vista de calificación de un proyecto con sliders sincronizados y cálculo de puntaje en vivo.
    Replica todas las opciones de eventos/evaluar_proyecto.html.
    """
    loading_ring = ft.ProgressRing(visible=True)
    content_column = ft.Column(spacing=20, visible=False)

    total_score_display = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY)
    max_score_display = ft.Text("/ 0 pts", size=18, color=COLOR_TEXT_MUTED)
    criteria_inputs = {}  # {criterio_id: {"slider": ft.Slider, "input": ft.TextField, "max": int}}
    error_banner = ft.Container(
        content=ft.Text("", color=COLOR_DANGER, size=13),
        bgcolor="#FEE2E2",
        border_radius=8,
        padding=10,
        visible=False,
    )

    def show_snack(text: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(text, color=ft.Colors.WHITE),
            bgcolor=COLOR_DANGER if is_error else COLOR_SUCCESS,
        )
        page.overlay.append(snack)
        snack.open = True
        safe_update(page)

    def calculate_total():
        total = 0
        for cid, ctrl in criteria_inputs.items():
            try:
                val = int(ctrl["input"].value)
            except Exception:
                val = 0
            total += val
        total_score_display.value = str(total)
        safe_update(total_score_display)

    def sync_from_slider(cid, slider_val):
        val = int(round(slider_val))
        ctrl = criteria_inputs[cid]
        ctrl["input"].value = str(val)
        safe_update(ctrl["input"])
        calculate_total()

    def sync_from_input(cid, text_val):
        ctrl = criteria_inputs[cid]
        max_p = ctrl["max"]
        try:
            val = int(text_val)
            if val < 0:
                val = 0
            elif val > max_p:
                val = max_p
        except Exception:
            val = 0
        ctrl["slider"].value = val
        ctrl["input"].value = str(val)
        safe_update(ctrl["slider"])
        safe_update(ctrl["input"])
        calculate_total()

    def handle_save_evaluation(e):
        evaluaciones_payload = []
        for cid, ctrl in criteria_inputs.items():
            try:
                pts = int(ctrl["input"].value)
            except Exception:
                pts = 0
            evaluaciones_payload.append({
                "criterio_id": cid,
                "puntaje": pts,
            })

        save_btn.disabled = True
        loading_ring.visible = True
        safe_update(save_btn)
        safe_update(loading_ring)

        res = api_client.submit_evaluacion(evento_id, participante_id, evaluaciones_payload)

        save_btn.disabled = False
        loading_ring.visible = False
        safe_update(save_btn)
        safe_update(loading_ring)

        if res.get("success"):
            show_snack("Evaluación guardada exitosamente.")
            on_back()
        else:
            err = res.get("error", {})
            msg = err.get("detail") or "Error al guardar la evaluación."
            error_banner.content.value = str(msg)
            error_banner.visible = True
            safe_update(error_banner)

    save_btn = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE, size=18),
            ft.Text("Guardar Evaluación", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ], tight=True),
        style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS),
        height=48,
        on_click=handle_save_evaluation,
    )

    def load_data():
        loading_ring.visible = True
        content_column.visible = False
        safe_update(loading_ring)
        safe_update(content_column)

        res = api_client.get_evaluar_proyecto(evento_id, participante_id)
        loading_ring.visible = False
        safe_update(loading_ring)

        if not res.get("success"):
            show_snack("No se pudo cargar el formulario de evaluación.", is_error=True)
            on_back()
            return

        data = res["data"]
        part = data.get("participante", {})
        criterios = data.get("criterios", [])
        total_max = data.get("total_criterios_score", 0)

        max_score_display.value = f"/ {total_max} pts"
        criteria_inputs.clear()

        # Encabezado del Participante
        part_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.GROUPS, color=COLOR_SUCCESS, size=24),
                        ft.Text("Evaluando al Participante", size=14, weight=ft.FontWeight.BOLD, color=COLOR_SUCCESS),
                    ], spacing=6),
                    ft.Text(part.get("nombre", ""), size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text(part.get("descripcion") or "Sin descripción.", size=13, color=COLOR_TEXT_MUTED),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=14, color=COLOR_PRIMARY),
                        ft.Text(f"Integrantes: {part.get('integrantes')}", size=12, color=COLOR_TEXT_MAIN),
                    ], spacing=6) if part.get("integrantes") else ft.Container(),
                ],
                spacing=6,
            ),
            bgcolor="#ECFDF5",
            border=ft.Border.all(1, "#A7F3D0"),
            border_radius=12,
            padding=20,
        )

        # Filas de Criterios con Sliders
        criterios_controls = []
        initial_total = 0

        for c in criterios:
            cid = c["id"]
            c_nom = c["nombre"]
            c_desc = c.get("descripcion") or "Sin descripción."
            c_max = c.get("puntaje_maximo", 100)
            c_val = c.get("puntaje_actual")
            if c_val is None:
                c_val = 0
            initial_total += c_val

            slider = ft.Slider(
                min=0,
                max=c_max,
                divisions=c_max,
                value=c_val,
                expand=True,
            )
            score_input = ft.TextField(
                value=str(c_val),
                width=80,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
            )

            criteria_inputs[cid] = {
                "slider": slider,
                "input": score_input,
                "max": c_max,
            }

            slider.on_change = lambda e, current_cid=cid: sync_from_slider(current_cid, e.control.value)
            score_input.on_change = lambda e, current_cid=cid: sync_from_input(current_cid, e.control.value)

            row_control = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(c_nom, size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                                ft.Container(
                                    content=ft.Text(f"Máx: {c_max} pts", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                    bgcolor="#F1F5F9",
                                    border_radius=6,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(c_desc, size=12, color=COLOR_TEXT_MUTED),
                        ft.Row(
                            controls=[
                                slider,
                                score_input,
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=6,
                ),
                padding=16,
                bgcolor=COLOR_CARD,
                border=ft.Border.all(1, COLOR_BORDER),
                border_radius=10,
            )
            criterios_controls.append(row_control)

        total_score_display.value = str(initial_total)

        # Caja de Total
        total_box = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Puntaje Total Asignado", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                            ft.Text("Suma de las puntuaciones otorgadas en cada criterio.", size=12, color=COLOR_TEXT_MUTED),
                        ],
                        spacing=2,
                    ),
                    ft.Row(
                        controls=[
                            total_score_display,
                            max_score_display,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                        spacing=6,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="#EFF6FF",
            border=ft.Border.all(1, "#BFDBFE"),
            border_radius=10,
            padding=16,
        )

        content_column.controls.clear()
        content_column.controls.extend([
            ft.Row([
                ft.TextButton(
                    content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Cancelar y Regresar")]),
                    on_click=lambda _: on_back(),
                )
            ]),
            part_card,
            error_banner,
            ft.Text("Criterios de Calificación", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
            ft.Column(controls=criterios_controls, spacing=14),
            total_box,
            ft.Row(
                controls=[
                    ft.OutlinedButton(
                        content=ft.Text("Cancelar"),
                        height=48,
                        on_click=lambda _: on_back(),
                    ),
                    save_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ])

        content_column.visible = True
        safe_update(content_column)

    view_container = ft.Container(
        content=ft.Column([loading_ring, content_column], scroll=ft.ScrollMode.AUTO),
        padding=24,
        expand=True,
    )

    view_container.load_data = load_data
    return view_container
