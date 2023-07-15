import os
import zipfile
import time
import shutil

root_folder = os.getcwd()
os.chdir('C:\\')
files_dict = {}

if not os.path.exists(root_folder+'\\to_zip_mtgo_tracker'):
    os.makedirs(root_folder+'\\to_zip_mtgo_tracker')

for (root,dirs,files) in os.walk('C:\\'):
    for i in files:
        if ('Match_GameLog_' not in i) or (len(i) < 30) or (i[-4:] != '.dat'):
            pass
        else:
            os.chdir(root)
            if i in files_dict:
                files_dict[i].append(time.mktime(time.strptime(time.ctime(os.path.getmtime(i)))))
            else:
                files_dict[i] = [time.mktime(time.strptime(time.ctime(os.path.getmtime(i))))]

            try:
                shutil.copy(i,root_folder+'\\to_zip_mtgo_tracker')
                os.chdir(root)
            except shutil.SameFileError:
                pass
        
        if (i.count(".") != 3) or (i.count("-") != 4) or (".txt" not in i):
            pass
        elif (len(i.split('-')[1].split('.')[0]) != 4) or (len(i.split('-')[2]) != 4):
            pass
        else:
            os.chdir(root)
            try:
                shutil.copy(i,root_folder+'\\to_zip_mtgo_tracker')
                os.chdir(root)
            except shutil.SameFileError:
                pass

os.chdir(root_folder+'\\to_zip_mtgo_tracker')
for (root,dirs,files) in os.walk(root_folder+'\\to_zip_mtgo_tracker'):
    for i in files:
        try:
            os.utime(i,(min(files_dict[i]), min(files_dict[i])))
        except KeyError:
            pass

os.chdir(root_folder)

with zipfile.ZipFile(root_folder+'\\MTGO-Log-Files.zip', "w") as zipf:
    for root, dirs, files in os.walk(root_folder+'\\to_zip_mtgo_tracker'):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, root_folder+'\\to_zip_mtgo_tracker'))

os.chdir(root_folder)

shutil.rmtree(root_folder+'\\to_zip_mtgo_tracker')