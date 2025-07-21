from PySide6 import QtWidgets
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from core.session import Session
from ui.feature_collection_loader import FeatureCollectionLoader
from ui.feature_splitting_window import FeatureSplittingWindow
from ui.line_splitting_window import LineSplitterWindow
from util.project_storage import load_project, save_project


class MainWindow(QMainWindow):
    def __init__(self, session: Session):
        super().__init__()

        self.session = session

        self.setWindowTitle("GPlates Utilities")

        # Widgets and Sub-Windows
        self.feature_collection_manager = FeatureCollectionLoader(session)
        # NOTE: There must be a way to store the central widgets instead of re-initializing them.

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
        reload_action.triggered.connect(self.reload_files)


        # Icons
        feature_split_icon = QIcon("./media/icons/plate_split_256.png")
        line_split_icon = QIcon("./media/icons/line_split_256.png")

        # Toolbars
        views_toolbar = self.addToolBar("Views")
        views_toolbar.setIconSize(QSize(32, 32))
        split_plates_action = views_toolbar.addAction(feature_split_icon, "Split Plates")
        split_plates_action.triggered.connect(self.show_feature_split_view)
        cheese_action = views_toolbar.addAction(line_split_icon, "Split Lines")
        cheese_action.triggered.connect(self.show_line_split_view)
        
        action_group = QActionGroup(self)
        action_group.addAction(split_plates_action)
        action_group.addAction(cheese_action)
        action_group.setExclusive(True)

        # Set initial "view"
        self.show_feature_split_view()
    
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
    
    @Slot()
    def show_feature_split_view(self):
        # TODO: clear any still opened windows
        self.resize(950, 400)
        self.setCentralWidget(FeatureSplittingWindow(self.session))
    
    @Slot()
    def show_line_split_view(self):
        # TODO: clear any still opened windows
        self.resize(400, 400)
        self.setCentralWidget(LineSplitterWindow(self.session))