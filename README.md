# BTC hourly direction

This project uses XGBoost to predict whether Bitcoin will rise or fall over the next hour, combining market features from BTC, ETH, SOL, and XRP with FinBERT sentiment from Bitcoin news.

## Data

The dataset covers 2025-08-09 through 2026-02-10, with hourly Binance market data in `data/market_hourly.parquet` and 40,172 article-level sentiment labels and confidence scores in `data/sentiment_events.parquet`. Alongside these extracts, `data/feature_store.parquet` preserves the original feature matrix used in the research, allowing the notebooks to reproduce the evaluation without rebuilding every predictor from raw data.

After aligning the features with the next-hour target, the modeling table contains **4,440 hours** and **136 predictors**, divided chronologically into training, calibration, and test periods as follows (all timestamps are UTC):

| Split | UTC dates | Hours |
|---|---|---:|
| Train | 2025-08-09 05:00 to 2025-12-16 16:00 | 3,108 |
| Calibration | 2025-12-16 17:00 to 2026-01-04 08:00 | 444 |
| Test | 2026-01-04 09:00 to 2026-02-10 12:00 | 888 |

## Methodology

The model predicts whether the next hourly Binance BTC close will be higher than the current close, using returns, volatility, moving averages, funding and positioning, and news sentiment as predictors. A shallow, regularized XGBoost classifier is fitted on the training period, after which Platt scaling uses the calibration period to adjust its probability estimates.

To select predictions, confidence is measured as the estimated probability of the predicted direction, `max(p, 1-p)`. Several confidence threshold are evaluated on the calibration period, and the one with the highest accuracy among those retaining at least 40 predictions is chosen before evaluating the test period.

## Results

The calibration procedure selected a confidence cutoff of **0.53**, which retained 34.3% of test hours and produced the following results:

| Predictions | Hours | Coverage | Accuracy |
|---|---:|---:|---:|
| All test hours | 888 | 100% | 48.20% |
| Confidence ≥ 0.53 | 305 | 34.3% | **55.08%** |


## Example

To reproduce the results, install the dependencies in `requirements.txt` and run [`01_feature_processing.ipynb`](notebooks/01_feature_processing.ipynb) to build the modeling table, followed by [`02_model_training.ipynb`](notebooks/02_model_training.ipynb) to train, calibrate, and evaluate the model.

The hourly market and news collection job is also included in [`data_collection/`](data_collection/README.md), with its setup documented there and additional dependencies listed in `requirements-collection.txt`.
