from alx import add_str
import sys
from tLib import tg, xl_cell_style_title
from pprint import pprint
from tFormat import Formatter
from tTable import Table
from tRow import  TableRow
from tBook import TableBook
from tBookXL import TableBookXL

"""---------------------------------------------------"""

dat_lst, dat_tup, dat_dic = tg(10)
print('\n>>> dat_lst')
pprint(dat_lst, width=180)

print('\n>>> dat_dic')
pprint(dat_dic, width=180)

dat_dic[3].pop('3')
print("\n>>> dat_dic after: dat_dic[3].pop('3')")
pprint(dat_dic, width=180)

dat_lst[2] = dat_lst[2][0:2]
dat_lst[7] = []
print("\n>>> dat_dic after: dat_lst[2] = dat_lst[2][0:2], dat_lst[7] = []")
pprint(dat_lst, width=180)

tab_lst_obj = Table(dat_lst, selector=[0,9,1,8,2,7,3,6])
print('\n>>> tab_lst_obj = Table(dat_lst, selector=[0,9,1,8,2,7,3,6])')
print(tab_lst_obj)
pprint(tab_lst_obj.get_table_data(),width=180)
print()

print('\n>>> dat_dic after: .pop(0), .pop(0)')
dat_dic.pop(0)
dat_dic.pop(0)
pprint(dat_dic, width=180)

tab_dic_obj = Table(dat_dic, columns=5, selector=['8','2','6','4'])
print("\n>>> tab_dic_obj after: columns=4,selector=['8','2','6','4']")
print(tab_dic_obj)
pprint(tab_dic_obj.get_table_data())

print()
print(f'\n>>>row_3_lst_obj = TableRow(tab_lst_obj, 3)')
row_3_lst_obj = TableRow(tab_lst_obj, 3)
print(row_3_lst_obj)

print()
print(f'\n>>> tab_lst_obj[3]')
print(tab_lst_obj[3])

print()
print(f'\n>>> row_4_dic_obj = TableRow(tab_dic_obj, 4)')
row_4_dic_obj = TableRow(tab_dic_obj, 4)
print(row_4_dic_obj)

print('\n>>> tab_dic_obj[4]')
print(tab_dic_obj[4])

print()
print('\n>>> list(item for item in row_4_dic_obj)')
print(list(item for item in row_4_dic_obj))
print('\nlist(row_4_dic_obj[i] for i in range(len(row_4_dic_obj)))')
print(list(row_4_dic_obj[i] for i in range(len(row_4_dic_obj))))

print()
print('\n>>> list(item for item in row_3_lst_obj)')
print(list(item for item in row_3_lst_obj))
print('\n>>> list(row_3_lst_obj[i] for i in range(len(row_3_lst_obj)))')
print(list(row_3_lst_obj[i] for i in range(len(row_3_lst_obj))))

print()
print('\n>>> for row_index in range(len(tab_td)):')
ptb = []
for row_index in range(len(tab_dic_obj)):
    pls = []
    for col_index in range(tab_dic_obj.columns):
        pls.append(tab_dic_obj[row_index][col_index])
    ptb.append(pls)
pprint(ptb, width=180)

print()
print('\n>>>for row_index in range(len(tab_tl)):')
ptb = []
for row_index in range(len(tab_lst_obj)):
    pls = []
    for col_index in range(tab_lst_obj.columns):
        pls.append(tab_lst_obj[row_index][col_index])
    ptb.append(pls)
pprint(ptb, width=180)

print("\n=== xlboo= = TableBookXL('!!!.xls')\n=== tablebook = xlbook.table_book")
xlbook = TableBookXL('!!!.xls')
tablebook = xlbook.table_book

print(f"TableBookXL('!!!.xls').table_book")
print(tablebook)

print('>>> for title, table in tablebook:')
for title, table in tablebook:
    print(f'>>> title="{title}"')
    print(table)
    print(f'\n>>> get_table_data()')
    pprint(table.get_table_data(), width=180)

print("\n===xlbook.save('+++.xlsx')")
xlbook.save('+++.xlsx')

xl = TableBookXL('!!!.xlsx')
book = xl.tablebook()
for title, table in book:
    print()
    print(f'---[{title}]----')
    print()
    for row in table:
        pprint(row.get_row_data(), width=180)

tab_sum_obj = tab_lst_obj + tab_dic_obj
print('\n>>> tab_sum_obj = tab_lst_obj + tab_dic_obj')
print(tab_sum_obj)

print('\n>>> tab_lst_obj.get_table_data()')
pprint(tab_lst_obj.get_table_data(), width=180)
print('\n>>> tab_dic_obj.get_table_data()')
pprint(tab_dic_obj.get_table_data(), width=180)
print('\n>>> tab_sum_obj.get_table_data()')
pprint(tab_sum_obj.get_table_data(), width=180)

book = TableBook()
book.add_table('ListMade', tab_lst_obj)
book.add_table('DictMade', tab_dic_obj)
book.add_table('UnionMade', tab_sum_obj)

print('\n>>> book = TableBook()')
print(book)

#sys.exit(0)


print()
print('=================================================================')
print()
filename = r'D:\aWrk\PYTHON\PyCharm\PyCat\.catrack\DST_MUK_2023-03-03.json'

jtab = Table(filename, selector=['src_index', 'part_vendor', 'part_number', 'part_name', 'net_price', 'on_stock'])
print(jtab)

xl = TableBookXL()
xl.add_sheet('MUK PriceList', jtab, Formatter(template_data=jtab.get_table_data()))
xl.get_formatter().set_row_style(0, xl_cell_style_title)

print('HERE')
xl.save('MUK PriceList.xlsx', header=True)
#xl.save('ERC PriceList.xlsx')
print('WHERE')
xl.close()


"""---------------------------------"""
"""---------------------------------"""
"""---------------------------------"""

sys.exit(0)
index = 0
styles = dict()

def up(style):
    global index
    styles.update({index: style})
    index += 1

"""Number formats"""
up("Comma")
up("Comma [0]")
up("Currency")
up("Currency [0]")
up("Percent")
"""Informative"""
up("Calculation")
up("Total")
up("Note")
up("Warning Text")
up("Explanatory Text")
"""Text styles"""
up("Title")
up("Headline 1")
up("Headline 2")
up("Headline 3")
up("Headline 4")
up("Hyperlink")
up("Followed Hyperlink")
up("Linked Cell")
"""Comparisons"""
up("Input")
up("Output")
up("Check Cell")
up("Good")
up("Bad")
up("Neutral")
"""Highlights"""
up("Accent1")
up("20 % - Accent1")
up("40 % - Accent1")
up("60 % - Accent1")
up("Accent2")
up("20 % - Accent2")
up("40 % - Accent2")
up("60 % - Accent2")
up("Accent3")
up("20 % - Accent3")
up("40 % - Accent3")
up("60 % - Accent3")
up("Accent4")
up("20 % - Accent4")
up("40 % - Accent4")
up("60 % - Accent4")
up("Accent5")
up("20 % - Accent5")
up("40 % - Accent5")
up("60 % - Accent5")
up("Accent6")
up("20 % - Accent6")
up("40 % - Accent6")
up("60 % - Accent6")
up("Pandas")

ft = Formatter(index='Style Index', test='Style ID', Num='Sample Number', num='Sample number', text='Text')
tab = []
for row in range(len(styles)):
    if row%3 != 0:
        tab.append([row, styles[row], 100, 0.01, 'sample text', 'extra_cell:', 44])
    else:
        tab.append([row, styles[row], 100])
    ft.set_row_style_segment(row, 'test', styles[row])

XL = XLBook()
XL.load(tab)
XL.save('openpyxl_styles_test.xlsx', ft)

wb = Workbook(write_only=True)
ws = wb.create_sheet()

