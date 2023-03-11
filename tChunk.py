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

        """ iteration index (used by __iter__()) """
        self.iter_index: int = 0

        """ variables to be defined now from parms """
        self.array: str | list | tuple = array
        self.columns: int | None = columns
        self.columns_arg: int | None = columns  # если None, то число столбцов будет назначаться автоматически.
        self.use_keys = use_keys
        self.selected_cols: list | None = select_cols
        self.selected_rows: list | None = select_rows
        self.filler: any = filler

        """ variables to be defined later """
        self.headers: list | dict | None = None
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
        if columns is None:
            self.columns = self.minimax[1]
        else:
            if type(columns) == int:
                if columns >= 0:  # разрешаем число столбцов = 0 (пустой объект)
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
        self._set_selected_cols(select_cols)
        if self.selected_cols and (self.columns_arg is None):  # Если columns не был задан явно при создании объекта,
            self.columns = len(self.selected_cols)             # то корректируем его автоматически

        # 'header'
        self._set_headers(headers, use_keys=use_keys)

    def __len__(self):
        if self.selected_rows:
            return len(self.selected_rows)
        else:
            return self.rows

    def __iter__(self):  # Table
        self.iter_index = 0
        return self

    def __next__(self):  # Table
        size = self.__len__()

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
            #return self._get_chunk_row(subscript)
            return self._get_chunk_row(i)
        elif isinstance(subscript, slice):
            selected_rows = self.selected_rows
            if selected_rows is None:
                selected_rows = list(range(self.rows))
            selected_rows = selected_rows[subscript]
            sliced_chunk = TableChunk(self.array,
                                      select_cols=self.selected_cols,
                                      columns=self.columns,
                                      headers=self.headers,
                                      use_keys=self.use_keys,
                                      filler=self.filler,
                                      select_rows=selected_rows
                                      )
            return sliced_chunk
        else:
            raise TableError(f'{class_name(self)}: Ожидался аргумент типа int или slice. Получен: {type(subscript)}\n'
                             f'{inspect_info()}')

    def get_chunk_headers(self) -> list:
        """
        Возвращает список заголовков столбцов с учетом значения self.columns и self.selected_cols
        Returns
        -------
        """
        _lst = []

        if self.selected_cols:  # если задана выборка столбцов (для self.types=dict она задана всегда)
            if self.headers:  # если заданы заголовки (для self.types==dict - она заданы словарем, иначе - списком)
                if self.types == dict:
                    if self.use_keys:
                        _lst = self.selected_cols
                    else:
                        for key in self.selected_cols:
                            _lst.append(self.headers.get(key, self.filler))
                else:
                    _lst = [self.headers[i] for i in self.selected_cols]
            else:  # если строки заданы словарями, а заголовки не заданы, но указано self.use_keys=True, то заголовки -
                #    это ключи.
                if self.types == dict:
                    if self.use_keys:
                        _lst = self.selected_cols
        else:
            if self.headers:
                # *** dbg *** отладочная проверка
                if self.types == dict:
                    raise TableError(f'{class_name(self)}: Внутренняя ошибка: если тип строк = dict, то '
                                     f'self.selected_cols всегда должен быть определен.\n'
                                     f'Обнаружено: self.selected_cols={repr(self.selected_cols)}\n'
                                     f'{inspect_info()}')
                _lst = self.headers

        # *** dbg *** отладочная проверка
        if self.selected_cols:
            if len(self.selected_cols) != self.columns:
                if not self.columns_arg:
                    raise TableError(f'{class_name(self)}: Внутренняя ошибка: если self.selected_cols определен, его '
                                     f'длинна должна быть равна значению self.columns.\n'
                                     f'Обнаружено: len(self.selected_cols)={len(self.selected_cols)}; '
                                     f'self.columns={self.columns}\n'
                                     f'{inspect_info()}')
        _lst = _lst[0:self.columns]
        empty_count = self.columns - len(_lst)
        while empty_count > 0:
            _lst.append(self.filler)
            empty_count -= 1

        return _lst

    def _get_chunk_row(self, row_index):
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

    def _set_selected_cols(self, ptr: list | tuple) -> None:  # Table
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
                    raise TableError(f'{class_name(self)}: Массив данных состоит из словарей с отличающимися наборами '
                                     f'ключей. Автоматическое назначение ключей выборки невозможно. \n'
                                     f'Задайте набор используемых ключей с помощью параметра select_col.\n'
                                     f'{inspect_info}')
            else:
                #_lst = list(range(self.minimax[1]))
                pass  # все же - нет необходимости задавать индексы автоматически

        elif isinstance(ptr, list) or isinstance(ptr, tuple):
            _lst = list(ptr)
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

    def _set_headers(self, ptr: int | list | tuple | dict | None, use_keys=True) -> None:  # Table
        """
        Устанавливает список заголовков. Заголовки могут быть заданы списком/кортежем/словарем либо ссылкой
        на номер строки, которая их содержит. Если строка задана словарем, то учитывается параметр use_keys.
        Если use_case == True, то в качестве заголовков используются ключи словаря: dict.keys()
        Если use_case == False, то в качестве заголовков используются ключи словаря: dict.values()

        * Если тип строк (self.types) - словарь, то заголовки также должны быть заданы словарем

        * Заголовки устанавливаются для всех столбцов, независимо от значения параметра self.selected_cols

        Parameters
        ----------
        ptr : перечень заголовков - список, кортеж, словарь или номер строки, содержащей список, кортеж или словарь

        Returns
        -------
        None. self.headers присваивается список заголовков.
        """
        if ptr is None:
            _hdr = None

        elif isinstance(ptr, int):
            """ -> Задан номер строки, хранящей заголовки """
            hdr_row_index = eval_index(ptr, self.rows)
            if hdr_row_index >= 0:  # eval_index возвращает -1, если индекс выходит за пределы таблицы
                if self.types == dict:
                    _hdr = self.array[hdr_row_index]
                else:
                    _hdr = list(self.array[hdr_row_index])
            else:
                raise TableError(f"{class_name(self)}: Параметр headers={ptr} указывает за пределы таблицы\n"
                                 f"{inspect_info()}")

            """ -> задан список или кортеж """
        elif isinstance(ptr, list) or isinstance(ptr, tuple):
            if self.types == dict:
                raise TableError(f"{class_name(self)}: Если строки представлены словарями, то заголовки должны "
                                 f"быть заданы словарем.\n"
                                 f"Получено: type(headers) = {type(ptr)}\n"
                                 f"{inspect_info()}")
            else:
                _hdr = list(ptr)

            """ -> задан словарь """
        elif isinstance(ptr, dict):
            if self.types == dict:
                _hdr = ptr
            elif use_keys:
                _hdr = [header for header in ptr.keys()]
            else:
                _hdr = [header for header in ptr.values()]
        else:
            raise TableError(f"{class_name(self)}: Тип type(headers)={type(ptr)} не поддерживается\n"
                             f"{inspect_info()}")

        self.headers = _hdr
