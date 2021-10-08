import os
import shutil

f = open('client_secret.json', 'w')
f.write('')  # 何も書き込まなくてファイルは作成されました
f.close()

os.mkdir('files')

shutil.copyfile("./settings/const_.py", "./const.py")