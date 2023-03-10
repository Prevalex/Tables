
"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------[ class TableBook ]--------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------"""


from tTable import Table
from alx import add_str, class_name, quote, inspect_info, dbg, get_datetime_stamp, del_if_exist, is_opened
from tLib import TableError, reorder_dict


class TableBook:  # TableBook

    index = 0
    tables_dic: dict = dict()

    def __str__(self):  # TableBook
        about = '\n' + '=' * 16 + '\n'
        about, _l = add_str(about, '{:<17}'.format(class_name(self)))
        about, _l = add_str(about, '{:<17}'.format('-' * _l))
        about, _l = add_str(about, '{:<17}'.format(f'Tables: {len(self.tables_dic)}'))

        tab_index = 0
        for title, table in self:
            _about = '-' * 16 + '\n'
            _about, _l = add_str(_about, '{:<17}{:<17}'.format(f'Table index:', f'{tab_index}'))
            _about, _l = add_str(_about, '{:<17}{:<17}'.format(f'Table title:', f'"{title}"'))
            _about, _l = add_str(_about, table.__str__().replace('\n', '\n  '))
            _about.replace('\n', '\n  ')
            tab_index += 1
            about += _about
        return about

    def __init__(self, **tables):  # TableBook
        self.index = 0
        self.tables_dic: dict = dict()
        if tables:
            for title, table in tables.items():
                self.add_table(title, table)

    def _check_title_(self, title: str, is_found=True) -> str:  # TableBook
        """
        Проверяет наличие (inclusion=True) или отсутствие (inclusion=False) имени в таблиці в списке имен
        Parameters
        ----------
        title :
        is_found :

        Returns
        -------

        """
        title = str(title).strip()
        if len(self.tables_dic) > 0:
            if title == '':
                title = list(self.tables_dic.keys())[0]
        if is_found:
            if title in self.tables_dic:
                return title
            else:
                raise TableError(f'{class_name(self)}: Таблица c именем "{title}" не найдена.\n'
                                 f'{inspect_info()}')
        else:
            if title in self.tables_dic:
                raise TableError(f'{class_name(self)}: Таблица с именем {title} уже существует.\n'
                                 f'{inspect_info()}')
        return title

    def get_table(self, title='') -> Table:  # TableBook
        title = self._check_title_(title)
        return self.tables_dic[title]

    def add_table(self, title: str, table: Table) -> None:  # TableBook
        title = self._check_title_(title, is_found=False)
        self.tables_dic[title] = table

    def new_table(self, title: str, table_data: list, selector=None, columns=None, headers=None, hdkeys=True, filler=None) -> None:
        title = self._check_title_(title, is_found=False)  # TableBook
        self.tables_dic[title] = Table(table_data, selector=selector, columns=columns, headers=headers, hdkeys=hdkeys, filler=filler)

    def del_table(self, title: str) -> None:  # TableBook
        title = self._check_title_(title)
        del self.tables_dic[title]

    def list_titles(self) -> list[str]:  # TableBook
        return list(self.tables_dic.keys())

    def reorder_titles(self, titles_list: list[str]) -> None:  # TableBook
        titles_list = list(self._check_title_(title) for title in titles_list)
        self.tables_dic = reorder_dict(self.tables_dic, titles_list)

    def __len__(self) -> int:  # TableBook
        return len(self.tables_dic)

    def __contains__(self, title) -> bool:  # TableBook
        return title in self.tables_dic

    def __getitem__(self, i: int | str) -> tuple[str | int, Table]:  # TableBook
        """
        Parameters
        ----------
        i : если i - целое число, то метод возвращает имя таблицы в книге и саму таблицу
            если i - имя таблицы в книге, то метод возвращает индекс таблицы и саму таблицу
        Returns
        -------

        """
        _titles = self.list_titles()

        if type(i) == str:
            if i in _titles:
                return _titles.index(i), self.tables_dic[i]
            else:
                raise TableError(f'{class_name(self)}: Таблица "{i}" не найдена.\n'
                                 f'{inspect_info()}')
        elif type(i) == int:
            if -1 < i < len(_titles):
                return _titles[i], self.tables_dic[_titles[i]]
            else:
                raise TableError(f'{class_name(self)}: Таблица с индексом [{i}] не найдена.\n'
                                 f'{inspect_info()}')

    def __iter__(self):  # TableBook
        self.index = 0
        return self

    def __next__(self):  # TableBook
        if self.index >= self.__len__():
            raise StopIteration()
        else:
            self.index += 1
            return self.__getitem__(self.index-1)

