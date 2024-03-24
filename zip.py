
# shutil.make_archive(ozip, 'zip', ifile)

from tqdm import tqdm
import zipfile
import os

from zipfile import ZipFile
from tqdm import tqdm
import time 

def compress_folder(folder_path, output_zip_file):
    """
    Compresses a folder and its contents into a zip file with a progress bar, 
    preserving the top-level directory structure.
    """
    total_file_size = sum(os.path.getsize(os.path.join(root, f)) for root, _, files in os.walk(folder_path) for f in files)

    with ZipFile(output_zip_file, 'w') as zip_file:
        with tqdm(total= total_file_size, desc=f"Compressing {os.path.basename(folder_path)}") as pbar:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the archive path relative to the original folder (excluding the top level)
                    archive_path = os.path.relpath(file_path, os.path.dirname(folder_path))
                    zip_file.write(file_path, archive_path)
                    pbar.update(os.path.getsize(file_path))

# Example usage
folder_to_compress =  "/Users/camilotoruno/Documents/local_research_data/bldgs_idf_output_flags"
output_file = "/Users/camilotoruno/Documents/local_research_data/bldgs_idf_output_flags.zip"


starttime = time.time()
compress_folder(folder_to_compress, output_file)
print(f"Time to complete: {time.time()-starttime} sec")

