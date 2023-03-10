import xlrd
from time import time

from openpyxl import load_workbook
from alx import inspect_info, dbg


class TableError(Exception):
    pass

xls_ext  = '.xls'
xlsx_ext = '.xlsx'
xltx_ext = '.xltx'
json_ext = '.json'
csv_ext  = '.csv'

""" """

excel_default_style = 'Normal'
excel_default_type = "General"

xl_cell_type_text = '@'
xl_cell_type_int = '0'
xl_cell_type_perc = '0.00%'
xl_cell_type_float = '#,##0.00'
xl_cell_type_gen = 'General'

xl_cell_style_title = 'Check Cell'
xl_cell_style_simple = 'Output'
xl_cell_style_note = 'Note'

""" ----- XLRD ----- 
Types: ( type = cell.ctype ) 
where ctype:    https://xlrd.readthedocs.io/en/latest/api.html?highlight=.row#xlrd.sheet.Cell
"""
XL_CELL_EMPTY	= 0	 # empty string ''
XL_CELL_TEXT	= 1	 # a Unicode string
XL_CELL_NUMBER	= 2	 # float
XL_CELL_DATE	= 3	 # float
XL_CELL_BOOLEAN	= 4	 # int; 1 means TRUE, 0 means FALSE
XL_CELL_ERROR	= 5	 # int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
XL_CELL_BLANK	= 6	 # empty string ''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used.


def tg(size):
    """  Генератор массивов для тестирования  """
    list_array = list()
    for irow in range(size):
        row = []
        for icol in range(size):
            row.append('L:R'+ str(irow) + 'C' + str(icol))
        list_array.append(row)

    tuple_array = list()
    for irow in range(size):
        row = []
        for icol in range(size):
            row.append('T:R' + str(irow) + 'C' + str(icol))
        tuple_array.append(tuple(row))
    tuple_array = tuple(tuple_array)

    dict_array = []
    for irow in range(size):
        row = {}
        for icol in range(size):
            row.update({str(icol): 'D:R' + str(irow) + 'C' + str(icol)})
        dict_array.append(row)
    return list_array, tuple_array, dict_array


def eval_index(index, size, slicer=None):
    """
    Вычисляет правильный индекс и проверяет его вхождение в пределы size.

    Parameters
    ----------
    index : Индекс для проверки
    size : Размер массива, который индексируется
    slicer : Список строк, которые сотались после предыдущего слайсинга [start, stop, step]

    Returns
    -------
    Скорректированный Индекс в массиве или -1, если индекс вышел за пределы списка

    """
    if slicer is None:
        if index < 0:
            index += size
        if 0 <= index < size:
            ret = index
        else:
            ret = -1
    else:
        i = eval_index(index, len(slicer))
        if i >= 0:
            ret = slicer[i]
        else:
            ret = i
    return ret


def get_test_indexes(total_rows) -> list:
    if total_rows < 9:
        _rows = set(list(range(total_rows)))
    else:
        _start = {0, 1, 2}
        _middle = int(round(total_rows / 2, 0))
        _middle = {_middle - 1, _middle, _middle + 1}
        _finish = {total_rows - 1, total_rows - 2, total_rows - 3}
        _rows = _start | _middle | _finish
    return list(_rows)


def test_keys(dic_array):
    key_array = []
    for row_index in get_test_indexes(len(dic_array)):
        key_array.append(list(dic_array[row_index].keys()))
    return all([set(row) == set(key_array[0]) for row in key_array])


def lapse(func):
    """
    Декоратор для замера времени выполнения функции в секундах
    https://sumit-ghosh.com/posts/demystifying-decorators-python/

    Parameters
    ----------
    func : функция, время исполнения которой замеряется

    Returns
    -------
    """
    def wrapper(*args, **kwargs):
        start = time()
        return_value = func(*args, **kwargs)
        end = time()
        print(f'[*] Время выполнения: {round(end-start,3)} секунд.')
        return return_value
    return wrapper


def get_array_keys(dic_array):
    key_array = []
    key_list = list(dic_array[0].keys())
    for row_dic in dic_array:
        key_array.append(list(row_dic.keys()))
    if all([set(row) == set(key_list) for row in key_array]):
        return key_list
    else:
        return []


def reorder_dict(src_dic: dict, key_list: list) -> dict:
    """
    Перестраивает словарь таким образом, что бы порядок следования пар ключ-значение соответствовал порядку в key_list.
    Использует тот факт, что в современно питоне (>3.7) словари таки сохраняют упорядоченность

    Parameters
    ----------
    src_dic : словарь
    key_list : список ключей

    Returns
    -------
    словарь, упорядоченный по key_list
    """
    _key_lst: list = list(src_dic.keys())
    _lst_lst: list = list(str(e) for e in key_list)

    _key_lst.sort()
    _lst_lst.sort()

    if _key_lst == _lst_lst:
        dst_dic = dict()
        for key in key_list:
            dst_dic[key] = src_dic[key]
    else:
        raise TableError(f'Ключи в словаре и списке не совпадают: '
                         f'Ключи:  {",".join(_key_lst)}; '
                         f'Список: {",".join(_lst_lst)}\n'
                         f'{inspect_info()}')
    return dst_dic

"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------[ Non-Class ROUTINES ]-----------------------------------------------------
---------------------------------------------------------------------------------------------------------------------"""


def read_xls_sheet_data(ws) -> list[list[any]]:
    table_data = list()
    for row_index in range(ws.nrows):
        row_data = list()
        for cell in ws.row(row_index):
            row_data.append(cell.value)
        table_data.append(row_data)
    return table_data


def read_xls_sheet(xls_file_name: str, sheet_id=0) -> list[list[any]]:
    xls_info = open_xls_book(xls_file_name)
    wb = xls_info['wb']

    if type(sheet_id) == int:
        ws = wb.sheet_by_index(sheet_id)
    elif type(sheet_id) == str:
        ws = wb.sheet_by_name(sheet_id)
    else:
        raise TableError(f'sheet_id type {type(sheet_id)} is unsupported. Use int for sheet index or str for '
                         f'sheet name\n{inspect_info()}')
    table_data = read_xls_sheet_data(ws)
    return table_data


def close_xls_book(wb):
    wb.release_resources()


def open_xls_book(xls_file_name: str) -> dict:
    """

    Parameters
    ----------
    xls_file_name : Имя файла

    Returns
    -------
    xls_info - словарь параметров workbook {'wb': wb,
                                            'ws_number: <число листов>',
                                            'ws_names: <список имен листов (упорядочен)>
    """
    """ not used here:
            sheet_by_name(sheet_name)
            sheet_by_index(sheetx)
        """
    xls_info = {}
    wb = xlrd.open_workbook(xls_file_name)
    #  wb = xlrd.open_workbook(xls_file_name, formatting_info=True)

    xls_info['wb'] = wb
    xls_info['ws_number'] = wb.nsheets
    xls_info['ws_names'] = wb.sheet_names()

    return xls_info


def read_xlsx_sheet(ws) -> list[list[any]]:
    table = []
    for row_tuple in ws.values:
        """ row_tuple имеет тип tuple """
        row_lst = list(row_tuple)
        table.append(row_lst)
    return table


def read_xlsx_book(xlsx_file_name) -> list[list[any]]:
    wb = load_workbook(xlsx_file_name, read_only=True, data_only=True)
    ws = wb.active

    table = read_xlsx_sheet(ws)
    wb.close()
    return table
