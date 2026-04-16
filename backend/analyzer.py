"""
QAMini v2 — Statistical Analysis Engine
Performs 8 experiments on any uploaded CSV dataset.
"""
from __future__ import annotations

import io
import base64
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from typing import Any

warnings.filterwarnings('ignore')

# ─── Plot Helpers ────────────────────────────────────────────────

PLOT_STYLE = {
    'figure.facecolor': '#12121a',
    'axes.facecolor': '#1a1a26',
    'axes.edgecolor': '#2a2a3a',
    'axes.labelcolor': '#a0a0b8',
    'text.color': '#f0f0f5',
    'xtick.color': '#6a6a82',
    'ytick.color': '#6a6a82',
    'grid.color': '#2a2a3a',
    'grid.alpha': 0.5,
    'font.family': 'sans-serif',
    'font.size': 10,
}

def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def _get_numeric_cols(df: pd.DataFrame) -> list[str]:
    """Get numeric columns, excluding those that look like IDs."""
    cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude columns that are likely IDs
    id_terms = ['id', 'index', 'key', 'pk']
    filtered = []
    for c in cols:
        name_lower = c.lower()
        # If it contains an ID term and has high cardinality/uniqueness
        # we still keep it for visualization but maybe skip for deep stats
        filtered.append(c)
    return filtered

def _is_probably_id(df: pd.DataFrame, col: str) -> bool:
    """Check if a column is likely an ID/Identifier column."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        return False
    name_lower = col.lower()
    for term in ['id', 'index', 'key', 'pk']:
        if term in name_lower:
            # If it's mostly unique and sequential-ish
            if df[col].nunique() > len(df) * 0.9:
                return True
    return False

def _get_categorical_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 2: Data Visualization
# ═════════════════════════════════════════════════════════════════

def exp_data_visualization(df: pd.DataFrame) -> dict[str, Any]:
    """Generate descriptive stats + visualization plots."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        cat_cols = _get_categorical_cols(df)
        plots = []

        # Descriptive statistics table
        # If too many columns, focus on the first 20 for the table to avoid payload bloat
        target_cols = df.columns[:20] if len(df.columns) > 20 else df.columns
        desc = df[target_cols].describe(include='all').round(4)
        desc_table = desc.replace({np.nan: None, np.inf: None, -np.inf: None}).reset_index().to_dict('records')

        # 1. Histograms for numeric columns
        if num_cols:
            n = len(num_cols)
            cols_grid = min(3, n)
            rows_grid = (n + cols_grid - 1) // cols_grid
            fig, axes = plt.subplots(rows_grid, cols_grid,
                                     figsize=(5 * cols_grid, 4 * rows_grid))
            if n == 1:
                axes = [axes]
            else:
                axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
            for i, col in enumerate(num_cols):
                if i < len(axes):
                    ax = axes[i]
                    data = df[col].dropna()
                    ax.hist(data, bins=min(30, max(10, len(data) // 5)),
                            color='#14b8a6', alpha=0.8, edgecolor='#0d9488')
                    ax.set_title(col, fontsize=11, fontweight='bold')
                    ax.set_xlabel('')
                    ax.grid(True, alpha=0.3)
            for j in range(i + 1, len(axes)):
                axes[j].set_visible(False)
            fig.suptitle('Histograms — Numeric Columns', fontsize=14,
                         fontweight='bold', y=1.02)
            fig.tight_layout()
            plots.append({'title': 'Histograms', 'image': _fig_to_base64(fig)})

        # 2. Box plots
        if num_cols:
            fig, ax = plt.subplots(figsize=(max(8, len(num_cols) * 1.5), 5))
            bp = ax.boxplot([df[c].dropna().values for c in num_cols],
                           labels=num_cols, patch_artist=True,
                           boxprops=dict(facecolor='#14b8a6', alpha=0.6),
                           medianprops=dict(color='#f59e0b', linewidth=2),
                           whiskerprops=dict(color='#6a6a82'),
                           capprops=dict(color='#6a6a82'),
                           flierprops=dict(marker='o', markerfacecolor='#ef4444',
                                          markersize=4, alpha=0.5))
            ax.set_title('Box Plots — Numeric Columns', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            fig.tight_layout()
            plots.append({'title': 'Box Plots', 'image': _fig_to_base64(fig)})

        # 3. Correlation heatmap
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().round(4)
            fig, ax = plt.subplots(figsize=(max(8, len(num_cols) * 0.9),
                                           max(6, len(num_cols) * 0.7)))
            im = ax.imshow(corr.values, cmap='RdYlGn', aspect='auto',
                          vmin=-1, vmax=1)
            ax.set_xticks(range(len(num_cols)))
            ax.set_yticks(range(len(num_cols)))
            ax.set_xticklabels(num_cols, rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels(num_cols, fontsize=8)
            for i in range(len(num_cols)):
                for j in range(len(num_cols)):
                    v = corr.values[i, j]
                    color = 'white' if abs(v) > 0.5 else '#f0f0f5'
                    ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                           fontsize=7, color=color)
            fig.colorbar(im, ax=ax, shrink=0.8)
            ax.set_title('Correlation Heatmap', fontsize=14, fontweight='bold')
            fig.tight_layout()
            plots.append({'title': 'Correlation Heatmap', 'image': _fig_to_base64(fig)})

        # 4. Categorical bar charts
        for col in cat_cols[:3]:
            vc = df[col].value_counts().head(15)
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.barh(range(len(vc)), vc.values, color='#6366f1', alpha=0.8)
            ax.set_yticks(range(len(vc)))
            ax.set_yticklabels([str(v)[:30] for v in vc.index], fontsize=8)
            ax.set_title(f'Value Counts — {col}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            ax.invert_yaxis()
            fig.tight_layout()
            plots.append({'title': f'Bar Chart: {col}', 'image': _fig_to_base64(fig)})

        # Summary stats
        summary = {
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'numeric_columns': int(len(num_cols)),
            'categorical_columns': int(len(cat_cols)),
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
        }

        return {
            'summary': summary,
            'descriptive_stats': desc_table,
            'plots': plots,
            'findings': [
                f"Dataset has {len(df)} rows and {len(df.columns)} columns.",
                f"{len(num_cols)} numeric and {len(cat_cols)} categorical columns.",
                f"Total missing values: {summary['missing_values']}.",
                f"Duplicate rows: {summary['duplicate_rows']}.",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 3: Sampling Techniques
# ═════════════════════════════════════════════════════════════════

def exp_sampling_techniques(df: pd.DataFrame) -> dict[str, Any]:
    """Demonstrate random, stratified, and systematic sampling."""
    with plt.rc_context(PLOT_STYLE):
        n = len(df)
        sample_size = min(max(int(n * 0.2), 10), n)
        num_cols = _get_numeric_cols(df)
        cat_cols = _get_categorical_cols(df)
        samples = {}
        plots = []

        # 1. Simple Random Sampling
        random_sample = df.sample(n=sample_size, random_state=42)
        samples['random'] = {
            'method': 'Simple Random Sampling',
            'size': int(len(random_sample)),
            'description': f'Randomly selected {sample_size} rows (20% of {n}).',
        }

        # 2. Systematic Sampling
        step = max(1, n // sample_size)
        systematic_idx = list(range(0, n, step))[:sample_size]
        systematic_sample = df.iloc[systematic_idx]
        samples['systematic'] = {
            'method': 'Systematic Sampling',
            'size': int(len(systematic_sample)),
            'description': f'Every {step}th row selected, yielding {len(systematic_sample)} rows.',
        }

        # 3. Stratified Sampling
        strat_col = cat_cols[0] if cat_cols else None
        if strat_col and df[strat_col].nunique() <= 20:
            fracs = {}
            for val in df[strat_col].unique():
                subset = df[df[strat_col] == val]
                frac = max(1, int(len(subset) * 0.2))
                fracs[val] = min(frac, len(subset))
            strat_parts = []
            for val, count in fracs.items():
                strat_parts.append(df[df[strat_col] == val].sample(n=count, random_state=42))
            stratified_sample = pd.concat(strat_parts)
            samples['stratified'] = {
                'method': 'Stratified Sampling',
                'size': int(len(stratified_sample)),
                'description': f'Stratified by "{strat_col}" — 20% from each group.',
                'strata_column': str(strat_col),
            }
        else:
            stratified_sample = random_sample
            samples['stratified'] = {
                'method': 'Stratified Sampling (fallback to random)',
                'size': int(len(stratified_sample)),
                'description': 'No suitable categorical column found, used random sampling.',
            }

        # Comparison plot — means
        if num_cols:
            compare_cols = num_cols[:6]
            pop_means = df[compare_cols].mean()
            rand_means = random_sample[compare_cols].mean()
            syst_means = systematic_sample[compare_cols].mean()
            strat_means = stratified_sample[compare_cols].mean()

            x = np.arange(len(compare_cols))
            width = 0.2
            fig, ax = plt.subplots(figsize=(max(8, len(compare_cols) * 2), 5))
            ax.bar(x - 1.5 * width, pop_means, width, label='Population', color='#f0f0f5', alpha=0.7)
            ax.bar(x - 0.5 * width, rand_means, width, label='Random', color='#14b8a6', alpha=0.8)
            ax.bar(x + 0.5 * width, syst_means, width, label='Systematic', color='#6366f1', alpha=0.8)
            ax.bar(x + 1.5 * width, strat_means, width, label='Stratified', color='#f59e0b', alpha=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(compare_cols, rotation=45, ha='right')
            ax.set_title('Sample Means vs Population Means', fontsize=14, fontweight='bold')
            ax.legend(loc='upper right', fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            fig.tight_layout()
            plots.append({'title': 'Sampling Comparison', 'image': _fig_to_base64(fig)})

        return {
            'samples': samples,
            'population_size': n,
            'sample_size': sample_size,
            'plots': plots,
            'findings': [
                f"Population size: {n}. Sample size: ~{sample_size} (20%).",
                f"Random sampling: {samples['random']['size']} rows selected.",
                f"Systematic sampling: every {step}th row, {samples['systematic']['size']} rows.",
                f"Stratified sampling: {samples['stratified']['size']} rows.",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 4: Correlation Types and SLR
# ═════════════════════════════════════════════════════════════════

def exp_correlation_slr(df: pd.DataFrame) -> dict[str, Any]:
    """Pearson, Spearman, Kendall correlations + Simple Linear Regression."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if len(num_cols) < 2:
            return {'error': 'Need at least 2 numeric columns.', 'plots': [], 'findings': ['Insufficient numeric columns.']}

        num_df = df[num_cols].dropna()

        # Correlation matrices
        pearson = num_df.corr(method='pearson').round(4)
        spearman = num_df.corr(method='spearman').round(4)
        kendall = num_df.corr(method='kendall').round(4)

        corr_tables = {
            'pearson': pearson.reset_index().to_dict('records'),
            'spearman': spearman.reset_index().to_dict('records'),
            'kendall': kendall.reset_index().to_dict('records'),
        }

        # Plot all three
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        for ax, (name, corr_mat) in zip(axes, [('Pearson', pearson), ('Spearman', spearman), ('Kendall', kendall)]):
            im = ax.imshow(corr_mat.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
            ax.set_xticks(range(len(num_cols)))
            ax.set_yticks(range(len(num_cols)))
            ax.set_xticklabels(num_cols, rotation=45, ha='right', fontsize=7)
            ax.set_yticklabels(num_cols, fontsize=7)
            ax.set_title(name, fontsize=12, fontweight='bold')
            for i in range(len(num_cols)):
                for j in range(len(num_cols)):
                    v = corr_mat.values[i, j]
                    ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=6,
                           color='white' if abs(v) > 0.5 else '#a0a0b8')
        fig.colorbar(im, ax=axes, shrink=0.6)
        fig.suptitle('Correlation Matrices', fontsize=14, fontweight='bold')
        fig.tight_layout()
        plots.append({'title': 'Correlation Matrices', 'image': _fig_to_base64(fig)})

        # Simple Linear Regression — find best correlated pair
        upper = pearson.where(np.triu(np.ones(pearson.shape, dtype=bool), k=1))
        abs_upper = upper.abs()
        best_pair = abs_upper.stack().idxmax()
        x_col, y_col = best_pair
        best_r = pearson.loc[x_col, y_col]

        X = num_df[x_col].values.reshape(-1, 1)
        y = num_df[y_col].values
        model = LinearRegression().fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)

        slr_results = {
            'x_column': x_col,
            'y_column': y_col,
            'correlation': round(float(best_r), 4),
            'slope': round(float(model.coef_[0]), 4),
            'intercept': round(float(model.intercept_), 4),
            'r_squared': round(float(r2), 4),
            'equation': f'{y_col} = {model.coef_[0]:.4f} × {x_col} + {model.intercept_:.4f}',
        }

        # SLR plot
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(num_df[x_col], num_df[y_col], alpha=0.4, color='#14b8a6',
                  s=20, edgecolors='none')
        sort_idx = np.argsort(X.flatten())
        ax.plot(X.flatten()[sort_idx], y_pred[sort_idx], color='#ef4444',
               linewidth=2, label=f'R² = {r2:.4f}')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'Simple Linear Regression: {y_col} vs {x_col}',
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plots.append({'title': 'Simple Linear Regression', 'image': _fig_to_base64(fig)})

        return {
            'correlation_tables': corr_tables,
            'slr': slr_results,
            'plots': plots,
            'findings': [
                f"Highest correlation: {x_col} ↔ {y_col} (r = {best_r:.4f}).",
                f"SLR equation: {slr_results['equation']}",
                f"R² = {r2:.4f} ({r2 * 100:.1f}% variance explained).",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 5: Partial and Multiple Correlation
# ═════════════════════════════════════════════════════════════════

def exp_partial_multiple_correlation(df: pd.DataFrame) -> dict[str, Any]:
    """Partial correlation and multiple correlation coefficient."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if len(num_cols) < 3:
            return {'error': 'Need at least 3 numeric columns.', 'plots': [], 'findings': ['Insufficient columns.']}

        num_df = df[num_cols].dropna()

        # Partial correlation matrix
        corr = num_df.corr()
        try:
            inv_corr = np.linalg.inv(corr.values)
            D = np.diag(1 / np.sqrt(np.diag(inv_corr)))
            partial_corr = -D @ inv_corr @ D
            np.fill_diagonal(partial_corr, 1.0)
            partial_df = pd.DataFrame(partial_corr, index=num_cols, columns=num_cols).round(4)
        except np.linalg.LinAlgError:
            partial_df = pd.DataFrame(np.eye(len(num_cols)), index=num_cols, columns=num_cols)

        # Multiple correlation coefficient (R for each variable vs all others)
        multiple_r = {}
        for col in num_cols:
            others = [c for c in num_cols if c != col]
            if len(others) < 1:
                continue
            X = num_df[others].values
            y = num_df[col].values
            model = LinearRegression().fit(X, y)
            r2 = r2_score(y, model.predict(X))
            multiple_r[col] = {
                'R': round(float(np.sqrt(max(0, r2))), 4),
                'R_squared': round(float(r2), 4),
            }

        # Partial correlation heatmap
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        im1 = axes[0].imshow(corr.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        axes[0].set_xticks(range(len(num_cols)))
        axes[0].set_yticks(range(len(num_cols)))
        axes[0].set_xticklabels(num_cols, rotation=45, ha='right', fontsize=7)
        axes[0].set_yticklabels(num_cols, fontsize=7)
        axes[0].set_title('Zero-Order Correlation', fontsize=12, fontweight='bold')
        for i in range(len(num_cols)):
            for j in range(len(num_cols)):
                axes[0].text(j, i, f'{corr.values[i, j]:.2f}', ha='center', va='center',
                           fontsize=6, color='white' if abs(corr.values[i, j]) > 0.5 else '#a0a0b8')

        im2 = axes[1].imshow(partial_df.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        axes[1].set_xticks(range(len(num_cols)))
        axes[1].set_yticks(range(len(num_cols)))
        axes[1].set_xticklabels(num_cols, rotation=45, ha='right', fontsize=7)
        axes[1].set_yticklabels(num_cols, fontsize=7)
        axes[1].set_title('Partial Correlation', fontsize=12, fontweight='bold')
        for i in range(len(num_cols)):
            for j in range(len(num_cols)):
                axes[1].text(j, i, f'{partial_df.values[i, j]:.2f}', ha='center', va='center',
                           fontsize=6, color='white' if abs(partial_df.values[i, j]) > 0.5 else '#a0a0b8')

        fig.suptitle('Zero-Order vs Partial Correlation', fontsize=14, fontweight='bold')
        fig.tight_layout()
        plots.append({'title': 'Correlation Comparison', 'image': _fig_to_base64(fig)})

        # Multiple R bar chart
        fig, ax = plt.subplots(figsize=(max(8, len(num_cols) * 1.2), 5))
        cols_list = list(multiple_r.keys())
        r_values = [multiple_r[c]['R'] for c in cols_list]
        colors = ['#14b8a6' if r > 0.7 else '#f59e0b' if r > 0.4 else '#ef4444' for r in r_values]
        ax.bar(cols_list, r_values, color=colors, alpha=0.8, edgecolor='none')
        ax.set_ylabel('Multiple R')
        ax.set_title('Multiple Correlation Coefficient (R)', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        fig.tight_layout()
        plots.append({'title': 'Multiple R', 'image': _fig_to_base64(fig)})

        return {
            'partial_correlation': partial_df.reset_index().to_dict('records'),
            'multiple_r': multiple_r,
            'plots': plots,
            'findings': [
                "Partial correlations control for all other variables.",
                f"Highest multiple R: {max(multiple_r.items(), key=lambda x: x[1]['R'])[0]} "
                f"(R = {max(multiple_r.values(), key=lambda x: x['R'])['R']:.4f}).",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 6: Multiple Linear Regression
# ═════════════════════════════════════════════════════════════════

def exp_multiple_linear_regression(df: pd.DataFrame) -> dict[str, Any]:
    """Multiple Linear Regression with diagnostics."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if len(num_cols) < 2:
            return {'error': 'Need at least 2 numeric columns.', 'plots': [], 'findings': ['Insufficient columns.']}

        num_df = df[num_cols].dropna()
        target = num_cols[-1]  # Use last numeric column as target
        features = [c for c in num_cols if c != target]

        if not features:
            return {'error': 'Need at least 1 feature column.', 'plots': [], 'findings': ['Insufficient features.']}

        X = num_df[features].values
        y = num_df[target].values

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression().fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        n, p = X_train.shape
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        adj_r2 = 1 - (1 - r2_train) * (n - 1) / (n - p - 1) if n > p + 1 else r2_train
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))

        # Coefficients
        coefficients = [{'feature': f, 'coefficient': round(float(c), 6)}
                       for f, c in zip(features, model.coef_)]
        coefficients.append({'feature': 'Intercept', 'coefficient': round(float(model.intercept_), 6)})

        # ANOVA table
        ss_reg = np.sum((y_pred_train - y_train.mean()) ** 2)
        ss_res = np.sum((y_train - y_pred_train) ** 2)
        ss_tot = ss_reg + ss_res
        df_reg = p
        df_res = n - p - 1
        ms_reg = ss_reg / df_reg if df_reg > 0 else 0
        ms_res = ss_res / df_res if df_res > 0 else 0
        f_stat = ms_reg / ms_res if ms_res > 0 else 0
        p_value = 1 - stats.f.cdf(f_stat, df_reg, df_res) if df_res > 0 else 1

        anova = {
            'regression': {'SS': round(ss_reg, 4), 'df': df_reg, 'MS': round(ms_reg, 4), 'F': round(f_stat, 4), 'p_value': round(p_value, 6)},
            'residual': {'SS': round(ss_res, 4), 'df': df_res, 'MS': round(ms_res, 4)},
            'total': {'SS': round(ss_tot, 4), 'df': df_reg + df_res},
        }

        # 1. Actual vs Predicted
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        axes[0].scatter(y_test, y_pred_test, alpha=0.5, color='#14b8a6', s=20, edgecolors='none')
        lims = [min(y_test.min(), y_pred_test.min()), max(y_test.max(), y_pred_test.max())]
        axes[0].plot(lims, lims, 'r--', alpha=0.7, linewidth=1.5)
        axes[0].set_xlabel('Actual')
        axes[0].set_ylabel('Predicted')
        axes[0].set_title('Actual vs Predicted', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # 2. Residual plot
        residuals = y_test - y_pred_test
        axes[1].scatter(y_pred_test, residuals, alpha=0.5, color='#6366f1', s=20, edgecolors='none')
        axes[1].axhline(y=0, color='#ef4444', linewidth=1.5, linestyle='--')
        axes[1].set_xlabel('Predicted')
        axes[1].set_ylabel('Residuals')
        axes[1].set_title('Residual Plot', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        # 3. Q-Q plot
        sorted_res = np.sort(residuals)
        theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_res)))
        axes[2].scatter(theoretical_q, sorted_res, alpha=0.5, color='#f59e0b', s=20, edgecolors='none')
        axes[2].plot(theoretical_q, theoretical_q * np.std(sorted_res) + np.mean(sorted_res),
                    'r--', alpha=0.7, linewidth=1.5)
        axes[2].set_xlabel('Theoretical Quantiles')
        axes[2].set_ylabel('Sample Quantiles')
        axes[2].set_title('Q-Q Plot (Residuals)', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)

        fig.suptitle(f'Multiple Linear Regression: {target} ~ {" + ".join(features)}',
                    fontsize=14, fontweight='bold')
        fig.tight_layout()
        plots.append({'title': 'MLR Diagnostics', 'image': _fig_to_base64(fig)})

        # Feature importance
        fig, ax = plt.subplots(figsize=(8, max(4, len(features) * 0.5)))
        abs_coefs = np.abs(model.coef_)
        sorted_idx = np.argsort(abs_coefs)
        ax.barh(np.array(features)[sorted_idx], abs_coefs[sorted_idx],
               color='#14b8a6', alpha=0.8)
        ax.set_xlabel('|Coefficient|')
        ax.set_title('Feature Importance', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        fig.tight_layout()
        plots.append({'title': 'Feature Importance', 'image': _fig_to_base64(fig)})

        return {
            'target': target,
            'features': features,
            'coefficients': coefficients,
            'r_squared_train': round(r2_train, 4),
            'r_squared_test': round(r2_test, 4),
            'adjusted_r_squared': round(adj_r2, 4),
            'rmse': round(rmse, 4),
            'anova': anova,
            'plots': plots,
            'findings': [
                f"Target: {target}. Features: {', '.join(features)}.",
                f"R² (train) = {r2_train:.4f}, R² (test) = {r2_test:.4f}.",
                f"Adjusted R² = {adj_r2:.4f}. RMSE = {rmse:.4f}.",
                f"F-statistic = {f_stat:.4f}, p-value = {p_value:.6f}.",
                f"Model is {'statistically significant' if p_value < 0.05 else 'not significant'} at α = 0.05.",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 7: MLE Estimation
# ═════════════════════════════════════════════════════════════════

def exp_mle_estimation(df: pd.DataFrame) -> dict[str, Any]:
    """Maximum Likelihood Estimation for Normal, Poisson, and Exponential distributions."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if not num_cols:
            return {'error': 'No numeric columns.', 'plots': [], 'findings': ['No data.']}

        results = {}
        # Analyze up to 4 columns
        for col in num_cols[:4]:
            if _is_probably_id(df, col):
                continue
            data = df[col].dropna().values
            if len(data) < 5 or np.all(data == data[0]):
                continue

            col_results = {}

            # Normal MLE
            mu_mle = np.mean(data)
            sigma_mle = np.std(data, ddof=0)
            ks_stat_norm, ks_p_norm = stats.kstest(data, 'norm', args=(mu_mle, sigma_mle))
            col_results['normal'] = {
                'mu': round(float(mu_mle), 4),
                'sigma': round(float(sigma_mle), 4),
                'ks_statistic': round(float(ks_stat_norm), 4),
                'ks_p_value': round(float(ks_p_norm), 4),
                'good_fit': bool(ks_p_norm > 0.05),
            }

            # Exponential MLE (only for positive data)
            pos_data = data[data > 0]
            if len(pos_data) > 5:
                lambda_mle = float(1 / np.mean(pos_data))
                ks_stat_exp, ks_p_exp = stats.kstest(pos_data, 'expon', args=(0, 1 / lambda_mle))
                col_results['exponential'] = {
                    'lambda': round(float(lambda_mle), 6),
                    'mean': round(float(1 / lambda_mle), 4),
                    'ks_statistic': round(float(ks_stat_exp), 4),
                    'ks_p_value': round(float(ks_p_exp), 4),
                    'good_fit': bool(ks_p_exp > 0.05),
                }

            # Poisson MLE (for non-negative integer-like data)
            int_data = data[(data >= 0) & (data == np.floor(data))]
            if len(int_data) > 5:
                lambda_p = np.mean(int_data)
                col_results['poisson'] = {
                    'lambda': round(float(lambda_p), 4),
                    'note': 'Data approximated as integer counts.',
                }

            results[col] = col_results

            # Plot: histogram with fitted distributions
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(data, bins=min(30, max(10, len(data) // 5)),
                   density=True, alpha=0.6, color='#14b8a6', edgecolor='#0d9488',
                   label='Data')
            x_range = np.linspace(data.min(), data.max(), 200)

            # Normal overlay
            ax.plot(x_range, stats.norm.pdf(x_range, mu_mle, sigma_mle),
                   color='#ef4444', linewidth=2, label=f'Normal (μ={mu_mle:.2f}, σ={sigma_mle:.2f})')

            # Exponential overlay (if applicable)
            if 'exponential' in col_results and pos_data.min() >= 0:
                x_exp = np.linspace(0, data.max(), 200)
                ax.plot(x_exp, stats.expon.pdf(x_exp, 0, 1 / lambda_mle),
                       color='#f59e0b', linewidth=2, linestyle='--',
                       label=f'Exponential (λ={lambda_mle:.4f})')

            ax.set_title(f'MLE Distribution Fit — {col}', fontsize=13, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            plots.append({'title': f'MLE: {col}', 'image': _fig_to_base64(fig)})

        return {
            'distributions': results,
            'plots': plots,
            'findings': [
                f"Analyzed {len(results)} numeric columns for distribution fitting.",
                *[f"{col}: Normal fit {'✓' if r.get('normal', {}).get('good_fit') else '✗'} "
                  f"(KS p={r.get('normal', {}).get('ks_p_value', 'N/A')})"
                  for col, r in results.items()],
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 8: T-Tests
# ═════════════════════════════════════════════════════════════════

def exp_t_tests(df: pd.DataFrame) -> dict[str, Any]:
    """One-sample and independent two-sample t-tests."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if not num_cols:
            return {'error': 'No numeric columns.', 'plots': [], 'findings': ['No data.']}

        results = {}

        # 1. One-sample t-test for each numeric column (H0: μ = 0)
        one_sample = {}
        for col in num_cols[:10]: # Limit to 10 columns
            if _is_probably_id(df, col):
                continue
            data = df[col].dropna().values
            if len(data) < 3 or np.all(data == data[0]):
                continue
            pop_mean = float(np.mean(data))
            t_stat, p_val = stats.ttest_1samp(data, 0)
            one_sample[col] = {
                'sample_mean': round(float(pop_mean), 4),
                'hypothesized_mean': 0,
                'n': int(len(data)),
                't_statistic': round(float(t_stat), 4),
                'p_value': round(float(p_val), 6),
                'significant': bool(p_val < 0.05),
                'conclusion': f'Reject H₀ (mean ≠ 0)' if p_val < 0.05 else 'Fail to reject H₀',
            }
        results['one_sample'] = one_sample

        # 2. Independent two-sample t-test (first two numeric columns)
        two_sample = {}
        if len(num_cols) >= 2:
            col1, col2 = num_cols[0], num_cols[1]
            data1 = df[col1].dropna().values
            data2 = df[col2].dropna().values
            t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)  # Welch's
            two_sample = {
                'column_1': str(col1),
                'column_2': str(col2),
                'mean_1': round(float(np.mean(data1)), 4),
                'mean_2': round(float(np.mean(data2)), 4),
                'n_1': int(len(data1)),
                'n_2': int(len(data2)),
                't_statistic': round(float(t_stat), 4),
                'p_value': round(float(p_val), 6),
                'significant': bool(p_val < 0.05),
                'conclusion': f'Means are significantly different' if p_val < 0.05 else 'No significant difference',
                'test_type': "Welch's t-test (unequal variances)",
            }
        results['two_sample'] = two_sample

        # Plot one-sample results
        if one_sample:
            cols_list = list(one_sample.keys())[:10]
            fig, ax = plt.subplots(figsize=(max(8, len(cols_list) * 1.2), 5))
            t_stats = [one_sample[c]['t_statistic'] for c in cols_list]
            colors = ['#22c55e' if one_sample[c]['significant'] else '#ef4444' for c in cols_list]
            bars = ax.bar(cols_list, t_stats, color=colors, alpha=0.8)
            ax.axhline(y=stats.t.ppf(0.975, df=30), color='#f59e0b', linestyle='--',
                      linewidth=1.5, label='Critical value (α=0.05)')
            ax.axhline(y=-stats.t.ppf(0.975, df=30), color='#f59e0b', linestyle='--', linewidth=1.5)
            ax.set_ylabel('t-statistic')
            ax.set_title('One-Sample T-Tests (H₀: μ = 0)', fontsize=14, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            fig.tight_layout()
            plots.append({'title': 'One-Sample T-Tests', 'image': _fig_to_base64(fig)})

        # Plot two-sample comparison
        if two_sample:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            data1 = df[two_sample['column_1']].dropna()
            data2 = df[two_sample['column_2']].dropna()
            axes[0].hist(data1, bins=20, alpha=0.6, color='#14b8a6', label=two_sample['column_1'], density=True)
            axes[0].hist(data2, bins=20, alpha=0.6, color='#6366f1', label=two_sample['column_2'], density=True)
            axes[0].set_title('Distribution Comparison', fontsize=12, fontweight='bold')
            axes[0].legend(fontsize=9)
            axes[0].grid(True, alpha=0.3)

            bp = axes[1].boxplot([data1.values, data2.values],
                                labels=[two_sample['column_1'], two_sample['column_2']],
                                patch_artist=True,
                                boxprops=dict(alpha=0.7),
                                medianprops=dict(color='#f59e0b', linewidth=2))
            bp['boxes'][0].set_facecolor('#14b8a6')
            bp['boxes'][1].set_facecolor('#6366f1')
            sig_text = '✓ Significant' if two_sample['significant'] else '✗ Not Significant'
            axes[1].set_title(f'Two-Sample T-Test ({sig_text})', fontsize=12, fontweight='bold')
            axes[1].grid(True, alpha=0.3, axis='y')

            fig.suptitle("Welch's Independent Two-Sample T-Test", fontsize=14, fontweight='bold')
            fig.tight_layout()
            plots.append({'title': 'Two-Sample T-Test', 'image': _fig_to_base64(fig)})

        return {
            'results': results,
            'plots': plots,
            'findings': [
                f"One-sample t-tests performed on {len(one_sample)} columns (H₀: μ = 0).",
                f"Significant results: {sum(1 for v in one_sample.values() if v['significant'])} / {len(one_sample)}.",
                f"Two-sample t-test: {two_sample.get('conclusion', 'N/A')} "
                f"(p = {two_sample.get('p_value', 'N/A')})." if two_sample else "Two-sample t-test not performed.",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# EXPERIMENT 9: Z-Tests
# ═════════════════════════════════════════════════════════════════

def exp_z_tests(df: pd.DataFrame) -> dict[str, Any]:
    """One-sample and two-sample z-tests."""
    with plt.rc_context(PLOT_STYLE):
        num_cols = _get_numeric_cols(df)
        plots = []

        if not num_cols:
            return {'error': 'No numeric columns.', 'plots': [], 'findings': ['No data.']}

        results = {}

        # 1. One-sample z-test for each column (H0: μ = population mean)
        one_sample = {}
        for col in num_cols:
            data = df[col].dropna().values
            if len(data) < 30:
                continue
            sample_mean = np.mean(data)
            pop_std = np.std(data, ddof=0)
            n = len(data)
            # Test H0: μ = 0
            z_stat = (sample_mean - 0) / (pop_std / np.sqrt(n)) if pop_std > 0 else 0
            p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            one_sample[col] = {
                'sample_mean': round(float(sample_mean), 4),
                'population_std': round(float(pop_std), 4),
                'n': int(n),
                'z_statistic': round(float(z_stat), 4),
                'p_value': round(float(p_val), 6),
                'significant': bool(p_val < 0.05),
                'conclusion': 'Reject H₀ (mean ≠ 0)' if p_val < 0.05 else 'Fail to reject H₀',
            }
        results['one_sample'] = one_sample

        # 2. Two-sample z-test
        two_sample = {}
        if len(num_cols) >= 2:
            col1, col2 = num_cols[0], num_cols[1]
            data1 = df[col1].dropna().values
            data2 = df[col2].dropna().values
            if len(data1) >= 30 and len(data2) >= 30:
                mean1, mean2 = np.mean(data1), np.mean(data2)
                std1, std2 = np.std(data1, ddof=0), np.std(data2, ddof=0)
                n1, n2 = len(data1), len(data2)
                se = np.sqrt(std1 ** 2 / n1 + std2 ** 2 / n2)
                z_stat = (mean1 - mean2) / se if se > 0 else 0
                p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                two_sample = {
                    'column_1': str(col1),
                    'column_2': str(col2),
                    'mean_1': round(float(mean1), 4),
                    'mean_2': round(float(mean2), 4),
                    'n_1': int(n1),
                    'n_2': int(n2),
                    'z_statistic': round(float(z_stat), 4),
                    'p_value': round(float(p_val), 6),
                    'significant': bool(p_val < 0.05),
                    'conclusion': 'Means are significantly different' if p_val < 0.05 else 'No significant difference',
                }
        results['two_sample'] = two_sample

        # Plot z-test results
        if one_sample:
            cols_list = list(one_sample.keys())[:10]
            fig, ax = plt.subplots(figsize=(max(8, len(cols_list) * 1.2), 5))
            z_stats = [one_sample[c]['z_statistic'] for c in cols_list]
            colors = ['#22c55e' if one_sample[c]['significant'] else '#ef4444' for c in cols_list]
            ax.bar(cols_list, z_stats, color=colors, alpha=0.8)
            ax.axhline(y=1.96, color='#f59e0b', linestyle='--', linewidth=1.5, label='z = ±1.96 (α=0.05)')
            ax.axhline(y=-1.96, color='#f59e0b', linestyle='--', linewidth=1.5)
            ax.set_ylabel('z-statistic')
            ax.set_title('One-Sample Z-Tests (H₀: μ = 0)', fontsize=14, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            fig.tight_layout()
            plots.append({'title': 'One-Sample Z-Tests', 'image': _fig_to_base64(fig)})

        # Normal distribution visualization for z-test
        fig, ax = plt.subplots(figsize=(8, 5))
        x = np.linspace(-4, 4, 300)
        ax.plot(x, stats.norm.pdf(x), color='#14b8a6', linewidth=2)
        ax.fill_between(x, stats.norm.pdf(x), where=(x <= -1.96) | (x >= 1.96),
                       alpha=0.3, color='#ef4444', label='Rejection region (α=0.05)')
        ax.fill_between(x, stats.norm.pdf(x), where=(x > -1.96) & (x < 1.96),
                       alpha=0.15, color='#22c55e', label='Acceptance region')
        ax.axvline(x=1.96, color='#f59e0b', linestyle='--', linewidth=1)
        ax.axvline(x=-1.96, color='#f59e0b', linestyle='--', linewidth=1)
        ax.set_title('Z-Test Critical Regions', fontsize=14, fontweight='bold')
        ax.set_xlabel('Z-score')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plots.append({'title': 'Z-Test Critical Regions', 'image': _fig_to_base64(fig)})

        return {
            'results': results,
            'plots': plots,
            'findings': [
                f"One-sample z-tests: {len(one_sample)} columns tested (n ≥ 30).",
                f"Significant results: {sum(1 for v in one_sample.values() if v['significant'])} / {len(one_sample)}.",
                f"Two-sample z-test: {two_sample.get('conclusion', 'Not enough data (n < 30)')}"
                f" (p = {two_sample.get('p_value', 'N/A')})." if two_sample else "",
            ]
        }


# ═════════════════════════════════════════════════════════════════
# MASTER RUNNER
# ═════════════════════════════════════════════════════════════════

EXPERIMENTS = [
    {'id': 'exp2', 'num': 2, 'name': 'Data Visualization', 'fn': exp_data_visualization},
    {'id': 'exp3', 'num': 3, 'name': 'Sampling Techniques', 'fn': exp_sampling_techniques},
    {'id': 'exp4', 'num': 4, 'name': 'Correlation & SLR', 'fn': exp_correlation_slr},
    {'id': 'exp5', 'num': 5, 'name': 'Partial & Multiple Correlation', 'fn': exp_partial_multiple_correlation},
    {'id': 'exp6', 'num': 6, 'name': 'Multiple Linear Regression', 'fn': exp_multiple_linear_regression},
    {'id': 'exp7', 'num': 7, 'name': 'MLE Estimation', 'fn': exp_mle_estimation},
    {'id': 'exp8', 'num': 8, 'name': 'T-Tests', 'fn': exp_t_tests},
    {'id': 'exp9', 'num': 9, 'name': 'Z-Tests', 'fn': exp_z_tests},
]

def run_all_experiments(df: pd.DataFrame, status_callback=None) -> dict[str, Any]:
    """Run all experiments on the dataframe, calling status_callback after each."""
    results = {}
    for exp in EXPERIMENTS:
        if status_callback:
            status_callback(exp['id'], 'running')
        try:
            result = exp['fn'](df)
            result['status'] = 'done'
        except Exception as e:
            result = {'status': 'failed', 'error': str(e), 'plots': [], 'findings': [f'Error: {e}']}
        results[exp['id']] = result
        if status_callback:
            status_callback(exp['id'], result['status'], result)
    return results
