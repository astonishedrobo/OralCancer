# -*- coding: utf-8 -*-
# Patched WSI Dataset used for inference, mainly for calculating embeddings
#
# @ Fabian Hörst, fabian.hoerst@uk-essen.de
# Institute for Artifical Intelligence in Medicine,
# University Medicine Essen

from typing import Callable, Tuple, List

import torch
from torch.utils.data import Dataset
from datamodel.wsi_datamodel import WSI
import os
from PIL import Image
import cv2


class PatchedWSIInference(Dataset):
    """Inference Dataset, used for calculating embeddings of *one* WSI. Wrapped around a WSI object

    Args:
        wsi_object (
        filelist (list[str]): List with filenames as entries. Filenames should match the key pattern in wsi_objects dictionary
        transform (Callable): Inference Transformations
    """

    def __init__(
        self,
        wsi_object: WSI,
        transform: Callable,
    ) -> None:
        # set all configurations
        assert isinstance(wsi_object, WSI), "Must be a WSI-object"
        assert (
            wsi_object.patched_slide_path is not None
        ), "Please provide a WSI that already has been patched into slices"

        self.transform = transform
        self.wsi_object = wsi_object

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, list[list[str, str]], list[str], int, str]:
        """Returns one WSI with patches, coords, filenames, labels and wsi name for given idx

        Args:
            idx (int): Index of WSI to retrieve

        Returns:
            Tuple[torch.Tensor, list[list[str,str]], list[str], int, str]:

            * torch.Tensor: Tensor with shape [num_patches, 3, height, width], includes all patches for one WSI
            * list[list[str,str]]: List with coordinates as list entries, e.g., [['1', '1'], ['2', '1'], ..., ['row', 'col']]
            * list[str]: List with patch filenames
            * int: Patient label as integer
            * str: String with WSI name
        """
        patch_name = self.wsi_object.patches_list[idx]

        patch, metadata = self.wsi_object.process_patch_image(
            patch_name=patch_name, transform=self.transform
        )

        return patch, metadata

    def __len__(self) -> int:
        """Return len of dataset

        Returns:
            int: Len of dataset
        """
        return int(self.wsi_object.get_number_patches())

    @staticmethod
    def collate_batch(batch: List[Tuple]) -> Tuple[torch.Tensor, list[dict]]:
        """Create a custom batch

        Needed to unpack List of tuples with dictionaries and array

        Args:
            batch (List[Tuple]): Input batch consisting of a list of tuples (patch, patch-metadata)

        Returns:
            Tuple[torch.Tensor, list[dict]]:
                New batch: patches with shape [batch_size, 3, patch_size, patch_size], list of metadata dicts
        """
        patches, metadata = zip(*batch)
        patches = torch.stack(patches)
        metadata = list(metadata)
        return patches, metadata

class PatchInference(Dataset):
    def __init__(self, patch_dir, transform: Callable) -> None:
        self.patch_dir = patch_dir
        self.transform = transform
        self.patch_list = sorted([file for file in os.listdir(patch_dir) if file.endswith('.png')])
        self.patch_list.sort()

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, dict]:
        patch_name = self.patch_list[idx]
        patch = Image.open(self.patch_dir / patch_name)
        # patch = cv2.imread(str(self.patch_dir / patch_name), cv2.IMREAD_UNCHANGED)
        # patch = cv2.cvtColor(patch, cv2.COLOR_BGRA2RGB)
        # patch = Image.fromarray(patch)
        if self.transform:
            patch = self.transform(patch)

        return patch

    def __len__(self) -> int:
        return len(self.patch_list)

    def get_patch_names(self) -> List[str]:
        return self.patch_list
