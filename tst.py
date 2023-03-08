from alx import add_str
import sys
from tLib import tg, xl_cell_style_title
from pprint import pprint
from tChunk import TableChunk
from tFormat import Formatter
from tTable import Table
from tRow import  TableRow
from tBook import TableBook
from tBookXL import TableBookXL

tg_lst, tg_tup, tg_dic = tg(5)

chunk_lst = TableChunk(tg_lst, columns=6)
print(chunk_lst)
for row in chunk_lst:
    pprint(row)

chunk_tup = TableChunk(tg_tup)
print(chunk_tup)
for row in chunk_tup:
    pprint(row)

chunk_dic = TableChunk(tg_dic, columns=4, headers=0)
print(chunk_dic)
for row in chunk_dic:
    pprint(row)
