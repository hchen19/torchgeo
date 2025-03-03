# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""DeepGlobe Land Cover Classification Challenge datamodule."""

from typing import Any

import kornia.augmentation as K
import torch
from torch.utils.data import random_split

from ..datasets import DeepGlobeLandCover
from ..samplers.utils import _to_tuple
from ..transforms.transforms import _RandomNCrop
from .geo import NonGeoDataModule


class DeepGlobeLandCoverDataModule(NonGeoDataModule):
    """LightningDataModule implementation for the DeepGlobe Land Cover dataset.

    Uses the train/test splits from the dataset.
    """

    def __init__(
        self,
        batch_size: int = 64,
        patch_size: tuple[int, int] | int = 64,
        val_split_pct: float = 0.2,
        num_workers: int = 0,
        **kwargs: Any,
    ) -> None:
        """Initialize a new DeepGlobeLandCoverDataModule instance.

        Args:
            batch_size: Size of each mini-batch.
            patch_size: Size of each patch, either ``size`` or ``(height, width)``.
                Should be a multiple of 32 for most segmentation architectures.
            val_split_pct: Percentage of the dataset to use as a validation set.
            num_workers: Number of workers for parallel data loading.
            **kwargs: Additional keyword arguments passed to
                :class:`~torchgeo.datasets.DeepGlobeLandCover`.
        """
        super().__init__(DeepGlobeLandCover, 1, num_workers, **kwargs)

        self.patch_size = _to_tuple(patch_size)
        self.val_split_pct = val_split_pct

        self.aug = K.AugmentationSequential(
            K.Normalize(mean=self.mean, std=self.std),
            _RandomNCrop(self.patch_size, batch_size),
            data_keys=None,
            keepdim=True,
        )

    def setup(self, stage: str) -> None:
        """Set up datasets.

        Args:
            stage: Either 'fit', 'validate', 'test', or 'predict'.
        """
        if stage in ['fit', 'validate']:
            self.dataset = DeepGlobeLandCover(split='train', **self.kwargs)
            generator = torch.Generator().manual_seed(0)
            self.train_dataset, self.val_dataset = random_split(
                self.dataset, [1 - self.val_split_pct, self.val_split_pct], generator
            )
        if stage in ['test']:
            self.test_dataset = DeepGlobeLandCover(split='test', **self.kwargs)
