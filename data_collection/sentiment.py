# FinBERT classifier: article title + summary → label and confidence.

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)


class FinBertLabeler:
    def __init__(self, model_path: str):
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.classifier = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )

    def label(self, articles: list[dict]) -> list[dict]:
        if not articles:
            return []
        results = self.classifier(
            [
                f"{article['title']}. {article['summary']}"
                for article in articles
            ],
            truncation=True,
            max_length=128,
        )
        return [
            {
                **article,
                "label": result["label"].lower(),
                "confidence": float(result["score"]),
            }
            for article, result in zip(articles, results, strict=True)
        ]
