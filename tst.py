from alx import add_str
import sys
from alx import read_pydata_from_json_file, class_name
from tLib import tg, test_keys, get_array_keys, lapse
from pprint import pprint
from tChunk import TableChunk
from tFormat import Formatter
from tTable import Table
from tRow import TableRow
from tBook import TableBook
from tBookXL import TableBookXL
import datetime

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
pprint(tg_dic)
chunk_dic = TableChunk(tg_dic, columns=4, headers=0)
print(chunk_dic)
for row in chunk_dic:
    pprint(row)

print()
print(f'chunk_dic_sliced = chunk_dic[-1, 0, -1]')
chunk_dic_sliced = chunk_dic[-1: 0: -1]
print(chunk_dic)
for row in chunk_dic:
    pprint(row)
print()
print("shunc_dic_select = TableChunk(tg_dic, select=['1','2','3','4'])")
chunk_dic_select = TableChunk(tg_dic, select_cols=['1', '2', '3', '4'])
print(chunk_dic_select)
for row in chunk_dic_select:
    pprint(row)

print()
print("shunc_dic_select = TableChunk(tg_dic, select=[1,2,3,4])")
chunk_dic_select = TableChunk(tg_dic, select_cols=['1', '2', '3', '4'])
print(chunk_dic_select)
for row in chunk_dic_select:
    pprint(row)

dst = read_pydata_from_json_file(r'D:\aWrk\PYTHON\PyCharm\PyCat\Samples\DST_ERC.json')
src = read_pydata_from_json_file(r'D:\aWrk\PYTHON\PyCharm\PyCat\Samples\SRC_ERC.json')

print(f'test_keys(src)={test_keys(src)}')
print(f'test_keys(dst)={test_keys(dst)}')

erc_chunk = TableChunk(src, select_cols=['vendor', 'gname', 'sprice', 'ddp', 'whs'], columns=10)
print(f'\nerc_chunk\n{erc_chunk}')

print(f'\nerc_chunk.get_chunk_headers()=\n{erc_chunk.get_chunk_headers()}')
for i in range(5):
    print(erc_chunk[i])

erc_slice = erc_chunk[0:0]
print(erc_slice)










