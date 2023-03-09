from alx import add_str
import sys
from tLib import tg, xl_cell_style_title
from pprint import pprint
from tChunk import TableChunk
from tFormat import Formatter
from tTable import Table
from tRow import TableRow
from tBook import TableBook
from tBookXL import TableBookXL

tg_lst, tg_tup, tg_dic = tg(5)
print()
pprint('pprint(tg_lst)')
pprint(tg_lst)
print()
pprint('pprint(tg_tup)')
pprint(tg_tup)
print()
pprint('pprint(tg_dic)')
pprint(tg_dic)
print()

chunk_lst = TableChunk(tg_lst, columns=6)
print(chunk_lst)
for row in chunk_lst:
    pprint(row)
print()
print(f'\nchunk_tup = TableChunk(tg_tup)')
chunk_tup = TableChunk(tg_tup)
print(chunk_tup)
for row in chunk_tup:
    pprint(row)
print()
print(f'\nchunk_tup_slice = chunk_tup[0::2]')
chunk_tup_slice = chunk_tup[0::2]
print(chunk_tup_slice)
for row in chunk_tup_slice:
    pprint(row)

print()
print(f'chunk_dic = TableChunk(tg_dic, columns=4, headers=0)')
chunk_dic = TableChunk(tg_dic, columns=4, headers=0)
print(chunk_dic)
for row in chunk_dic:
    pprint(row)

print()
print(f'chunk_dic_sliced = chunk_dic[-1, 0, -1]')
chunk_dic_sliced = chunk_dic[-1, 0, -1]
print(chunk_dic)
for row in chunk_dic:
    pprint(row)
print()
print("shunc_dic_select = TableChunk(tg_dic, select=['1','2','3','4'])")
chunk_dic_select = TableChunk(tg_dic, selector=['1','2','3','4'])
print(chunk_dic_select)
for row in chunk_dic_select:
    pprint(row)

print()
print("shunc_dic_select = TableChunk(tg_dic, select=[1,2,3,4])")
chunk_dic_select = TableChunk(tg_dic, selector=[1,2,3,4])
print(chunk_dic_select)
for row in chunk_dic_select:
    pprint(row)




