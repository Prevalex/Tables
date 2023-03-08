import os
from alx import add_str, class_name, inspect_info, read_pydata_from_json_file
from tLib import TableError, json_ext, csv_ext
from tRow import TableRow


"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------[ class Table ]------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------"""

class Table:  # Table
    """
    Объекты класса Table формируются из подтаблиц (chunks). Потаблицы объединяются поколоночно, слева направо:
    То есть: сначала идет подтаблица 0, потом, начиная со следующего столбца - подтаблица 1 и т.д.

    Сами данные подтаблицы могут иметь формат списка списков, списка словарей или списка кортежей, где словари списки и
    кортежи представляют строки. В каждой data_table могут быть строки только одного типа.

    Для каждой подтаблицы создается дескриптор chunk_info:

    Формат chunk_info = {'data_table': [],  = список строк-списков, строк-кортежей или строк-словарей
                        'filler': filler = заполнитель пустых ячеек, которые не содержат значений
                        'type': None, = тип строк: list или dict
                        'selector': [], = ключи столбцов (словарей столбцов. Ключи используются для выборки определенных
                                      столбцов из data_table, если тип строк - dict.
                        'headers': [], = заголовки столбцов
                        'minimax': (0, 0),= минимальное и максимальное число столбцов, обнаруженное в строках data_table
                        'columns': 0, = число столбцов. Может использоваться для сокращения или расширения числа столбцв
                        'rows': 0} = число строк data_table
    """
    _index = 0
    chunk_list = []
    columns = 0
    rows = 0

    def __str__(self):  # Table
        def chunk_str(d: dict, i: int):  # Table
            _about = '\n' + '='*16+'\n'
            _about, __l = add_str(_about, '{:<17}'.format(f'Data Chunk #{i}:'))
            _about, __l = add_str(_about, '{:<17}'.format(f'-' * 16))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('Type of rows:', str(type(d['type']()))))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('Rows:', d['rows']))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('Columns:', d['columns']))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('Selector:', f"[{','.join(map(str,d['selector']))}]"))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('Headers:', f"[{','.join(d['headers'])}]"))
            _about, __l = add_str(_about, '{:<17} {:<17}'.format('MiniMax:', f"{d['minimax'][0]}, {d['minimax'][1]}"))
            return _about.replace('\n','\n  ')

        about = '\n' + '=' * 16 + '\n'
        about, _l = add_str(about, '{:<17}'.format(f'{class_name(self)}:'))
        about, _l = add_str(about, '{:<17}'.format(f'-' * 16))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Chunks:', len(self.chunk_list)))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Rows:', self.rows))
        about, _l = add_str(about, '{:<17} {:<17}'.format('Columns:', self.columns))

        for i in range(len(self.chunk_list)):
            about += chunk_str(self.chunk_list[i], i)

        return about

    def add_chunk_list(self, added_chunk_list):  # Table
        """
        Добавляет подтаблицы (chunks) в таблицу, которые получает в виде списка. Подтаблица (chunks) это структура
        данных, которая содержит ссылку на данные подтаблицы и аттрибуты данных. Данные - это список списков или
        список словарей данных.

        Формат chunk_info = {'data': [], 'filler': filler, 'type': None, 'keys': [], 'header': [],
                    'minimax': (0, 0), 'columns': 0, 'rows': 0}

        Parameters
        ----------
        added_chunk_list : список подтаблиц (chunks)

        Returns
        -------

        """
        for chunk_info in added_chunk_list:
            self.chunk_list.append(chunk_info)
            self.rows = max(self.rows, chunk_info['rows'])
            self.columns = self.columns + chunk_info['columns']

    def __init__(self, array=None, selector=None, columns=None, headers=None, hdkeys=True, filler=None):  # Table
        """
        Parameters
        ----------
        array : список строк в виде списка списков или списка словарей
        selector : указатель на контейнер ключей/заголовков таблицы. Это может быть номер строки, в которой содержатся
                 ключи или список ключей.
        columns : число столбцов, до которого сокращается/расширяется таблица при выводе.
        headers : список заголовков столбцов или номер строки, представленной списком или словарем (titles=dict.values())
        hdkeys: Если True: то для таблиц со строками-словарями, заголовки будут браться из ключей словарей. Иначе - значений
        filler : заполнитель ячеек, у которых нет значений. Например, при расширении таблицы до заданного columns.
        """
        self._index = 0
        self.chunk_list = []
        self.columns = 0
        self.rows = 0
        self.keygen_counter = 0

        if array is not None:
            self.add_chunk(array, selector=selector, columns=columns, headers=headers, hdkeys=hdkeys,
                           filler=filler)

    def add_chunk(self, array, selector=None, columns=None, headers=None, hdkeys=True, filler=None):  # Table
        """
        Добавляет подтаблицу в таблицу. Для каждой подтаблицы формируется дескриптор chunk_info. Поддерживаются только
        вертикальные (колоночные) подтаблицы, которые следуют слева направо.

        Parameters
        ----------
        array : список строк в виде списка списков или списка словарей, или имя json/csv файла, содержащего этот
        список строк.
        selector : список ключей столбцов или номер строки-словаря, из которого будут взяты ключи.
        columns : число столбцов, до которого сокращается/расширяется таблица при выводе.
        headers : список заголовков столбцов или номер строки, представленной списком или словарем (titles=dict.values())
        hdkeys: Если True: то для таблиц со строками-словарями, заголовки будут браться из ключей словарей. Иначе - значений
        filler : заполнитель ячеек, у которых нет значений. Например - при расширении таблицы до заданного columns.
        """

        # add_chunk()
        def __take_selector(chunk, select: list|tuple) -> list:  # Table
            """
            Возвращает список селекторов.
            * Если таблица состоит из списков/кортежей, то селектор - это список целочисленных индексов столбцов от 0.
            * Если таблица состоит из словарей, то селектор - это список ключей столбцов.

            Parameters
            ----------
            chunk :  дескриптор подтаблицы (chunk_info)
            select : селектор

            Returns
            -------
            selector (список)
            """
            if select is None:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  _lst = list()
            elif isinstance(select, list) or isinstance(select, tuple):
                _lst = list(select)
            else:
                raise TableError(f'{class_name(self)}: Селектор должен быть списком или кортежем.'
                                 f'Получено: {type(select)}\n'
                                 f'{inspect_info()}')
            if chunk['type'] == dict:
                pass
            else:
                for i in _lst:
                    if type(i) != int:
                        raise TableError(
                            f'{class_name(self)}: Для таблиц, состоящих из списков и кортежей селекторы должны '
                            f'иметь тип int. Получен: type({i})={type(i)}')
            return _lst

        # add_chunk()
        def __take_headers(chunk_info: dict, pointer: int | list | None, hdkeys=True) -> list:  # Table
            """
            Возвращает список заголовков, которые заданы списком/кортежем/словарем либо ссылкой на строку data_table,
             из которой они извлекаются. Если задан словарем или ссылкой на словарь(-строку) то извлекаются как
             dict.values()

            Parameters
            ----------
            chunk_info : заголовок подтаблицы данных (chunk)
            pointer : параметр titles или keys переданный в __init__


            Returns
            -------
            возвращает параметр в виде списка значений
            """
            if pointer is None:
                _lst = []

                """ -> Задан номер строки """
            elif isinstance(pointer, int):  #  номером строки, откуда брать headers
                if pointer < 0:
                    pointer = pointer + chunk_info['rows']

                if -1 < pointer < chunk_info['rows']:  # Номер строки - в пределах таблицы
                    if chunk_info['type'] == dict:
                        if hdkeys:
                            _lst = [title for title in chunk_info['data'][pointer].keys()]
                        else:
                            _lst = [title for title in chunk_info['data'][pointer].values()]
                    else:
                        _lst = list(chunk_info['data'][pointer])
                else:
                    raise TableError(f"{class_name(self)}: Параметр headers={pointer} указывает за пределы таблицы\n"
                                     f"{inspect_info()}")

                """ -> задан список или кортеж """
            elif isinstance(pointer, list) or isinstance(pointer, tuple):
                _lst = list(pointer)

                """ -> задан словарь """
            elif isinstance(pointer, dict):
                if hdkeys:
                    _lst = [header for header in pointer.keys()]
                else:
                    _lst = [header for header in pointer.values()]
            else:
                raise TableError(f"{class_name(self)}: Тип type(headers)={type(pointer)} не поддерживается\n"
                                 f"{inspect_info()}")
            return _lst

        """ add_chunk()  OWN CODE """

        chunk_info = {'data': list(),
                      'type': None,
                      'selector': list(),
                      'headers': list(),
                      'minimax': (0, 0),
                      'columns': 0,
                      'rows': 0,
                      'filler': filler,
                      }

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

        if not (isinstance(array, list) or isinstance(array, tuple)):
            raise TableError(f'{class_name(self)}: Таблица должны иметь тип list или tuple.'
                             f'Получен: {type(array)}'
                             f'.\n{inspect_info()}')
        # 'data':
        chunk_info['data'] = array

        # 'type':
        if all([isinstance(row_data, list) for row_data in array]):
            chunk_info['type'] = list
        elif all([isinstance(row_data, tuple) for row_data in array]):
            chunk_info['type'] = tuple
        elif all([isinstance(row_data, dict) for row_data in array]):
            chunk_info['type'] = dict
        else:
            raise TableError(f'{class_name(self)}: Все строки таблицы должны быть одного типа. Допустимые типы::  list,'
                             f' dict, tuple.\n'
                             f'{inspect_info()}')
        # 'rows':
        chunk_info['rows'] = len(array)

        # 'minimax':
        _lens = [len(_itm) for _itm in array]
        chunk_info['minimax'] = min(_lens), max(_lens)

        # 'columns':
        chunk_info['columns'] = chunk_info['minimax'][1]
        if columns is not None:
            if type(columns) == int:
                if columns > 0:
                    chunk_info['columns'] = columns
                else:
                    raise TableError(f'{class_name(self)}: Число столбцов, задаваемое параметром columns  должно быть '
                                     f'целым положительным числом.\n'
                                     f'Получено: columns={columns}.\n'
                                     f'{inspect_info()}')
            else:
                raise TableError(f'{class_name(self)}: Число столбцов должно положительным целым числом: '
                                 f'Получено: {columns}.\n'
                                 f'{inspect_info()}')

        # 'selector':
        chunk_info['selector'] = __take_selector(chunk_info, selector)

        # 'header'
        chunk_info['header'] = __take_headers(chunk_info, headers, hdkeys=hdkeys)

        if chunk_info['selector']:
            if chunk_info['header']:
                if len(chunk_info['header']) != len(chunk_info['selector']):
                    raise TableError(f'{class_name(self)}: Размеры списков selector и headers не совпадают.')
            else:
                chunk_info['header'] = chunk_info['selector'].copy()

        self.chunk_list.append(chunk_info)
        self.rows = max(self.rows, chunk_info['rows'])
        self.columns = self.columns + chunk_info['columns']

    def get_table_data(self):  # Table
        table_data = list()
        for row_obj in self:
            row_data = list()
            for cell in row_obj:
                row_data.append(cell)
            table_data.append(row_data)
        return table_data

    def get_header(self):  # Table

        def get_header_chunk(chunk_info: dict) -> list:  # Table
            header_chunk_row = chunk_info['header'][0:chunk_info['columns']]
            empty_count = chunk_info['columns'] - len(header_chunk_row)
            while empty_count > 0:
                header_chunk_row.append(chunk_info['filler'])
                empty_count -= 1
            return header_chunk_row

        hdr = []
        for chunk in self.chunk_list:
            hdr += get_header_chunk(chunk)
        return hdr

    def __add__(self, other):  # Table
        if type(other) == Table:
            new = Table()
            new.add_chunk_list(self.chunk_list)
            new.add_chunk_list(other.chunk_list)
            return new
        else:
            raise TableError(f"{class_name(self)}: Невозможно добавить объект класса {type(other)} к объекту класса "
                             f"Table\n{inspect_info()}")

    def __len__(self):  # Table
        return self.rows

    def __getitem__(self, i):  # Table
        if i < 0:
            i = self.rows + i

        if -1 < i < self.rows:
            return TableRow(self, i)
        else:
            raise TableError(f"{class_name(self)}: В таблице нет строки с номером: {i}. Всего строк: {self.rows}\n"
                             f"{inspect_info()}")

    def __iter__(self):  # Table
        self._index = 0
        return self

    def __next__(self):  # Table
        if self._index >= self.rows:
            raise StopIteration()
        else:
            self._index += 1
            return TableRow(self, self._index - 1)

