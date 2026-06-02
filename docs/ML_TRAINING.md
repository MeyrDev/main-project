# ML-обучение модели риска

## Команды

Подготовить датасеты:

```bash
make prepare-datasets
```

Обучить модель:

```bash
make train
```

Показать путь к markdown-отчету:

```bash
make train-report
```

Прямой запуск через Docker Compose:

```bash
docker compose run --rm --no-deps app python -m app.ml.prepare_datasets_from_csv
docker compose run --rm --no-deps app python -m app.ml.train_model
```

## Файлы для демонстрации комиссии

- `data/train_dataset.csv` - обучающая выборка.
- `data/validation_dataset.csv` - отдельная валидационная выборка.
- `artifacts/risk_model.joblib` - сохраненный artifact модели.
- `artifacts/training_report.json` - подробный JSON-отчет обучения.
- `artifacts/training_report.md` - markdown-отчет на русском языке.
- `artifacts/validation_predictions.csv` - предсказания модели на validation dataset.

## Как подтвердить корректность обучения

Модель обучается только на `data/train_dataset.csv`. Проверка качества выполняется только на отдельном `data/validation_dataset.csv`. Пропуски в validation dataset заполняются медианами, рассчитанными по train dataset, поэтому validation не используется при обучении и не создает data leakage.

После обучения в `artifacts/training_report.md` доступны метрики `roc_auc`, `pr_auc`, `f1`, `precision`, `recall`, `accuracy`, `brier_score` и матрица ошибок. Файл `artifacts/validation_predictions.csv` показывает фактический класс, предсказанный класс, вероятность риска и использованные признаки для каждой строки validation dataset.
