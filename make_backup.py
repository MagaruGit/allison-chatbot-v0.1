import zipfile
import os
import datetime

# Configuración
BACKUP_DIR = 'versiones_zip'
EXCLUDE_DIRS = {BACKUP_DIR, '__pycache__', '.git', '.vscode', 'venv', 'env', '.idea', 'data_vias_limpia'} # Excluyo data_vias_limpia si es muy pesado, pero el usuario dijo "todo". Lo dejaré si no es gigante. Mejor lo incluyo.
# Re-pensando: data_vias_limpia parece contener CSVs procesados. Mejor incluirlos para tener un backup completo.
EXCLUDE_DIRS = {BACKUP_DIR, '__pycache__', '.git', '.vscode', 'venv', 'env', '.idea'}
EXCLUDE_FILES = {'.DS_Store', 'Thumbs.db'}
EXCLUDE_EXTENSIONS = {'.pyc', '.pyo', '.pyd'}

def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = os.path.join(BACKUP_DIR, f"backup_completo_{timestamp}.zip")

    print(f"Iniciando respaldo en: {zip_name}...")

    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('.'):
                # Modificar dirs in-place para saltar directorios excluidos
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    if file in EXCLUDE_FILES:
                        continue
                    
                    _, ext = os.path.splitext(file)
                    if ext in EXCLUDE_EXTENSIONS:
                        continue
                        
                    # No incluir el propio zip que se está creando
                    if file == os.path.basename(zip_name):
                        continue

                    file_path = os.path.join(root, file)
                    # Guardar en el zip con la ruta relativa
                    arcname = os.path.relpath(file_path, '.')
                    
                    # print(f"Agregando: {arcname}") # Comentado para no saturar la terminal
                    zipf.write(file_path, arcname)

        print(f"Backup creado exitosamente: {zip_name}")
        return zip_name

    except Exception as e:
        print(f"Error creando el respaldo: {e}")
        return None

if __name__ == "__main__":
    create_backup()
