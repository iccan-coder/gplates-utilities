import os
from typing import Sequence

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QMessageBox, QWidget
import pygplates


class LoadedFeatureCollection():
    def __init__(self, path, feature_collection) -> None:
        self.path = path
        self.feature_collection = feature_collection
        self.shortname = os.path.basename(path)


class Session:
    def __init__(self) -> None:
        self.loaded_feature_collections: list[LoadedFeatureCollection] = []
        self.windows: list[QWidget] = []

        self._feature_collection_names = QStringListModel()
        self._feature_model = QStandardItemModel()
        self._feature_model.setColumnCount(7)
        self._feature_model.setHorizontalHeaderLabels(["Feature Name", "Feature Type", "Geometry Type", "Plate ID", "Start Time", "End Time", "Feature ID", "Feature Collection"])

        self._rotationModel_path: str = ""
        self._rotationModel: pygplates.RotationModel = None
    
    def load_rotation_model(self, path):
        self._rotationModel_path = path
        self._rotationModel = pygplates.RotationModel(path)
    
    def reload_rotation_model(self):
        if self._rotationModel_path == "":
            QMessageBox.warning(None, "Error", "Cannot reload uninitialized feature model.")
            return
        
        self._rotationModel = pygplates.RotationModel(self._rotationModel_path)

    
    def get_feature_collection_model(self):
        return self._feature_collection_names
    
    def get_feature_model(self):
        return self._feature_model
    
    def load_feature_collections(self, paths: list[str]) -> None:
        new_paths = [p for p in paths if len([lfc for lfc in self.loaded_feature_collections if lfc.path == p]) == 0]

        if len(new_paths) == 0:
            return
        
        for path in new_paths:
            lfc = LoadedFeatureCollection(path, pygplates.FeatureCollection(path))
            self.loaded_feature_collections.append(lfc)
            for feature in lfc.feature_collection:
                feature_item: Sequence[QStandardItem] = []

                feature_item.append(QStandardItem(feature.get_name()))                          # Feature Name
                feature_item.append(QStandardItem(feature.get_feature_type().get_name()))       # Feature Type
                feature_item.append(QStandardItem(type(feature.get_geometry()).__name__))       # Geometry Type
                feature_item.append(QStandardItem(str(feature.get_reconstruction_plate_id())))  # Plate ID
                feature_item.append(QStandardItem(str(feature.get_valid_time()[0])))            # Start Time
                feature_item.append(QStandardItem(str(feature.get_valid_time()[1])))            # End Time
                feature_item.append(QStandardItem(feature.get_feature_id().get_string()))       # Feature ID
                feature_item.append(QStandardItem(lfc.shortname))                               # Feature Collection (shortname)

                self._feature_model.appendRow(feature_item)

        # Completely update our names model
        self._feature_collection_names.setStringList([x.shortname for x in self.loaded_feature_collections])
    
    def unload_feature_collection(self, shortname):
        lfc = next(filter(lambda x: x.shortname == shortname, self.loaded_feature_collections), None)

        if not lfc:
            return
        
        self.loaded_feature_collections.remove(lfc)

        # Update Feature Collection name model
        index = self._feature_collection_names.stringList().index(shortname)
        self._feature_collection_names.removeRow(index)

        # Update Feature Model
        items = self._feature_model.findItems(shortname, Qt.MatchFlag.MatchFixedString, 7)
        for i in items:
            self._feature_model.removeRow(i.row())
    
    def reload_features(self):
        self._feature_model.removeRows(0, self._feature_model.rowCount())
        self._feature_model.setColumnCount(7)
        self._feature_model.setHorizontalHeaderLabels(["Feature Name", "Feature Type", "Geometry Type", "Plate ID", "Start Time", "End Time", "Feature ID", "Feature Collection"])

        for lfc in self.loaded_feature_collections:
            lfc.feature_collection = pygplates.FeatureCollection(lfc.path)

            for feature in lfc.feature_collection:
                feature_item: Sequence[QStandardItem] = []

                feature_item.append(QStandardItem(feature.get_name()))                          # Feature Name
                feature_item.append(QStandardItem(feature.get_feature_type().get_name()))       # Feature Type
                feature_item.append(QStandardItem(type(feature.get_geometry()).__name__))       # Geometry Type
                feature_item.append(QStandardItem(str(feature.get_reconstruction_plate_id())))  # Plate ID
                feature_item.append(QStandardItem(str(feature.get_valid_time()[0])))            # Start Time
                feature_item.append(QStandardItem(str(feature.get_valid_time()[1])))            # End Time
                feature_item.append(QStandardItem(feature.get_feature_id().get_string()))       # Feature ID
                feature_item.append(QStandardItem(lfc.shortname))                               # Feature Collection (shortname)

                self._feature_model.appendRow(feature_item)