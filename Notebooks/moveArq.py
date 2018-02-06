""" Mover arquivos """
import os
import shutil

src = 'D:\\Users\\47020753817\\Downloads\\WinPython-64bit-3.5.3.1Qt5\\AJNA\\ajna\\2017'
dst = 'D:\\Users\\47020753817\\Downloads\\WinPython-64bit-3.5.3.1Qt5\\AJNA\\ajna\\busca\\busca\\static\\busca\\2017'

for file in os.listdir(src):
    print(file)  # testing
    src_file = os.path.join(src, file)
    dst_file = os.path.join(dst, file)
    shutil.move(src_file, dst_file)
