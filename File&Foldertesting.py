# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 17:44:17 2019

@author: Asif Towheed
"""

import os

PATH = os.getcwd().replace('\\','/')

for subdir, dirs, files in os.walk(PATH):
    print('subdir', subdir)
    print('dirs', dirs)
    print('files', files)
    
print('---------FOR FOLDERS --------------------------------------------')
for filename in os.listdir(PATH):
    if not os.path.isfile(filename):
        print(filename)
    
print('---------FOR FILES --------------------------------------------')
for filename in os.listdir(PATH):
    if os.path.isfile(filename):
        print(filename)



    
    