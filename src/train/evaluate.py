# evaluate.py
import os
import sys
import json
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


def evaluate():
    device = torch.device(config.DEVICE)

    TEST_PATH  = os.path.join(root_dir,"dataset/data_processed/test.csv")
    CHECKPOINT_PATH = os.path.join(root_dir,"checkpoints/phobert_best.pt")

    # Tokenizer (same as training)
    tokenizer = AutoTokenizer.from_pretrained(
        config.MODEL_NAME,
        use_fast=False
    )

    # Test dataset & loader
    test_dataset = FakeNewsDataset(
        csv_path=TEST_PATH,
        tokenizer=tokenizer,
        max_len=config.MAX_SEQ_LENGTH
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
    
    # ==================================================
    # =========== SAVE ALL RESULTS TO JSON ==============
    # ==================================================
    output_dir = os.path.join(root_dir,"result/evaluation")
    os.makedirs(output_dir, exist_ok=True)

    report_dict = classification_report(
        all_labels,
        all_preds,
        digits=4,
        output_dict=True
    )

    results = {
        "test_accuracy": round(acc, 4),
        "test_macro_f1": round(macro_f1, 4),
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist()
    }

    json_path = os.path.join(output_dir, "evaluation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n All evaluation results saved to {json_path}")


if __name__ == "__main__":
    evaluate()
