# train.py
import os
import sys
import random
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from transformers import AutoTokenizer, DataCollatorWithPadding
from tqdm import tqdm
import pandas as pd
import copy
from sklearn.metrics import f1_score

from src.train.dataset import FakeNewsDataset
from src.model.model import PhoBERTClassifier
import configs.config_train  as config


# =========================
# Reproducibility
# =========================
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# =========================
# Training for one epoch
# =========================
def train_epoch(model, dataloader, optimizer, scheduler, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch in tqdm(dataloader, desc="Training"):
        optimizer.zero_grad()

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = torch.nn.functional.cross_entropy(logits, labels)

        loss.backward()
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()

        preds = torch.argmax(logits, dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total

    return avg_loss, accuracy


# =========================
# Validation for one epoch
# =========================
def eval_epoch(model, dataloader, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            logits = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = torch.nn.functional.cross_entropy(logits, labels)

            total_loss += loss.item()

            preds = torch.argmax(logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total
    macro_f1 = f1_score(all_labels, all_preds, average="macro")

    return avg_loss, accuracy, macro_f1


# =========================
# Main training pipeline
# =========================
def train():
 
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    data_processed_dir(root_dir,"dataset/data_processed")
    
    TRAIN_PATH = os.path.join(data_processed_dir,"train.csv")
    VAL_PATH   = os.path.join(data_processed_dir,"val.csv")
    TEST_PATH  = os.path.join(data_processed_dir,"test")
    
    CHECKPOINT_PATH = os.path.join(os.path.abspath(os.path.join(data_processed_dir,"../..")),"checkpoints/phobert_best.pt")
    RESULT_PATH = os.path.join(os.path.abspath(os.path.join(data_processed_dir,"../..")),"result/train/training_history.csv")
    
    set_seed(config.RANDOM_SEED)
    device = torch.device(config.DEVICE)

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.MODEL_NAME,
        use_fast=False
    )

    # Datasets
    train_dataset = FakeNewsDataset(
        csv_path=TRAIN_PATH,
        tokenizer=tokenizer,
        max_len=config.MAX_SEQ_LENGTH
    )

    val_dataset = FakeNewsDataset(
        csv_path=VAL_PATH,
        tokenizer=tokenizer,
        max_len=config.MAX_SEQ_LENGTH
    )

    # Dynamic padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        collate_fn=data_collator
    )

    val_loader = DataLoader(
        val_dataset,
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

    # Optimizer
    optimizer = AdamW(
        model.parameters(),
        lr=config.LEARNING_RATE,
        weight_decay=config.WEIGHT_DECAY
    )

    # Scheduler
    total_steps = len(train_loader) * config.EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps
    )

    # History
    history = {
        "epoch": [],
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_macro_f1": []
    }

    # Early stopping
    best_val_loss = float("inf")
    best_model_state = None
    patience = 2
    patience_counter = 0

    # Training loop
    for epoch in range(config.EPOCHS):
        print(f"\nEpoch {epoch + 1}/{config.EPOCHS}")

        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, scheduler, device
        )

        val_loss, val_acc, val_macro_f1 = eval_epoch(
            model, val_loader, device
        )

        history["epoch"].append(epoch + 1)
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        history["val_macro_f1"].append(val_macro_f1)

        print(
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Acc: {val_acc:.4f} | "
            f"Val Macro-F1: {val_macro_f1:.4f}"
        )

        # ===== Early Stopping =====
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            print(f"EarlyStopping counter: {patience_counter}/{patience}")

            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    # Save best model
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
    torch.save(best_model_state, CHECKPOINT_PATH)
    print(f"Best model saved to {CHECKPOINT_PATH}")

    # Save history
    df = pd.DataFrame(history)
    os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
    df.to_csv(RESULT_PATH, index=False)
    print("Training history saved to training_history.csv")


if __name__ == "__main__":
    train("g:\VsCode\Python\ANM\Fake_news_Classify\dataset\data_processed")
