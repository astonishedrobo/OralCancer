import json
import pandas as pd
import argparse
import os

TYPE_NUCLEI_DICT = {0: "UNK", 1: "Neoplastic", 2: "Inflammatory", 3: "Connective", 4: "Dead", 5: "Epithelial"}

def create_cell_prob_dist(json_path, prob_threshold=0.8):
    """
    Create a CSV file from a JSON file containing cell data.

    Args:
        json_path (str): Path to the JSON file.
        output_csv_path (str): Path to save the output CSV file.
        prob_threshold (float, optional): Probability threshold for marking cell types as "UNC" (Unclassified).

    Returns:
        None
    """
    with open(json_path, 'r') as f:
        input_data = json.load(f)

    data = []

    for patch_name, patch_data in input_data.items():
        for cell_id, cell_data in patch_data.items():
            type_dist = cell_data["type_dist"]
            type_probs = [type_dist.get(str(key), 0) for key in TYPE_NUCLEI_DICT.values()]
            
            # Check the type probability against the threshold
            if cell_data["type_prob"] < prob_threshold:
                cell_type = "UNC"
            else:
                cell_type = cell_data["type"]
            
            row = [
                patch_name,
                cell_id,
                *type_probs,
                cell_type,
                cell_data["type_prob"],
            ]
            data.append(row)

    columns = [
        "patch_name",
        "cell_id",
        *[key for key in TYPE_NUCLEI_DICT.values()],
        "type",
        "type_prob",
    ]

    df = pd.DataFrame(data, columns=columns)
    return df

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent_folder", type=str, default=None, help="Path to Parent Folder")
    parser.add_argument("--json_file", type=str, default=None, help="Path to Json File")
    parser.add_argument("--combine", type=bool, default=False)

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    parent_folder = args.parent_folder

    if args.combine:
        collated_df = pd.DataFrame()

    if parent_folder is not None:
        folders = sorted(os.listdir(parent_folder))
        
        for folder in folders:
            if os.path.isdir(os.path.join(parent_folder, folder)):
                json_path = os.path.join(parent_folder, folder, "instance_segmentation.json")
                print(json_path)
                df = create_cell_prob_dist(json_path)
                if args.combine:
                    collated_df = pd.concat([collated_df, df], ignore_index=True)
                    collated_df.reset_index()
                
                else:
                    save_path = os.path.join(parent_folder, folder, f"cell_prob_dist_{parent_folder.split('/')[-1]}.csv")
                    df.to_csv(save_path, index=False)

        if args.combine:
            save_path = os.path.join(parent_folder, f"cell_prob_dist_{parent_folder.split('/')[-1]}_combined.csv")
            collated_df.to_csv(save_path, index=False)
            print(f"File save to {save_path}")

    elif args.json_file is not None:
        df = create_cell_prob_dist(args.json_file)
        dir_name = os.path.dirname(args.json_file)
        save_path = os.path.join(dir_name, "instance_cell_prob_dist.csv")
        df.to_csv(save_path, index=False)
        print(save_path)

if __name__ == "__main__":
    main()