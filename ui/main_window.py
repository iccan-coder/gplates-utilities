from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from core.session import Session
from ui.feature_collection_loader import FeatureCollectionLoader
from util.project_storage import load_project, save_project


class MainWindow(QMainWindow):
    def __init__(self, session: Session):
        super().__init__()

        self.session = session

        self.setWindowTitle("GPlates Utilities")

        # Widgets and Sub-Windows
        # TODO: Add these
        self.feature_collection_manager = FeatureCollectionLoader(session)

        # File Menu Items
        file_menu = self.menuBar().addMenu("File")

        load_project_action = file_menu.addAction("Open Project")
        load_project_action.triggered.connect(self.open_project)
        save_project_action = file_menu.addAction("Save Project")
        save_project_action.triggered.connect(self.save_project)

        file_menu.addSeparator()

        manage_feature_collection_action = file_menu.addAction("Manage Feature Collections")
        manage_feature_collection_action.triggered.connect(self.feature_collection_manager.show)
        load_feature_collection_action = file_menu.addAction("Open Feature Collection(s)")
        load_feature_collection_action.triggered.connect(self.open_feature_collections)
        load_rotation_model_action = file_menu.addAction("Open Rotation Model")
        load_rotation_model_action.triggered.connect(self.open_rotation_model)

        file_menu.addSeparator()

        reload_action = file_menu.addAction("Reload files")
        reload_action.triggered.connect(self.open_rotation_model)

        # Set initial "view"
        # TODO: self.setCentralWidget(???)
    
    @Slot()
    def open_project(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Project", ".", "JavaScript Object Notation (*.json)")
        if not file_name:
            return
        if not load_project(self.session, file_name):
            QMessageBox.critical(self, "Error", "Error occured loading project file.")
    
    @Slot()
    def save_project(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Project", ".", "JavaScript Object Notation (*.json)")
        if not file_name:
            return
        if not save_project(self.session, file_name):
            QMessageBox.critical(self, "Error", "Error occured loading project file.")
    
    @Slot()
    def open_feature_collections(self):
        fc_filepaths, _ = QFileDialog.getOpenFileNames(self, "Open Feature Collection(s)", ".", "GPlates Markup Language (*.gpml)")
        if len(fc_filepaths) == 0:
            return

        self.session.load_feature_collections(fc_filepaths)
    
    @Slot()
    def open_rotation_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Rotation Model", ".", "PLATES4 rotation (*.rot)")
        if file_name:
            self.session.load_rotation_model(file_name)
    
    @Slot()
    def reload_files(self):
        self.session.reload_features()
        self.session.reload_rotation_model()