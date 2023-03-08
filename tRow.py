"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------[ class TableRow ]---------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------"""
from tLib import TableError
from alx import class_name, inspect_info
"""------------------------------------------------------------------------------------------------------------------"""


class TableRow:  # TableRow
    row = []
    index = 0
    table = None
    chunk_index = 0

    def __str__(self):
        return f'[{", ".join(map(str,self.row))}]'

    def get_row_chunk(self, chunk_info: dict, row_index: int) -> list:  # TableRow
        """
        Формат chunk_info = {'data_table': [],  = список строк-списков, строк-кортежей или строк-словарей
                        'filler': filler = заполнитель пустых ячеек, которые не содержат значений
                        'type': None, = тип строк: list или dict
                        'keys': [], = ключи столбцов (словарей столбцов. Ключи используются для выборки определенных
                                      столбцов из data_table, если тип строк - dict.
                        'header': [], = заголовки столбцов
                        'minimax': (0, 0),= минимальное и максимальное число столбцов, обнаруженное в строках data_table
                        'columns': 0, = число столбцов. Может использоваться для сокращения или расширения числа
                                        столбцов
                        'rows': 0} = число строк data_table
        """
        chunk_row = []

        if row_index < 0:
            row_index = row_index + chunk_info['rows']
        if row_index < 0:
            raise TableError(f"{class_name(self)}: Строка с номером {row_index + chunk_info['rows']} не существует.\n"
                             f"{inspect_info()}")

        if row_index < chunk_info['rows']:  # строка в пределах этой подтаблицы
            if chunk_info['type'] == dict:  # таблица словарей
                if not chunk_info['selector']:      # селектор пуст
                    chunk_row = list(chunk_info['data'][row_index].values())
                else:                               # селектор заполнен
                    chunk_row = \
                        [chunk_info['data'][row_index].get(key, chunk_info['filler']) for key in chunk_info['selector']]
            else:                           # таблица списков
                if not chunk_info['selector']:      # селектор пуст
                    chunk_row = list(chunk_info['data'][row_index])
                else:
                    for i in chunk_info['selector']:
                        try:
                            chunk_row.append(chunk_info['data'][row_index][i])
                        except IndexError:
                            chunk_row.append(chunk_info['filler'])

            chunk_row = chunk_row[0:chunk_info['columns']]  # обрезаем строку по columns
            empty_count = chunk_info['columns'] - len(chunk_row)

        else:  # строка вне пределов подтаблицы - заполняем filler'ом - это применяется для выравнивания длин chunks.
            empty_count = chunk_info['columns']

        while empty_count > 0:
            chunk_row.append(chunk_info['filler'])
            empty_count -= 1
        return chunk_row

    def _resync_row_(self):  # TableRow
        self.row = []
        for chunk in self.table.chunk_list:
            self.row += self.get_row_chunk(chunk, self.row_index)

    def __init__(self, table_obj, row_index, cache=True):  # TableRow

        self.index = 0
        self.resync = not cache
        self.table = table_obj
        self.row_index = row_index
        self._resync_row_()

    def get_row_data(self):  # TableRow
        if self.resync:
            self._resync_row_()
        return self.row

    def __len__(self):  # TableRow
        if self.resync:
            self._resync_row_()
        return len(self.row)

    def __getitem__(self, i):  # TableRow
        if self.resync:
            self._resync_row_()

        if i < 0:
            i = len(self.row) + i

        if -1 < i < len(self.row):
            ret = self.row[i]
            if self.resync:
                self.row = []  # если не указано хранить кеш, то экономим память на строках.
            return ret
        else:
            raise TableError(f"{class_name(self)}: В строке нет столбца с номером: {i}. Всего столбцов: {self.row}\n"
                             f"{inspect_info()}")

    def __iter__(self):  # TableRow
        self.index = 0
        return self

    def __next__(self):  # TableRow
        if self.resync:
            self._resync_row_()
        if self.index >= len(self.row):
            raise StopIteration()
        else:
            self.index += 1
            return self.row[self.index-1]
