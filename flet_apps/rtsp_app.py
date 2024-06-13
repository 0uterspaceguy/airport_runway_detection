import flet as ft


class RtspApp(ft.Column):
    def __init__(self):
        super().__init__()

        self.title = ft.Text("Детекция на rtsp потоке", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)

        self.controls = [
            ft.Row(
                controls=[
                    self.title,
                ],
            ),]
