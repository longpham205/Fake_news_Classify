# evaluate.py
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DataCollatorWithPadding
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    f1_score,
    confusion_matrix
)

from src.train.dataset import FakeNewsDataset
from src.model.model import PhoBERTClassifier
import configs.config_train as config


def evaluate(data_processed_dir):
    device = torch.device(config.DEVICE)

    TEST_PATH  = os.path.join(data_processed_dir,"test.csv")
    CHECKPOINT_PATH = os.path.join(os.path.abspath(os.path.join(data_processed_dir,"..")),"checkpoint/phobert_best.pt")

    # Tokenizer (same as training)
    tokenizer = AutoTokenizer.from_pretrained(
        config.MODEL_NAME,
        use_fast=False
    )

    # Test dataset & loader
    test_dataset = FakeNewsDataset(
        csv_path=TEST_PATH,
        tokenizer=tokenizer,
        max_len=config.MAX_LEN
    )

    data_collator = DataCollatorWithPadding(tokenizer)

    test_loader = DataLoader(
        test_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        collate_fn=data_collator
    )

    # Model
    model = PhoBERTClassifier(
        model_name=config.MODEL_NAME,
        num_classes=config.NUM_CLASSES,
        dropout_rate=config.DROPOUT_RATE,
        freeze_encoder=False
    ).to(device)

    # Load best trained weights
    model.load_state_dict(
        torch.load(CHECKPOINT_PATH, map_location=device)
    )
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            preds = torch.argmax(logits, dim=1)

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro")
    cm = confusion_matrix(all_labels, all_preds)

    print(f"\nTest Accuracy   : {acc:.4f}")
    print(f"Test Macro-F1   : {macro_f1:.4f}\n")

    print("Classification Report:")
    print(classification_report(all_labels, all_preds, digits=4))

    print("Confusion Matrix:")
    print(cm)


if __name__ == "__main__":
    evaluate("g:\VsCode\Python\ANM\Fake_news_Classify\dataset\data_processed")
