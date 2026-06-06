# Отчет об обучении ML-модели

## Использованные датасеты

- Обучающая выборка: `data/train_dataset.csv`
- Валидационная выборка: `data/validation_dataset.csv`
- Количество строк в train dataset: `500`
- Количество строк в validation dataset: `300`
- Распределение target в train: `{0: 389, 1: 111}`
- Распределение target в validation: `{0: 233, 1: 67}`

Модель обучалась на `train_dataset.csv`, а проверка качества выполнялась на отдельном `validation_dataset.csv`.

## Признаки модели

- `log_revenue`
- `log_debt_amount`
- `debt_ratio`
- `overdue_days_30`
- `overdue_days_90`
- `disputes_count`
- `transactions_count`
- `employees_count`
- `low_transactions_flag`

Целевая колонка: `target`.

## Алгоритм обучения

Использован алгоритм `GradientBoostingClassifier + IsotonicCalibration`.

## Результаты проверки на validation_dataset

- ROC AUC: `0.7371`
- PR AUC: `0.4045`
- F1: `0.3871`
- Precision: `0.4211`
- Recall: `0.3582`
- Accuracy: `0.7467`
- Brier score: `0.1556`
- Порог классификации, выбранный на train dataset: `0.402299`

## Матрица ошибок

Метки классов: `[0, 1]`

| Actual / Predicted | 0 | 1 |
| --- | ---: | ---: |
| 0 | 200 | 33 |
| 1 | 43 | 24 |