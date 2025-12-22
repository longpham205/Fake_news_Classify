# dataset.py

import torch
from torch.utils.data import Dataset
import pandas as pd


class FakeNewsDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_len):
        """
        Args:
            csv_path (str): path to processed CSV file
            tokenizer: HuggingFace tokenizer (PhoBERT)
            max_len (int): maximum sequence length
        """
        self.df = pd.read_csv(csv_path)

        # Validate required columns
        if "text" not in self.df.columns or "label" not in self.df.columns:
            raise ValueError("CSV file must contain 'text' and 'label' columns")

        self.texts = self.df["text"].astype(str).tolist()
        self.labels = self.df["label"].astype(int).tolist()

        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }
