import os
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.uix.screenmanager import MDScreenManager

# class MainView(MDScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.name = "MainView"

#! THIS IS JUST A TEST

class ViewManager:
    
    views = {}
    selected_view = None
    
    def __init__(self, views_dir="views"):
        self.views_dir = views_dir
        # self.load_views()
        
    def set(self, view):
        
        for file in os.listdir(self.views_dir):
            
            if file.endswith(".kv"):
                
                # Gets view name and its path
                view = os.path.splitext(file)[0]

                # Crea dinamicamente una classe per la vista
                view_class = type(view, (MDScreen,), {"name": view})
                self.views[view] = view_class

    def load_views(self):
        
        for file in os.listdir(self.views_dir):
            
            if file.endswith(".kv"):
                
                # Gets view name and its path
                view = os.path.splitext(file)[0]
                view_path = os.path.join(self.views_dir, file)

                # Ricarica il file .kv
                # Builder.unload_file(view_path)
                # Builder.load_file(view_path)

                # Crea dinamicamente una classe per la vista
                view_class = type(view, (MDScreen,), {"name": view})
                self.views[view] = view_class

    def select(self, view):
        if view in self.views:
            self.selected_view = self.views[view]()
        else:
            raise ValueError(f"View '{view}' non trovata.")