# model.py

import torch
import torch.nn as nn
from transformers import AutoModel


class PhoBERTClassifier(nn.Module):
    def __init__(
        self,
        model_name: str,
        num_classes: int,
        dropout_rate: float = 0.1,
        freeze_encoder: bool = False
    ):
        """
        PhoBERT-based classifier for text classification

        Args:
            model_name (str): HuggingFace model name (e.g. vinai/phobert-base)
            num_classes (int): number of output classes
            dropout_rate (float): dropout probability
            freeze_encoder (bool): whether to freeze PhoBERT encoder
        """
        super().__init__()

        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        if freeze_encoder:
            for param in self.encoder.parameters():
                param.requires_grad = False

        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )

        # CLS token embedding
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        cls_embedding = self.dropout(cls_embedding)

        logits = self.classifier(cls_embedding)
        return logits
