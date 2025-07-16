from os import path
from PySide6.QtCore import QLocale, QObject, QSortFilterProxyModel
from PySide6.QtGui import QDoubleValidator, QRegularExpressionValidator, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QStyledItemDelegate, QTreeView, QVBoxLayout, QWidget
import pygplates

from core.plate_splitter import split_plate_by_line
from core.session import Session
from ui.feature_collection_loader import FeatureCollectionLoader


class RiftFilterModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._time_filter: float = float("inf")
    
    def filterAcceptsRow(self, row_num: int, _) -> bool:
        # Get the underlying model
        model: QStandardItemModel = self.sourceModel()  # type: ignore | We know what data we are dealing with
        
        geo_type = model.item(row_num, 2).text()
        feature_type = model.item(row_num, 1).text()
        start_time = float(model.item(row_num, 4).text())
        end_time = float(model.item(row_num, 5).text())
        
        return geo_type == "PolylineOnSphere" and feature_type in ["ContinentalRift", "SubductionZone"] and (start_time >= self._time_filter >= end_time)
    
    def setTimeFilter(self, time: float):
        self.beginFilterChange()
        self._time_filter = time
        self.invalidateFilter()

class FeatureFilterModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._time_filter: float = float("inf")
        self._accepted_ids: list[str] = []
    
    def filterAcceptsRow(self, row_num: int, _) -> bool:
        # Get the underlying model
        model: QStandardItemModel = self.sourceModel()  # type: ignore | We know what data we are dealing with
        
        geo_type = model.item(row_num, 2).text()
        plateId = model.item(row_num, 3).text()
        start_time = float(model.item(row_num, 4).text())
        end_time = float(model.item(row_num, 5).text())

        return geo_type == "PolygonOnSphere" and (len(self._accepted_ids) == 0 or plateId in self._accepted_ids) and (start_time >= self._time_filter >= end_time)
    
    def setTimeFilter(self, time: float):
        self.beginFilterChange()
        self._time_filter = time
        self.invalidateFilter()
    
    def setPlateIdFilter(self, ids: list[str]):
        self.beginFilterChange()
        self._accepted_ids = ids
        self.invalidateFilter()

class TimeDecoratorDelegate(QStyledItemDelegate):
    def __init__(self, /, parent: QObject | None) -> None:
        super().__init__(parent)
    
    def displayText(self, value: str, locale: QLocale) -> str:
        if value == "-inf":
            return "Distant Future"
        elif value == "inf":
            return "Distant Past"
        
        return value

class FeatureSplittingWindow(QWidget):
    def __init__(self, session: Session):
        super().__init__()

        self.session = session

        self.rift_model = RiftFilterModel()
        self.rift_model.setSourceModel(session.get_feature_model())

        self.feature_model = FeatureFilterModel()
        self.feature_model.setSourceModel(session.get_feature_model())
        
        self.setWindowTitle("Plate Splitting Tool")
        self.resize(900, 400)
        
        self.debugwindow = FeatureCollectionLoader(self.session)

        split_date_label = QLabel("Split Time:")
        self.split_date = QLineEdit()
        self.split_date.setValidator(QDoubleValidator())
        self.split_date.editingFinished.connect(self.updateSplitTime)

        plate_id_label = QLabel("Plate ID(s):")
        self.plate_filter = QLineEdit()
        self.plate_filter.setValidator(QRegularExpressionValidator("\\d+(,\\d*)*"))
        self.plate_filter.editingFinished.connect(self.updatePlateFilter)
        
        self.rift_selection = QComboBox()
        self.rift_selection.setModel(self.rift_model)
        self.rift_selection.setModelColumn(0)
        self.rift_selection.setPlaceholderText("[Load Feature Collections to select Rift]")

        self.new_feature_view = QTreeView()
        self.new_feature_view.setModel(self.feature_model)
        self.new_feature_view.setColumnHidden(2, True)
        self.new_feature_view.setItemDelegateForColumn(4, TimeDecoratorDelegate(self.new_feature_view))
        self.new_feature_view.setItemDelegateForColumn(5, TimeDecoratorDelegate(self.new_feature_view))
        self.new_feature_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.new_feature_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.new_feature_view.setStyleSheet(
            """
            QTreeView::branch  {
                background: palette(base);
            }

            QTreeView::branch:selected {
                background-color: rgb(34, 177, 76);
            }
            """)    # Sets 
        

        

        button_1 = QPushButton("Manage Feature Collections")
        button_1.clicked.connect(self.load_feature_collection)


        button_reload_fcs = QPushButton("Reload Feature Collections")
        button_reload_fcs.clicked.connect(self.session.reload_features)

        button_rotation_model = QPushButton("Load Rotation Model")
        button_rotation_model.clicked.connect(self.load_rotation_model)

        button_rotation_reload = QPushButton("Reload Rotation Model")
        button_rotation_reload.clicked.connect(self.session.reload_rotation_model)

        button_2 = QPushButton("Set Save Location")
        button_2.clicked.connect(self.set_save_location)
        self._save_location: str = ""

        split_button = QPushButton("Split")
        split_button.clicked.connect(self.on_split)

        split_date_layout = QHBoxLayout()
        split_date_layout.addWidget(split_date_label, 0)
        split_date_layout.addWidget(self.split_date, 1)

        plate_filter_layout = QHBoxLayout()
        plate_filter_layout.addWidget(plate_id_label, 0)
        plate_filter_layout.addWidget(self.plate_filter, 1)

        side_layout = QVBoxLayout()
        side_layout.addLayout(split_date_layout)
        side_layout.addLayout(plate_filter_layout)
        side_layout.addWidget(self.rift_selection)
        side_layout.addWidget(button_1, 0)
        side_layout.addWidget(button_reload_fcs, 0)
        side_layout.addWidget(button_rotation_model, 0)
        side_layout.addWidget(button_rotation_reload, 0)
        side_layout.addWidget(QWidget(), 1)
        side_layout.addWidget(button_2, 0)
        side_layout.addWidget(split_button, 0)
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.new_feature_view, 1)
        main_layout.addLayout(side_layout, 0)

        self.setLayout(main_layout)
    
    def load_feature_collection(self):
        self.debugwindow.show()
    
    def load_rotation_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Rotation Model", ".", "PLATES4 rotation (*.rot)")
        if file_name:
            self.session.load_rotation_model(file_name)
    
    def set_save_location(self):
        self._save_location, _ = QFileDialog.getSaveFileName(self, "Set Resulting Feature Collection", ".", "GPlates Markup Language (*.gpml)")

    def updateSplitTime(self):
        time = float(self.split_date.text())
        self.rift_model.setTimeFilter(time)
        self.feature_model.setTimeFilter(time)
    
    def updatePlateFilter(self):
        filter_text = self.plate_filter.text()
        if filter_text == "":
            self.feature_model.setPlateIdFilter([])
        self.feature_model.setPlateIdFilter([id for id in filter_text.split(",") if len(id) > 0])

    def on_split(self):
        if self.rift_selection.currentIndex() < 0:
            QMessageBox.critical(self, "Error", "No rift selected!")
            return
        
        rift_idx = self.rift_model.index(self.rift_selection.currentIndex(), 6)
        all_features = [f for lfc in self.session.loaded_feature_collections for f in lfc.feature_collection]
        selected_rift = next(filter(lambda f: f.get_feature_id().get_string() == self.rift_model.itemData(rift_idx)[0], all_features))
        
        if self.split_date.text() == "":
            QMessageBox.critical(self, "Error", "No rifting time set!")
            return

        split_date = float(self.split_date.text())

        if selected_rift == None:
            QMessageBox.critical(self, "Error", "No rift selected!")
            return
        
        
        selected_feature_ids = [i.data() for i in self.new_feature_view.selectedIndexes() if i.column() == 6]
        selected_feature_collections = [i.data() for i in self.new_feature_view.selectedIndexes() if i.column() == 7]
        
        selected_features = []

        for i in range(len(selected_feature_ids)):
            fc = next(filter(lambda x: x.shortname == selected_feature_collections[i],self.session.loaded_feature_collections)).feature_collection
            feature = fc.get(lambda f: f.get_feature_id().get_string() == selected_feature_ids[i])
            selected_features.append(feature)
        
        if len(selected_features) == 0:
            QMessageBox.critical(self, "Error", "No features selected!")
            return
        
        if not self.session._rotationModel:
            QMessageBox.critical(self, "Error", "No rotation model selected!")
            return
        
        if not self._save_location:
            QMessageBox.critical(self, "Error", "No save location set!")
            return

        fc = self.actual_splitting(selected_features, selected_rift, split_date)
        fc.write(self._save_location)
        QMessageBox.information(self, "Success", "Successfully saved split features: " + path.realpath(self._save_location))

    def actual_splitting(self, plates, rift, rifting_time) -> pygplates.FeatureCollection:
        initial_feature_collection = pygplates.FeatureCollection(plates)
        rotation_model = self.session._rotationModel
        snapshot = pygplates.ReconstructSnapshot(initial_feature_collection, rotation_model, rifting_time)
        rift_snapshot = pygplates.ReconstructSnapshot(pygplates.FeatureCollection(rift), rotation_model, rifting_time)
        snapshot_features = snapshot.get_reconstructed_geometries()
        rift_snapshot_feature = rift_snapshot.get_reconstructed_geometries()[0]

        new_collection = pygplates.FeatureCollection()

        for feature in snapshot_features:
            plates = split_plate_by_line(feature.get_reconstructed_geometry(), rift_snapshot_feature.get_reconstructed_geometry())

            if len(plates) == 0:
                # Ignore making features if we have no plates
                continue

            plate_feature = feature.get_feature()

            for new_plate in [
                pygplates.Feature.create_reconstructable_feature(plate_feature.get_feature_type(), split_plate, f"{plate_feature.get_name()} [{i}]", reconstruction_plate_id=plate_feature.get_reconstruction_plate_id())
                for i, split_plate in enumerate(plates)
                ]:
                new_plate.set_valid_time(rifting_time, float("-inf"))
                new_collection.add(new_plate)
        
        pygplates.reverse_reconstruct(new_collection, rotation_model, rifting_time)

        return new_collection
