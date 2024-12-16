import os
from kivy.lang import Builder
from kivymd.tools.hotreload.app import MDApp
from kivy.core.window import Window
from kivy.animation import Animation
from googleapiclient.discovery import build
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import Widget
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemLeadingIcon,
    MDListItemLeadingAvatar,
    MDListItemTrailingIcon,
    MDListItemTrailingCheckbox
)
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivymd.uix.fitimage import FitImage
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

# from widgets import Dialog_yt_api_key

from downloader import Downloader
from settings import SettingsManager

class MainView(MDScreenManager):
    pass

class MainApp(MDApp):

    DEBUG = True
    KV_DIRS=[ os.path.join(os.getcwd(), "views") ]
    dialog = None

    sm = None
    yt = None
    settings = None
    file_manager = None
    selected_items = []

    def __init__(self, *args):
        super(MainApp, self).__init__(*args)
        # settings = contains settings + methods to access & edit them
        self.settings = SettingsManager()
        # sownloader = manages all search-/download-related operations
        self.yt = Downloader()
        # GUI
        self.screen = Builder.load_file("views/main.kv") #! Could also bee self.root = ...
        # Instanciates a new ViewManager + changes selected_view to MainView
        # self.vm = ViewManager(views_dir="views")
        # self.vm.select("main")

    def build_app(self):
        self.title = "YouTubeDownloader"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Window.bind(on_resize=self.on_resize)
        Window.minimum_width = 640
        Window.minimum_height = 480
        # _ = MainView()
        # _.add_widget(self.screen)
        # self.sm =
        # self.sm.add_widget(MDScreen().add_widget(self.root))
        self.update_orientation()
        return self.screen

    def on_resize(self, *args):
        self.update_orientation()

    def update_orientation(self):
        # horizontal
        if Window.width > Window.height:
            self.screen.ids.blt_results.size_hint_x = 0.65
            self.screen.ids.blt_results.size_hint_y = 1
            self.screen.ids.blt_selected.size_hint_x = 0.35
            self.screen.ids.blt_selected.size_hint_y = 1
        # vertical
        else:
            self.screen.ids.blt_results.size_hint_x = 1
            self.screen.ids.blt_results.size_hint_y = 0.65
            self.screen.ids.blt_selected.size_hint_x = 1
            self.screen.ids.blt_selected.size_hint_y = 0.35

    def select(self, view):
        self.screen = Builder.load_file(f"views/{view}.kv")

    def open_settings_menu(self):
        settings = [
            {
                "text": "Edit YouTube API key",
                "on_release": lambda: self.select_setting(self.show_dialog, {"dialog_name": "Dialog_yt_api_key", "dialog_title": "Edit YouTube API key"}), #? Add ids array 'dialog_ids'?
            },
            # {
            #     "text": "Confirm each download",
            #     "on_release": lambda: self.select_setting(self.show_dialog, {"dialog_name": "", "dialog_title": "Confirm options before each download"}),
            # },
            {
                "text": "Select download path",
                "on_release": lambda: self.select_setting(self.open_file_manager, os.getenv("DEFAULT_DOWNLOAD_PATH") if os.getenv("DEFAULT_DOWNLOAD_PATH") else os.path.expanduser("~")),
            },
            {
                "text": "Import",
                "on_release": lambda: self.select_setting(self.open_file_manager, os.path.expanduser("~")),
            },
            #...
        ]
        self.menu = MDDropdownMenu(caller=self.screen.ids.btn_menu_settings, items=settings)
        self.menu.open()

    def select_setting(self, func, params=None):
        # Executes passed func with eventual params (dict)
        if params:
            func(params)
        else:
            func()
        # Closes menu
        self.menu.dismiss()
        self.menu = None

    def open_format_menu(self):
        formats = [{ "text": format, "on_release": lambda x=format: self.select_format(x) } for format in self.yt.formats]
        self.menu = MDDropdownMenu(caller=self.screen.ids.btn_menu_format, items=formats) # width_mult=4, = dimensione del menu
        self.menu.open()

    def select_format(self, format):
        # Sets option in .env
        self.settings.set_env("FORMAT", format)
        self.settings.set_env("DOWNLOAD_FORMAT", format)
        # Updates option in downloader
        self.yt.format = format
        # Sets format as menu text
        self.screen.ids.btn_menu_format.children[0].text = format
        # Closes menu
        self.menu.dismiss()
        self.menu = None

    def open_quality_menu(self):
        qualities = [
            {
                "text": f"{i+1}",
                "on_release": lambda x=i+1: self.select_quality(x),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(caller=self.screen.ids.btn_menu_quality, items=qualities)
        self.menu.open()

    def select_quality(self, quality):
        # Sets option in .env
        self.settings.set_env("DOWNLOAD_QUALITY", quality)
        # Updates option in downloader
        self.yt.quality = quality
        # Sets quality as menu text
        self.screen.ids.btn_menu_quality.children[0].text = str(quality)
        # Closes menu
        self.menu.dismiss()
        self.menu = None

    def set_split_chapters(self, active):
        self.yt.split_chapters = active
        #! MDButton management:
        # Set split chapters true if false & vice-versa
        # if self.yt.split_chapters is False:
        #     self.yt.split_chapters = True
        # else:
        #     self.yt.split_chapters = False

    # self.settings.edit_youtube_api_key
    def show_dialog(self, params):

        # Gets dialog name (if None returns)
        # dialog_name = params.get("dialog_name", None)
        # if dialog_name is None:
        #     return

        # Closes currently opened dialog (if there's any opened)
        if self.dialog is not None:
            self.close_dialog()

        # Creates the dialog #! DOESN'T WORK IN .kv FILE
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=params.get("dialog_title", "Dialog"),
            ),
            MDDialogContentContainer(
                # eval(dialog_name) if dialog_name is not None else ... #! Should be like this but doesn't work
                # Dialog_yt_api_key(), #! Doesn't work
                MDTextField(
                    id="tf_yt_api_key",
                    text=os.getenv("YT_API_KEY"),
                    hint_text="YouTube API key",
                    mode="outlined",
                    size_hint_x=1,
                    multiline=False
                ),
                orientation="vertical"
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Annulla"),
                    style="text",
                    on_release=lambda x: self.close_dialog()
                ),
                MDButton(
                    MDButtonText(text="Salva"),
                    style="text",
                    on_release=lambda x: self.close_dialog(self.settings.set_env, ["YT_API_KEY", self.dialog.get_ids().tf_yt_api_key.text])
                ),
            )
        )
        self.dialog.open()

    # Calls a func (if !None) with params (if !None) + closes the dialog
    def close_dialog(self, func=None, params=None):

        # If there's a dialog + a func is defined + dialog has
        if self.dialog and func:
            if params:
                func(*params)
                self.yt.rebuild_yt_api()
            else:
                func()

        # Closes the dialog
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def open_file_manager(self, path):

        # Closes the file_manager (if it's open)
        self.close_file_manager()

        # Inits & shows file manager
        self.file_manager = MDFileManager(select_path=self.select_path, exit_manager=self.close_file_manager)
        self.file_manager.show(path)

    def select_path(self, path: str):

        # Closes the file_manager
        self.close_file_manager()

        _ = path if path is not None else os.path.expanduser("~")

        # Sets the path in .env & yt
        self.settings.set_env("DEFAULT_DOWNLOAD_PATH", _)
        self.yt.default_download_path = _

        # Displays a snackbar popup
        MDSnackbar(
            MDSnackbarText(
                text="Selected download path: " + path,
            ),
            y="24dp",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()

    def close_file_manager(self, *args):
        # Closes the file_manager (if not None)
        if self.file_manager is not None:
            self.file_manager.close()
            self.file_manager = None

    def search(self, query):

        # Error popup if no search term
        if not query.strip():
            MDSnackbar(
                MDSnackbarText(
                    text="Insert a search term or a URL",
                    pos_hint={"center_x": 0.5},
                ),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=None,
                width="260dp"
            ).open()
            return

        # Clears videos from UI
        self.screen.ids.list_results.clear_widgets()

        # Search video
        results = self.yt.search(query)

        # Adds items
        for item in results:
            self.screen.ids.list_results.add_widget(
                MDGridLayout(
                    FitImage(
                        id="result_img",
                        source=item["thumbnail"],
                        fit_mode="contain",
                        size_hint_x=None,
                        width="160dp"
                    ),
                    MDBoxLayout(
                        MDLabel(
                            id="result_title",
                            text=item["title"],
                            theme_text_color="Custom",
                            text_color=[1,1,1,1],
                            font_style="Title",
                            role="medium",
                            bold=True,
                            allow_selection=False,
                            allow_copy=False,
                            shorten=True,
                            shorten_from="right",
                            size_hint_y=None,
                            height="25dp",
                        ),
                        MDLabel(
                            id="result_channel",
                            text=item["channel"],
                            theme_text_color="Custom",
                            text_color=[1,1,1,0.6],
                            font_style="Label",
                            role="medium",
                            allow_selection=False,
                            allow_copy=False,
                            shorten=True,
                            shorten_from="right",
                            size_hint_y=None,
                            height="25dp",
                        ),
                        orientation='vertical',
                        size_hint_x=.8,
                        size_hint_y=1,
                        padding=["8dp", "20dp"],
                    ),
                    MDAnchorLayout(
                        MDIconButton(
                            id="result_icon",
                            icon="checkbox-marked" if next((x for x in self.selected_items if x["id"] == item["id"]), None) else "checkbox-blank-outline",
                            style="standard",
                            on_release=lambda x, item=item: self.handle_video_check(x, "select" if x.icon == "checkbox-blank-outline" else "deselect", item)
                        ),
                        size_hint_y=1,
                        size_hint_x=None,
                        width="80dp",
                        anchor_x='center',
                        anchor_y='center',
                        # pos_hint={"center_x": .5, "center_y": .5},
                    ),
                    id=item["id"],
                    md_bg_color=[0.25, 0.25, 0.25, 1],
                    rows=1,
                    cols=3,
                    size_hint_x=1,
                    size_hint_y=None,
                    height="90dp",
                )
            )

    def handle_video_check(self, btn, action, item):
        # Select video in list_results
        if action == "select":
            btn.icon = "checkbox-marked"
            self.select_item(item)
        # Deselect video in list_results + remove from list_selected
        else:
            # Changes icon if clicked btn is in list_results
            if btn.icon == "checkbox-marked": 
                btn.icon = "checkbox-blank-outline"
            else:
                item_to_deselect = next((x for x in self.screen.ids.list_results.children if x.id == item["id"]), None)
                if item_to_deselect is not None:
                    item_to_deselect.children[0].children[0].icon = "checkbox-blank-outline"
            self.deselect_item(item)

    def select_item(self, item):
        selected_item = MDGridLayout(
            MDBoxLayout(
                MDLabel(
                    id="selected_title",
                    text=item["title"],
                    theme_text_color="Custom",
                    text_color=[1,1,1,1],
                    font_style="Label",
                    role="medium",
                    bold=True,
                    allow_selection=False,
                    allow_copy=False,
                    shorten=True,
                    shorten_from="right",
                    size_hint_y=None,
                    height="25dp",
                ),
                orientation='vertical',
                size_hint_x=.8,
                size_hint_y=1,
                padding=["8dp", "20dp"],
            ),
            MDAnchorLayout(
                MDIconButton(
                    id="result_icon",
                    icon="close",
                    style="standard",
                    on_release=lambda x, item=item: self.handle_video_check(x, "remove", item)
                ),
                size_hint_y=1,
                size_hint_x=None,
                width="80dp",
                anchor_x='center',
                anchor_y='center',
                # pos_hint={"center_x": .5, "center_y": .5},
            ),
            id=item["id"],
            md_bg_color=[0.18, 0.18, 0.18, 1],
            rows=1,
            cols=3,
            size_hint_x=1,
            size_hint_y=None,
            height="70dp",
        )
        self.screen.ids.list_selected.add_widget(selected_item)
        # Adds item id to list
        self.selected_items.append(item)

    def deselect_item(self, item):
        # Removes item from list_selected
        widget_to_remove = next((x for x in self.screen.ids.list_selected.children if x.id == item["id"]), None)
        if widget_to_remove is not None:
            self.screen.ids.list_selected.remove_widget(widget_to_remove)
        # Removes item from selected_items
        item_to_remove = next((x for x in self.selected_items if x["id"] == item["id"]), None)
        if item_to_remove is not None:
            self.selected_items.remove(item_to_remove)

    def download(self):
        # Downloads items
        self.yt.download(self.selected_items)
        # Clears selected list
        self.selected_items = []
        # Clears list_selected + set deselected boxes to list_results
        self.screen.ids.list_selected.clear_widgets()
        for widget in self.screen.ids.list_results.children:
            widget.children[0].children[0].icon = "checkbox-blank-outline"

if __name__ == '__main__':
    MainApp().run()

"""
info = {
    "Name": [
        os.name,
        (
            "microsoft"
            if os.name == "nt"
            else ("linux" if os.uname()[0] != "Darwin" else "apple")
        ),
    ],
    "Architecture": [os.uname().machine, "memory"],
    "Hostname": [os.uname().nodename, "account"],
    "Python Version": ["v" + sys.version, "language-python"],
    "Kivy Version": ["v" + kv__version__, "alpha-k-circle-outline"],
    "KivyMD Version": ["v" + __version__, "material-design"],
    "MaterialYouColor Version": ["v" + mc__version__, "invert-colors"],
    "Pillow Version": ["Unknown", "image"],
    "Working Directory": [os.getcwd(), "folder"],
    "Home Directory": [os.path.expanduser("~"), "folder-account"],
    "Environment Variables": [os.environ, "code-json"],
}
"""