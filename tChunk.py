import os
from tLib import TableError, json_ext, csv_ext, eval_index
from alx import add_str, class_name, _q, inspect_info, read_pydata_from_json_file, dbg, get_datetime_stamp, \
    del_if_exist, is_opened


class TableChunk:
    array = None
    selector = None
    columns = None
    headers = None
    head_keys = None
    filler = None
    slicer: list = None

    """ variables to be defined later """
    types = None
    minimax = None
    rows = None

    def __str__(self):
        _index = 0
        about = '=' * 16 + '\n'
        about, _l = add_str(about, '{:<17}'.format(f'{class_name(self)}:'))
        about, _l = add_str(about, '{:<17}'.format(f'-' * 16))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Type of rows:', str(type(self.types()))))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Rows:', self.rows))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Columns:', self.columns))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Selector:', f"{repr(self.selector)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Headers:', f"{repr(self.headers)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('MiniMax:', f"{repr(self.minimax)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Filler:', f"{repr(self.filler)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Slicer:', f"{repr(self.slicer)}"))
        about, _l = add_str(about, '{:<17} {:<17}'.format('head_keys:', f"{repr(self.head_keys)}"),
                            endstr=True)
        return about

    def __init__(self,
                 array: str | list | tuple,
                 selector: list | tuple | None = None,
                 columns: int | None = None,
                 headers: list | tuple | dict | int | None = None,
                 head_keys: bool = True,
                 filler: any = None,
                 slicer: list | None = None):
        """

        Parameters
        ----------
        array : массив табличных данных: list|tuple[list|tuple|dict]
        selector : перечень ключей, по которым будет сделана выборка столбцов, если строки это dict; или: перечень
        индексов, если строки - это list или tuple
        columns : число, по которому будет выравниваться число столбцов (добавляться справа или сокращаться справа).
        При добавлении - используется значение, заданное filler
        headers : список/кортеж/словарь заголовков столбцов или указатель на строку array, которая их содержит
        (list, tuple, или dict.values)
        head_keys : если True _и_ указан headers _и_ (строки dict _или_ тип headers=dict), то для выборки заголовков
        используется не dict.values() а dict.keys()
        filler :
        slicer :
        """

        """ iteration index """
        self._index = 0

        """ variables to be defined now from parms """
        self.array = array
        self.selector = selector
        self.columns = columns
        self.headers = headers
        self.head_keys = head_keys
        self.filler = filler
        self.slicer = slicer

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
        self.array = array

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
                                     f'Получено: columns={_q(columns)}.\n'
                                     f'{inspect_info()}')
            else:
                raise TableError(f'{class_name(self)}: Число столбцов должно быть задано целым числом.\n'
                                 f'Получено: columns={_q(columns)}.\n'
                                 f'{inspect_info()}')
        # 'selector':
        self._take_selector(selector)

        # 'header'
        self._take_headers(headers, head_keys=head_keys)

        if self.selector:
            if self.headers:
                if len(self.headers) != len(self.selector):
                    raise TableError(f'{class_name(self)}: Размеры списков selector и headers не совпадают.')
            else:
                self.headers = self.selector.copy()

    def __len__(self):
        if self.slicer is None:
            return self.rows
        else:
            return len(self.slicer)

    def __iter__(self):  # Table
        self._index = 0
        return self

    def __next__(self):  # Table
        if self.slicer is None:
            size = self.rows
        else:
            size = len(self.slicer)

        if self._index >= size:
            raise StopIteration()
        else:
            i = eval_index(self._index, self.rows, slicer=self.slicer)
            ret = self.__getitem__(i)
            self._index += 1
            return ret

    def __getitem__(self, subscript: int | slice):
        if isinstance(subscript, int):
            i = eval_index(subscript, self.rows, self.slicer)
            return self._get_row(subscript)
        elif isinstance(subscript, slice):
            slicer = self.slicer
            if slicer is None:
                slicer = list(range(self.rows))
            slicer = slicer[subscript]
            sliced_chunk = TableChunk(self.array,
                                      selector=self.selector,
                                      columns=self.columns,
                                      headers=self.headers,
                                      head_keys=self.head_keys,
                                      filler=self.filler,
                                      slicer=slicer
                                      )
            return sliced_chunk

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
                    if not self.selector:  # селектор пуст
                        chunk_row = list(self.array[row_index].values())
                    else:  # селектор заполнен
                        chunk_row = \
                            [self.array[row_index].get(key, self.filler) for key in self.selector]
                else:  # таблица списков
                    if not self.selector:  # селектор пуст
                        chunk_row = list(self.array[row_index])
                    else:
                        for i in self.selector:
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

    def _take_selector(self, selector: list | tuple) -> None:  # Table
        """
        Устанавливает список селекторов.
        * Если таблица состоит из списков/кортежей, то селектор - это список целочисленных индексов столбцов от 0.
        * Если таблица состоит из словарей, то селектор - это список ключей столбцов.

        Parameters
        ----------
        selector : селектор

        Returns
        -------
        selector (список)
        """
        if selector is None:
            _lst = list()
        elif isinstance(selector, list) or isinstance(selector, tuple):
            _lst = list(selector)
            self.columns = len(_lst)
        else:
            raise TableError(f'{class_name(self)}: Селектор должен быть списком или кортежем.'
                             f'Получено: {type(selector)}\n'
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
        self.selector = _lst

    def _take_headers(self, hdr: int | list | tuple | dict | None, head_keys=True) -> None:  # Table
        """
        Устанавливает список заголовков, которые заданы списком/кортежем/словарем либо ссылкой на строку data_table,
         из которой они извлекаются. Если задан словарем или ссылкой на словарь(-строку) то извлекаются как
         dict.values()

        Parameters
        ----------
        chunk_info : заголовок подтаблицы данных (chunk)
        hdr : параметр titles или keys переданный в __init__

        Returns
        -------
        возвращает параметр в виде списка значений
        """
        if hdr is None:
            _lst = []

        elif isinstance(hdr, int):
            """ -> Задан номер строки, хранящей заголовки """
            hdr_row_index = eval_index(hdr, self.rows)
            if hdr_row_index >= 0:
                if self.types == dict:
                    if head_keys:
                        _lst = [title for title in self.array[hdr_row_index].keys()]
                    else:
                        _lst = [title for title in self.array[hdr_row_index].values()]
                else:
                    _lst = list(self.array[hdr_row_index])
            else:
                raise TableError(f"{class_name(self)}: Параметр headers={hdr} указывает за пределы таблицы\n"
                                 f"{inspect_info()}")

            """ -> задан список или кортеж """
        elif isinstance(hdr, list) or isinstance(hdr, tuple):
            _lst = list(hdr)

            """ -> задан словарь """
        elif isinstance(hdr, dict):
            if head_keys:
                _lst = [header for header in hdr.keys()]
            else:
                _lst = [header for header in hdr.values()]
        else:
            raise TableError(f"{class_name(self)}: Тип type(headers)={type(hdr)} не поддерживается\n"
                             f"{inspect_info()}")
        self.headers = _lst
