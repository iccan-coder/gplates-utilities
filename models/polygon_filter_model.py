from PySide6.QtCore import QSortFilterProxyModel


class PolygonFilterModel(QSortFilterProxyModel):
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