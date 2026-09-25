import flet as ft
from ..theme import (
    COLOR_PRIMARY, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED, safe_update
)
from ..components.event_card import create_event_card


def build_eventos_view(api_client, on_navigate, on_view_event, on_evaluate_event, on_results_event):
    """
    Construye la vista principal con lista y clasificación de eventos.
    Replica todas las opciones de eventos/lista.html.
    """
    current_status_filter = [None]  # None = todos, 'activos', 'proximos', 'finalizados'
    events_data = []

    cards_grid = ft.Row(
        controls=[],
        wrap=True,
        spacing=20,
        run_spacing=20,
        alignment=ft.MainAxisAlignment.START,
    )

    empty_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=60, color=ft.Colors.GREY_400),
                ft.Text("No se encontraron eventos", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                ft.Text("No hay eventos que coincidan con el filtro seleccionado.", size=13, color=COLOR_TEXT_MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.Alignment(0, 0),
        padding=40,
        visible=False,
    )

    loading_indicator = ft.ProgressRing(visible=False)

    search_field = ft.TextField(
        hint_text="Buscar evento por nombre o descripción...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=8,
        dense=True,
        expand=True,
    )

    # Botones de filtro por estado
    btn_todos = ft.OutlinedButton(
        content=ft.Text("Todos"),
        style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
    )
    btn_activos = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.PLAY_CIRCLE, size=15, color=COLOR_SUCCESS), ft.Text("Activos")]),
    )
    btn_proximos = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME, size=15, color=COLOR_WARNING), ft.Text("Próximos")]),
    )
    btn_finalizados = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, size=15, color=COLOR_MUTED), ft.Text("Finalizados")]),
    )

    filter_buttons = [
        (btn_todos, None),
        (btn_activos, "activos"),
        (btn_proximos, "proximos"),
        (btn_finalizados, "finalizados"),
    ]

    def update_filter_styles(active_val):
        for btn, val in filter_buttons:
            if val == active_val:
                btn.style = ft.ButtonStyle(bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE)
            else:
                btn.style = ft.ButtonStyle(bgcolor=ft.Colors.TRANSPARENT, color=COLOR_TEXT_MAIN)
            safe_update(btn)

    def render_cards():
        search_query = search_field.value.lower().strip() if search_field.value else ""
        filtered = []

        for ev in events_data:
            # Filtro por estado
            status_f = current_status_filter[0]
            if status_f == "activos" and not ev.get("esta_activo"):
                continue
            if status_f == "proximos" and (ev.get("esta_activo") or ev.get("ha_finalizado")):
                continue
            if status_f == "finalizados" and not ev.get("ha_finalizado"):
                continue

            # Filtro de búsqueda
            nombre = (ev.get("nombre") or "").lower()
            desc = (ev.get("descripcion") or "").lower()
            if search_query and (search_query not in nombre and search_query not in desc):
                continue

            filtered.append(ev)

        cards_grid.controls.clear()
        if filtered:
            empty_container.visible = False
            for ev in filtered:
                card = create_event_card(
                    ev,
                    on_view_details=on_view_event,
                    on_evaluate=on_evaluate_event,
                    on_view_results=on_results_event,
                )
                cards_grid.controls.append(card)
        else:
            empty_container.visible = True

        safe_update(cards_grid)
        safe_update(empty_container)

    def load_events():
        loading_indicator.visible = True
        safe_update(loading_indicator)

        raw_events = api_client.get_eventos()
        events_data.clear()
        events_data.extend(raw_events)

        # Actualizar contadores en los botones
        c_activos = sum(1 for e in raw_events if e.get("esta_activo"))
        c_proximos = sum(1 for e in raw_events if not e.get("esta_activo") and not e.get("ha_finalizado"))
        c_finalizados = sum(1 for e in raw_events if e.get("ha_finalizado"))
        c_todos = len(raw_events)

        btn_todos.content.value = f"Todos ({c_todos})"
        btn_activos.content.controls[1].value = f"Activos ({c_activos})"
        btn_proximos.content.controls[1].value = f"Próximos ({c_proximos})"
        btn_finalizados.content.controls[1].value = f"Finalizados ({c_finalizados})"

        loading_indicator.visible = False
        safe_update(loading_indicator)
        render_cards()

    def set_filter(val):
        current_status_filter[0] = val
        update_filter_styles(val)
        render_cards()

    btn_todos.on_click = lambda _: set_filter(None)
    btn_activos.on_click = lambda _: set_filter("activos")
    btn_proximos.on_click = lambda _: set_filter("proximos")
    btn_finalizados.on_click = lambda _: set_filter("finalizados")

    search_field.on_change = lambda _: render_cards()

    # Encabezado Banner
    banner = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.EMOJI_EVENTS, size=28, color=COLOR_PRIMARY),
                                ft.Text("UMLRanking", size=26, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                            ],
                            spacing=8,
                        ),
                        ft.Text(
                            "Crea eventos, gestiona jurados y evalúa proyectos o equipos académicos con criterios personalizados.",
                            size=13,
                            color=COLOR_TEXT_MUTED,
                        ),
                    ],
                    expand=True,
                    spacing=4,
                ),
                ft.FilledButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ADD_CIRCLE, size=18, color=ft.Colors.WHITE),
                            ft.Text("Crear Nuevo Evento", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        tight=True,
                    ),
                    style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
                    height=44,
                    on_click=lambda _: on_navigate("crear_evento"),
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Recargar eventos",
                    on_click=lambda _: load_events(),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=12,
        padding=20,
        margin=ft.Padding.only(bottom=16),
    )

    # Barra de Búsqueda y Filtros
    filter_bar = ft.Container(
        content=ft.Row(
            controls=[
                search_field,
                btn_todos,
                btn_activos,
                btn_proximos,
                btn_finalizados,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        margin=ft.Padding.only(bottom=20),
    )

    view_container = ft.Container(
        content=ft.Column(
            controls=[
                banner,
                filter_bar,
                loading_indicator,
                cards_grid,
                empty_container,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=24,
        expand=True,
    )

    view_container.load_data = load_events
    return view_container
