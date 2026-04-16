"""
QAMini v2 — QA Builder
Converts experiment results into Q&A pairs for semantic search chat.
"""
from __future__ import annotations

import numpy as np
from typing import Any, Optional


def build_qa_pairs(results: dict[str, Any], df_info: dict) -> list[dict[str, str]]:
    """Generate natural-language Q&A pairs from experiment results."""
    pairs = []

    # Dataset-level questions
    pairs.append({
        'question': 'How many rows and columns does the dataset have?',
        'answer': f"The dataset has {df_info['rows']} rows and {df_info['columns']} columns."
    })
    pairs.append({
        'question': 'What columns are in the dataset?',
        'answer': f"The columns are: {', '.join(df_info['column_names'])}."
    })
    pairs.append({
        'question': 'What are the numeric columns?',
        'answer': f"Numeric columns: {', '.join(df_info.get('numeric_columns', []))}."
    })
    pairs.append({
        'question': 'What are the categorical columns?',
        'answer': f"Categorical columns: {', '.join(df_info.get('categorical_columns', []))}."
                  if df_info.get('categorical_columns') else "There are no categorical columns."
    })
    pairs.append({
        'question': 'Are there any missing values?',
        'answer': f"Total missing values: {df_info.get('missing_values', 0)}."
    })

    # Exp 2: Data Visualization
    if 'exp2' in results and results['exp2'].get('status') == 'done':
        r = results['exp2']
        for f in r.get('findings', []):
            pairs.append({'question': f'Tell me about the dataset overview', 'answer': f})
        summary = r.get('summary', {})
        if summary:
            pairs.append({
                'question': 'What is the dataset summary?',
                'answer': f"Rows: {summary.get('rows')}, Columns: {summary.get('columns')}, "
                          f"Numeric: {summary.get('numeric_columns')}, "
                          f"Categorical: {summary.get('categorical_columns')}, "
                          f"Missing: {summary.get('missing_values')}, "
                          f"Duplicates: {summary.get('duplicate_rows')}."
            })

    # Exp 3: Sampling
    if 'exp3' in results and results['exp3'].get('status') == 'done':
        r = results['exp3']
        for f in r.get('findings', []):
            pairs.append({'question': 'What sampling techniques were used?', 'answer': f})
        for name, info in r.get('samples', {}).items():
            pairs.append({
                'question': f'How does {name} sampling work on this dataset?',
                'answer': info.get('description', '')
            })

    # Exp 4: Correlation & SLR
    if 'exp4' in results and results['exp4'].get('status') == 'done':
        r = results['exp4']
        for f in r.get('findings', []):
            pairs.append({'question': 'What are the correlations in the dataset?', 'answer': f})
        slr = r.get('slr', {})
        if slr:
            pairs.append({
                'question': 'What is the simple linear regression result?',
                'answer': f"SLR: {slr.get('equation', '')}. R² = {slr.get('r_squared', '')}."
            })
            pairs.append({
                'question': 'Which variables are most correlated?',
                'answer': f"{slr.get('x_column')} and {slr.get('y_column')} with correlation {slr.get('correlation')}."
            })

    # Exp 5: Partial & Multiple Correlation
    if 'exp5' in results and results['exp5'].get('status') == 'done':
        r = results['exp5']
        for f in r.get('findings', []):
            pairs.append({'question': 'What about partial and multiple correlation?', 'answer': f})
        for col, info in r.get('multiple_r', {}).items():
            pairs.append({
                'question': f'What is the multiple correlation for {col}?',
                'answer': f"Multiple R for {col} = {info['R']}, R² = {info['R_squared']}."
            })

    # Exp 6: MLR
    if 'exp6' in results and results['exp6'].get('status') == 'done':
        r = results['exp6']
        for f in r.get('findings', []):
            pairs.append({'question': 'What are the multiple regression results?', 'answer': f})
        pairs.append({
            'question': 'What is the target variable for regression?',
            'answer': f"Target: {r.get('target', 'N/A')}. Features: {', '.join(r.get('features', []))}."
        })
        pairs.append({
            'question': 'What is the R-squared of the regression model?',
            'answer': f"R² (train) = {r.get('r_squared_train')}, R² (test) = {r.get('r_squared_test')}, "
                      f"Adjusted R² = {r.get('adjusted_r_squared')}, RMSE = {r.get('rmse')}."
        })

    # Exp 7: MLE
    if 'exp7' in results and results['exp7'].get('status') == 'done':
        r = results['exp7']
        for f in r.get('findings', []):
            pairs.append({'question': 'What are the MLE distribution fitting results?', 'answer': f})
        for col, dists in r.get('distributions', {}).items():
            if 'normal' in dists:
                pairs.append({
                    'question': f'Does {col} follow a normal distribution?',
                    'answer': f"Normal fit for {col}: μ = {dists['normal']['mu']}, σ = {dists['normal']['sigma']}. "
                              f"KS test p = {dists['normal']['ks_p_value']}. "
                              f"{'Good fit' if dists['normal']['good_fit'] else 'Poor fit'} at α = 0.05."
                })

    # Exp 8: T-Tests
    if 'exp8' in results and results['exp8'].get('status') == 'done':
        r = results['exp8']
        for f in r.get('findings', []):
            pairs.append({'question': 'What do the t-test results show?', 'answer': f})
        one_sample = r.get('results', {}).get('one_sample', {})
        for col, info in one_sample.items():
            pairs.append({
                'question': f'Is the mean of {col} significantly different from zero?',
                'answer': f"One-sample t-test for {col}: t = {info['t_statistic']}, "
                          f"p = {info['p_value']}. {info['conclusion']}."
            })
        two = r.get('results', {}).get('two_sample', {})
        if two:
            pairs.append({
                'question': 'What does the two-sample t-test show?',
                'answer': f"Two-sample t-test ({two.get('column_1')} vs {two.get('column_2')}): "
                          f"t = {two.get('t_statistic')}, p = {two.get('p_value')}. {two.get('conclusion')}."
            })

    # Exp 9: Z-Tests
    if 'exp9' in results and results['exp9'].get('status') == 'done':
        r = results['exp9']
        for f in r.get('findings', []):
            pairs.append({'question': 'What do the z-test results show?', 'answer': f})
        one_sample = r.get('results', {}).get('one_sample', {})
        for col, info in one_sample.items():
            pairs.append({
                'question': f'What is the z-test result for {col}?',
                'answer': f"One-sample z-test for {col}: z = {info['z_statistic']}, "
                          f"p = {info['p_value']}. {info['conclusion']}."
            })

    # Filter out empty answers
    pairs = [p for p in pairs if p['answer'].strip()]
    return pairs
