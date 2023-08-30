import os
import zipfile
import time
import shutil

def get_logtype_from_filename(filename):
	if ('Match_GameLog_' in filename) and (len(filename) >= 30) and ('.dat' in filename):
		return 'GameLog'
	if (filename.count('.') != 3) or (filename.count('-') != 4) or ('.txt' not in filename):
		return 'NA'
	elif (len(filename.split('-')[1].split('.')[0]) != 4) or (len(filename.split('-')[2]) != 4):
		return 'NA'
	else:
		return 'DraftLog'

root_folder = os.getcwd()
os.chdir('C:\\')
files_dict = {}

if not os.path.exists(root_folder+'\\to_zip_mtgo_tracker'):
    os.makedirs(root_folder+'\\to_zip_mtgo_tracker')

for (root,dirs,files) in os.walk('C:\\'):
    for i in files:
        if get_logtype_from_filename(i) == 'GameLog':
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
        elif get_logtype_from_filename(i) == 'DraftLog':
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