import zipfile
import os
import datetime

if not os.path.exists('versiones_zip'):
    os.makedirs('versiones_zip')

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
zip_name = f"versiones_zip/backup_{timestamp}.zip"

folders_to_zip = ['app', 'assets', 'data', 'chroma_db']
files_to_zip = ['README.md', 'requirements.txt', 'run.bat']

print(f"Creating backup: {zip_name}...")

try:
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in folders_to_zip:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    # Exclude __pycache__
                    if '__pycache__' in dirs:
                        dirs.remove('__pycache__')
                    
                    for file in files:
                        if file.startswith('~$'):
                            continue
                        file_path = os.path.join(root, file)
                        # Avoid zipping the zip file itself if it somehow ends up in the path (unlikely with this logic)
                        zipf.write(file_path, file_path)
            else:
                print(f"Warning: Folder '{folder}' not found.")
        
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file, file)
            else:
                print(f"Warning: File '{file}' not found.")

    print(f"Backup created successfully: {zip_name}")

except Exception as e:
    print(f"Error creating backup: {e}")
