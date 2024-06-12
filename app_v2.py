import flet as ft


class MainApp(ft.Column):
    # application's root control is a Column containing all other controls
    def __init__(self):
        super().__init__()
        self.title = ft.Text("Detector", theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM)

        self.filter = ft.Tabs(
            tab_alignment="CENTER",
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="Images"), 
                  ft.Tab(text="Videos"), 
                  ft.Tab(text="RTSP")],
        )
        self.width = 600

        self.controls = [
            ft.Row(
                controls=[
                    self.title,
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter,
                ],
            ),
        ]

    # def add_clicked(self, e):
    #     task = Task(self.new_task.value, self.task_status_change, self.task_delete)
    #     self.tasks.controls.append(task)
    #     self.new_task.value = ""
    #     self.update()

    # def task_status_change(self):
    #     self.update()

    # def task_delete(self, task):
    #     self.tasks.controls.remove(task)
    #     self.update()

    # def before_update(self):
    #     status = self.filter.tabs[self.filter.selected_index].text
    #     for task in self.tasks.controls:
    #         task.visible = (
    #             status == "all"
    #             or (status == "active" and task.completed == False)
    #             or (status == "completed" and task.completed)
    #         )

    def tabs_changed(self, e):
        self.update()


def main(page: ft.Page):
    page.title = "To-Do App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    # create application instance
    app = MainApp()

    # add application's root control to the page
    page.add(app)


ft.app(target=main)