import torch
from transformers import AutoModel

class SentimentModel(torch.nn.Module):
    def __init__(self, model_name, num_labels):
        super(SentimentModel, self).__init__()
        self.transformer = AutoModel.from_pretrained(model_name)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(
            self.transformer.config.hidden_size,
            num_labels
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        pooled = outputs.last_hidden_state[:, 0, :]
        x = self.dropout(pooled)
        return self.classifier(x)
