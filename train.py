import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer
from torch.utils.data import Dataset, DataLoader
from model import SentimentModel
from preprocessing import clean_text
from tqdm import tqdm

MODEL_NAME = "xlm-roberta-base"
EPOCHS = 1
BATCH_SIZE = 16
LR = 2e-5



class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            padding="max_length",
            truncation=True,
            max_length=64,
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx])
        }

def main():
    df = pd.read_csv("data/large_multilingual_dataset.csv")
    df["text"] = df["text"].apply(clean_text)

    le = LabelEncoder()
    df["label"] = le.fit_transform(df["sentiment"])

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_ds = SentimentDataset(X_train.tolist(), y_train.tolist(), tokenizer)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = SentimentModel(MODEL_NAME, 8).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    loss_fn = torch.nn.CrossEntropyLoss()

    model.train()
    for epoch in tqdm(range(EPOCHS), desc="Training Epochs"):
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} Batches", leave=False):
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, mask)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1} Loss: {total_loss/len(train_loader):.4f}")

    torch.save(model.state_dict(), "sentiment_model.pt")
    print("Model saved.")

if __name__ == "__main__":
    main()
