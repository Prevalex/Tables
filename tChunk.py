import os
from tLib import TableError, json_ext, csv_ext, eval_index, get_array_keys
from alx import add_str, class_name, inspect_info, read_pydata_from_json_file, dbg


class TableChunk:

    def __str__(self) -> str:
        _index = 0
        about = '=' * 16 + '\n'
        about, _l = add_str(about, '{:<17}'.format(f'{class_name(self)}:'))
        about, _l = add_str(about, '{:<17}'.format(f'-' * 16))
        about, _l = add_str(about, '{:<17} {:<17}'.format('types:', str(type(self.types()))))
        about, _l = add_str(about, '{:<17} {:<17}'.format('rows:', self.rows))
        about, _l = add_str(about, '{:<17} {:<17}'.format('selected_rows:', f"{repr(self.selected_rows)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('columns:', self.columns))
        about, _l = add_str(about, '{:<17} {:<17}'.format('selected_cols:', f"{repr(self.selected_cols)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('headers:', f"{repr(self.headers)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('miniMax:', f"{repr(self.minimax)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('filler:', f"{repr(self.filler)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('use_keys:', f"{repr(self.use_keys)}"),
                            endstr=True)
        return about

    def __init__(self,
                 array: str | list | tuple,
                 select_cols: list | tuple | None = None,
                 select_rows: list | None = None,
                 columns: int | None = None,
                 headers: list | tuple | dict | int | None = None,
                 use_keys: bool = True,
                 filler: any = None,
                 ):
        """
        Parameters
        ----------
        array :         Массив табличных данных: list|tuple[list|tuple|dict] или имя файла .json или .csv
        select_cols :   Если строки - это dict, то select_cols - это перечень ключей (type any), по которым будет
                        сделана выборка. Если строки - это list или tuple, то select_cols - это перечень индексов
                        столбцов (type int).
        select_rows :   Список индексов строк, которые включаются в таблицу.
        columns :       Число, по которому будет выравниваться число столбцов (добавляться справа или сокращаться
                        справа). Для добавления столбцов будет использовано значение, заданное параметром filler
        headers :       Список/кортеж/словарь заголовков столбцов или указатель на строку array, которая их содержит.
                        Если строки представлены словарями, то в качестве заголовков используются dict.values().
                        Но если указан use_keys=True, то в качестве заголовков будут использованы ключи словаря.
        use_keys :     Если True _и_ указан headers _и_ (строки dict _или_ тип headers=dict), то для выборки заголовков
                        используется не dict.values() а dict.keys()
        filler :        значение, которое будет использоваться как заполнитель при добавлении столбцов.
        """

        """ iteration index """
        self.iter_index: int = 0

        """ variables to be defined now from parms """
        self.array: str | list | tuple = array
        self.columns: list | tuple | None = columns
        self.headers: list | None = headers
        self.use_keys = use_keys
        self.selected_cols: list | None = select_cols
        self.selected_rows: list | None = select_rows
        self.filler: any = filler

        """ variables to be defined later """
        self.types = None
        self.minimax = None
        self.rows = None

        """ Если array имеет тип str, то считаем, что передано имя json или csv файла, которые 
            должны существовать и иметь соответствующие расширения .csv или .json.
            Если все так - загружаем содержимое файла в память"""
        if isinstance(array, str):  # >>> Передано имя файла
            src_filename = os.path.abspath(array)
            src_file_ext = os.path.splitext(src_filename)[1].lower()

            if not os.path.isfile(src_filename):
                raise TableError(f'{class_name(self)}: Файл {src_filename} не найден.\n'
                                 f'{inspect_info()}')

            elif src_file_ext == json_ext.lower():
                array = read_pydata_from_json_file(src_filename)

            elif src_file_ext == csv_ext.lower():
                #data_table = alx.read_pydata_from_csv_file(src_filename)
                raise TableError(f'{class_name(self)}: Поддержка файлов .csv не реализована\n{inspect_info()}')
            else:
                raise TableError(f'{class_name(self)}: Файл таблицы должен иметь расширение {json_ext} или {csv_ext}. '
                                 f'Получен: {src_filename}\n{inspect_info()}')

        """ Если array имеет тип, отличный от str, tuple или list - то генерируем исключение """
        if not (isinstance(array, list) or isinstance(array, tuple)):
            raise TableError(f'{class_name(self)}: Таблица должны иметь тип list или tuple.'
                             f'Получен: {type(array)}'
                             f'.\n{inspect_info()}')
        # 'data':
        if len(array) > 0:
            self.array = array
        else:
            raise TableError(f'{class_name(self)}: Получен пустой массив табличных данных.'
                             f'.\n{inspect_info()}')
        # 'type':
        """ проверяем, что бы все строки были одного типа и запоминаем этот тип. Допустимые типы: tuple, list, dict"""
        if all([isinstance(row_data, list) for row_data in array]):
            self.types = list
        elif all([isinstance(row_data, tuple) for row_data in array]):
            self.types = tuple
        elif all([isinstance(row_data, dict) for row_data in array]):
            self.types = dict
        else:
            raise TableError(f'{class_name(self)}: Все строки таблицы должны быть одного типа. Допустимые типы::  list,'
                             f' dict, tuple.\n'
                             f'{inspect_info()}')
        # 'rows':
        """ устанавливаем длину массива"""
        self.rows = len(array)

        # 'minimax':
        """ устанавливаем минимальное и максимальное число столбцов, обнаруженное в строках массива"""
        _lens = [len(_itm) for _itm in array]
        self.minimax = min(_lens), max(_lens)

        # 'columns':
        """ устанавливаем требуемое число столбцов, по которому будут выравниваться (наращиваться или укорачиваться)
            все строки массива. Наращивание производится добавлением значений filler"""
        self.columns = self.minimax[1]
        if columns is not None:
            if type(columns) == int:
                if columns > 0:
                    self.columns = columns
                else:
                    raise TableError(f'{class_name(self)}: Число столбцов должно быть задано положительным целым '
                                     f'числом.\n'
                                     f'Получено: columns={repr(columns)}.\n'
                                     f'{inspect_info()}')
            else:
                raise TableError(f'{class_name(self)}: Число столбцов должно быть задано целым числом.\n'
                                 f'Получено: columns={repr(columns)}.\n'
                                 f'{inspect_info()}')
        # 'select_cols':
        self._take_col_selection(select_cols)

        # 'header'
        self._take_headers(headers, use_keys=use_keys)

        if self.selected_cols:
            if self.headers:
                if len(self.headers) != len(self.selected_cols):
                    raise TableError(f'{class_name(self)}: Размеры списков selector и headers не совпадают.')
            else:
                self.headers = self.selected_cols.copy()

    def __len__(self):
        if self.selected_rows is None:
            return self.rows
        else:
            return len(self.selected_rows)

    def __iter__(self):  # Table
        self.iter_index = 0
        return self

    def __next__(self):  # Table
        if self.selected_rows is None:
            size = self.rows
        else:
            size = len(self.selected_rows)

        if self.iter_index >= size:
            raise StopIteration()
        else:
            i = eval_index(self.iter_index, self.rows, slicer=self.selected_rows)
            ret = self.__getitem__(i)
            self.iter_index += 1
            return ret

    def __getitem__(self, subscript: int | slice):
        if isinstance(subscript, int):
            i = eval_index(subscript, self.rows, self.selected_rows)
            return self._get_row(subscript)
        elif isinstance(subscript, slice):
            slicer = self.selected_rows
            if slicer is None:
                slicer = list(range(self.rows))
            slicer = slicer[subscript]
            sliced_chunk = TableChunk(self.array,
                                      select_cols=self.selected_cols,
                                      columns=self.columns,
                                      headers=self.headers,
                                      use_keys=self.use_keys,
                                      filler=self.filler,
                                      select_rows=slicer
                                      )
            return sliced_chunk
        else:
            raise TableError(f'{class_name(self)}: Ожидался аргумент типа int или slice. Получен: {type(subscript)}\n'
                             f'{inspect_info()}')

    def _get_row(self, row_index):
        chunk_row = []
        if not isinstance(row_index, int):
            raise TableError(f"{class_name(self)}: Индекс строки row_index должен иметь тип int.\n"
                             f"Получен: {type(row_index)}.\n"
                             f"{inspect_info()}")
        else:
            row_index = eval_index(row_index, self.rows)
            if row_index < 0:
                raise TableError(f"{class_name(self)}: Строка с номером {row_index + self.rows} не существует.\n"
                                 f"{inspect_info()}")
            else:  # строка в пределах этой подтаблицы
                if self.types == dict:  # таблица словарей
                    if not self.selected_cols:  # селектор пуст
                        chunk_row = list(self.array[row_index].values())
                    else:  # селектор заполнен
                        chunk_row = \
                            [self.array[row_index].get(key, self.filler) for key in self.selected_cols]
                else:  # таблица списков
                    if not self.selected_cols:  # селектор пуст
                        chunk_row = list(self.array[row_index])
                    else:
                        for i in self.selected_cols:
                            try:
                                chunk_row.append(self.array[row_index][i])
                            except IndexError:
                                chunk_row.append(self.filler)

                chunk_row = chunk_row[0:self.columns]  # обрезаем строку по columns
                empty_count = self.columns - len(chunk_row)

                while empty_count > 0:
                    chunk_row.append(self.filler)
                    empty_count -= 1
            return chunk_row

    def _take_col_selection(self, ptr: list | tuple) -> None:  # Table
        """
        Устанавливает список селекторов.
        * Если таблица состоит из списков/кортежей, то селектор - это список целочисленных индексов столбцов от 0.
        * Если таблица состоит из словарей, то селектор - это список ключей столбцов.

        Parameters
        ----------
        ptr : селектор

        Returns
        -------
        selector (список)
        """
        _lst = list()

        if ptr is None:
            if self.types == dict:
                _lst = get_array_keys(self.array)
                if not _lst:  # если список ключей после get_array_keys пуст
                    raise TableError(f'{class_name(self)}: Массив данных состоит из словарей с различными наборами '
                                     f'ключей. Задайте набор используемых ключей с помощью параметра select_col.\n'
                                     f'{inspect_info}')
            else:
                #_lst = list(range(self.minimax[1]))
                pass  # все же - нет необходимости задавать индексы автоматически

        elif isinstance(ptr, list) or isinstance(ptr, tuple):
            _lst = list(ptr)
            self.columns = len(_lst)

        else:
            raise TableError(f'{class_name(self)}: Селектор должен быть списком или кортежем.'
                             f'Получено: {type(ptr)}\n'
                             f'{inspect_info()}')

        """ выполняем дополнительную проверку полученного селектора"""
        if self.types == dict:
            """ разрешаем ключи любого типа"""
            pass
        else:
            for i in _lst:
                if type(i) != int:
                    raise TableError(
                        f'{class_name(self)}: Для таблиц, состоящих из списков и кортежей селекторы должны '
                        f'иметь тип int. Получен: type({i})={type(i)}')

        self.selected_cols = _lst

    def _take_headers(self, ptr: int | list | tuple | dict | None, use_keys=True) -> None:  # Table
        """
        Устанавливает список заголовков, которые заданы списком/кортежем/словарем либо ссылкой на строку data_table,
         из которой они извлекаются. Если задан словарем или ссылкой на словарь(-строку) то извлекаются как
         dict.values()

        Parameters
        ----------
        ptr : параметр titles или keys переданный в __init__

        Returns
        -------
        возвращает параметр в виде списка значений
        """
        if ptr is None:
            _lst = []

        elif isinstance(ptr, int):
            """ -> Задан номер строки, хранящей заголовки """
            hdr_row_index = eval_index(ptr, self.rows)
            if hdr_row_index >= 0:
                if self.types == dict:
                    if use_keys:
                        _lst = [title for title in self.array[hdr_row_index].keys()]
                    else:
                        _lst = [title for title in self.array[hdr_row_index].values()]
                else:
                    _lst = list(self.array[hdr_row_index])
            else:
                raise TableError(f"{class_name(self)}: Параметр headers={ptr} указывает за пределы таблицы\n"
                                 f"{inspect_info()}")

            """ -> задан список или кортеж """
        elif isinstance(ptr, list) or isinstance(ptr, tuple):
            _lst = list(ptr)

            """ -> задан словарь """
        elif isinstance(ptr, dict):
            if use_keys:
                _lst = [header for header in ptr.keys()]
            else:
                _lst = [header for header in ptr.values()]
        else:
            raise TableError(f"{class_name(self)}: Тип type(headers)={type(ptr)} не поддерживается\n"
                             f"{inspect_info()}")
        self.headers = _lst
