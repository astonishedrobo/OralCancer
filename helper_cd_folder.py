import subprocess

folders = ["NORMAL", "OSMF", "OSCC/WD", "OSCC/MD", "OSCC/PD"]
sub_folders = ["train", "validation", "test"]

for sub_folder in sub_folders:
    for folder in folders:
        script_command = f"python Utils/cell_detection_folder.py --data_folder=/media/KutumLabGPU/split_data_png_new_padded/{sub_folder}/{folder} --out_folder=/media/KutumLabGPU/split_data_png_new_padded/{sub_folder}/{folder}"
        subprocess.run(script_command, shell=True)
