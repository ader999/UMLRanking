import flet as ft
from ..theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
    COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_GOLD, COLOR_SILVER, COLOR_BRONZE, COLOR_WARNING, COLOR_DANGER, safe_update
)


def build_resultados_view(api_client, evento_id: int, on_back):
    """
    Construye la vista de cuadro de honor, podio y tabla de posiciones.
    Replica todas las opciones de eventos/resultados.html.
    """
    loading_ring = ft.ProgressRing(visible=True)
    content_column = ft.Column(spacing=24, visible=False)

    def load_data():
        loading_ring.visible = True
        content_column.visible = False
        safe_update(loading_ring)
        safe_update(content_column)

        res = api_client.get_resultados(evento_id)
        loading_ring.visible = False
        safe_update(loading_ring)

        if not res.get("success"):
            err = res.get("error", {})
            msg = err.get("detail") or "Los resultados no están disponibles o el evento aún no ha finalizado."
            content_column.controls.clear()
            content_column.controls.extend([
                ft.TextButton(
                    content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Volver al Evento")]),
                    on_click=lambda _: on_back(),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOCK_CLOCK, size=50, color=COLOR_WARNING),
                        ft.Text("Resultados No Disponibles", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                        ft.Text(msg, size=13, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                ),
            ])
            content_column.visible = True
            safe_update(content_column)
            return

        data = res["data"]
        evento = data.get("evento", {})
        criterios = data.get("criterios", [])
        podio = data.get("podio", {})
        resultados = data.get("resultados", [])
        es_previsualizacion = data.get("es_previsualizacion", False)

        content_column.controls.clear()

        # Botón Volver
        content_column.controls.append(
            ft.Row([
                ft.TextButton(
                    content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Volver al Evento")]),
                    on_click=lambda _: on_back(),
                ),
            ])
        )

        # Banner de Previsualización si el evento no ha terminado
        if es_previsualizacion:
            content_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER, color=COLOR_WARNING, size=24),
                        ft.Column([
                            ft.Text("Previsualización de Administrador", weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN, size=14),
                            ft.Text(
                                "Este evento está en curso o programado. Los resultados son preliminares y están ocultos para usuarios generales.",
                                color=COLOR_TEXT_MUTED,
                                size=12,
                            ),
                        ], spacing=2, expand=True),
                    ], spacing=12),
                    bgcolor="#FEF3C7",
                    border=ft.Border.all(1, "#FCD34D"),
                    border_radius=8,
                    padding=14,
                )
            )

        # Título y Trofeo
        content_column.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.EMOJI_EVENTS, size=56, color=COLOR_GOLD),
                    ft.Text("Cuadro de Honor y Resultados", size=26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text(
                        f"Puntuaciones del jurado calculadas para el evento {evento.get('nombre', '')}",
                        size=14,
                        color=COLOR_TEXT_MUTED,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding.symmetric(vertical=10),
            )
        )

        # --------------------------------------------------------------------
        # Podio de Ganadores (1º, 2º, 3º Lugar)
        # --------------------------------------------------------------------
        primero = podio.get("primero")
        segundo = podio.get("segundo")
        tercero = podio.get("tercero")

        def build_podium_card(item, puesto_num, color_metal, icon_metal, label_puesto, is_center=False):
            if not item:
                return ft.Container(width=220)

            p_info = item.get("participante", {})
            score = item.get("puntaje_promedio", 0.0)
            evaluadores = item.get("evaluadores_count", 0)

            card_content = ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon_metal, color=ft.Colors.WHITE, size=24 if not is_center else 28),
                        bgcolor=color_metal,
                        border_radius=25,
                        padding=12 if not is_center else 16,
                    ),
                    ft.Text(
                        p_info.get("nombre", ""),
                        size=16 if not is_center else 18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT_MAIN,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(label_puesto, size=11, weight=ft.FontWeight.BOLD, color=color_metal),
                    ft.Text(f"{score:.2f}", size=28 if not is_center else 34, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY if is_center else COLOR_TEXT_MAIN),
                    ft.Text(f"Promedio de {evaluadores} jurado(s)", size=11, color=COLOR_TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            )

            return ft.Container(
                content=card_content,
                width=240 if not is_center else 270,
                bgcolor=COLOR_CARD,
                border=ft.Border.all(2 if is_center else 1, color_metal if is_center else COLOR_BORDER),
                border_radius=14,
                padding=20,
                shadow=ft.BoxShadow(
                    spread_radius=2 if is_center else 1,
                    blur_radius=12 if is_center else 6,
                    color=ft.Colors.with_opacity(0.1 if is_center else 0.05, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
            )

        if primero:
            podium_row = ft.Row(
                controls=[
                    build_podium_card(segundo, 2, COLOR_SILVER, ft.Icons.MILITARY_TECH, "Segundo Puesto"),
                    build_podium_card(primero, 1, COLOR_GOLD, ft.Icons.WORKSPACE_PREMIUM, "Ganador del Evento", is_center=True),
                    build_podium_card(tercero, 3, COLOR_BRONZE, ft.Icons.MILITARY_TECH, "Tercer Puesto"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=16,
            )
            content_column.controls.append(podium_row)

        # --------------------------------------------------------------------
        # Tabla de Clasificación General
        # --------------------------------------------------------------------
        table_columns = [
            ft.DataColumn(ft.Text("Puesto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Proyecto / Equipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Jurados", weight=ft.FontWeight.BOLD)),
        ]
        for c in criterios:
            table_columns.append(
                ft.DataColumn(
                    ft.Column([
                        ft.Text(c["nombre"][:15], weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(f"Máx: {c['puntaje_maximo']}p", size=10, color=COLOR_TEXT_MUTED),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )
        table_columns.append(
            ft.DataColumn(ft.Text("Puntaje Final", weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY))
        )

        table_rows = []
        for r in resultados:
            p_obj = r.get("participante", {})
            puesto = r.get("puesto", 1)
            score_final = r.get("puntaje_promedio", 0.0)
            desglose = r.get("desglose_criterios", {})

            # Icono de puesto
            if puesto == 1:
                puesto_cell = ft.Row([ft.Icon(ft.Icons.EMOJI_EVENTS, color=COLOR_GOLD, size=16), ft.Text("1", weight=ft.FontWeight.BOLD, color=COLOR_GOLD)])
            elif puesto == 2:
                puesto_cell = ft.Row([ft.Icon(ft.Icons.MILITARY_TECH, color=COLOR_SILVER, size=16), ft.Text("2", weight=ft.FontWeight.BOLD, color=COLOR_SILVER)])
            elif puesto == 3:
                puesto_cell = ft.Row([ft.Icon(ft.Icons.MILITARY_TECH, color=COLOR_BRONZE, size=16), ft.Text("3", weight=ft.FontWeight.BOLD, color=COLOR_BRONZE)])
            else:
                puesto_cell = ft.Text(str(puesto), weight=ft.FontWeight.BOLD)

            row_cells = [
                ft.DataCell(puesto_cell),
                ft.DataCell(
                    ft.Column([
                        ft.Text(p_obj.get("nombre", ""), weight=ft.FontWeight.BOLD, size=13),
                        ft.Text(p_obj.get("integrantes") or "", size=11, color=COLOR_TEXT_MUTED),
                    ], spacing=2)
                ),
                ft.DataCell(ft.Text(str(r.get("evaluadores_count", 0)), text_align=ft.TextAlign.CENTER)),
            ]

            for c in criterios:
                c_score = desglose.get(str(c["id"])) or desglose.get(c["id"]) or 0.0
                row_cells.append(
                    ft.DataCell(ft.Text(f"{c_score:.1f}", text_align=ft.TextAlign.CENTER))
                )

            row_cells.append(
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            f"{score_final:.2f} pts",
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_PRIMARY,
                            size=14,
                        ),
                        bgcolor=COLOR_PRIMARY_LIGHT,
                        border_radius=6,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    )
                )
            )

            table_rows.append(ft.DataRow(cells=row_cells))

        tabla_container = ft.Container(
            content=ft.Column([
                ft.Text("Tabla de Clasificación General", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                ft.DataTable(
                    columns=table_columns,
                    rows=table_rows,
                    heading_row_color="#F8FAFC",
                    border=ft.Border.all(1, COLOR_BORDER),
                    border_radius=8,
                    vertical_lines=ft.BorderSide(1, "#F1F5F9"),
                ),
            ], spacing=12),
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=20,
        )

        content_column.controls.append(tabla_container)
        content_column.visible = True
        safe_update(content_column)

    view_container = ft.Container(
        content=ft.Column([loading_ring, content_column], scroll=ft.ScrollMode.AUTO),
        padding=24,
        expand=True,
    )

    view_container.load_data = load_data
    return view_container
