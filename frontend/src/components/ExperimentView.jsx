import { useState } from 'react'

export default function ExperimentView({ experiment, expMeta }) {
  const [expandedTable, setExpandedTable] = useState(null)

  if (!experiment) {
    return (
      <div className="experiment-loading">
        <div className="analyzing-spinner" />
        <p>{expMeta ? `Waking up Exp ${expMeta.num}: ${expMeta.name}...` : 'Select an experiment to view results'}</p>
      </div>
    )
  }

  if (experiment.status === 'failed') {
    return (
      <div className="experiment-view error-state">
        <div className="experiment-header">
          <div className="experiment-header-badge error">Exp. {experiment.num || expMeta?.num}</div>
          <h2>{experiment.name || expMeta?.name}</h2>
        </div>
        <div className="error-card">
          <div className="error-icon">⚠️</div>
          <h3>Experiment Failed</h3>
          <p>{experiment.error || 'An unknown error occurred during statistical analysis.'}</p>
          <div className="error-suggestion">
            Possible reasons: 
            <ul>
              <li>Insufficient numeric data for this specific test.</li>
              <li>Missing values (NaN) in required columns.</li>
              <li>Column names with special characters or spaces.</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  const name = experiment.name || expMeta?.name
  const num = experiment.num || expMeta?.num
  
  // Check if experiment has any data
  const hasData = experiment.findings || experiment.summary || experiment.plots || experiment.samples || experiment.coefficients || experiment.distributions || experiment.multiple_r || experiment.slr || experiment.descriptive_stats
  
  if (!hasData) {
    return (
      <div className="experiment-loading">
        <div className="analyzing-spinner" />
        <p>Loading {name} data...</p>
      </div>
    )
  }

  return (
    <div className="experiment-view">
      {/* Header */}
      <div className="experiment-header">
        <h2>{name}</h2>
      </div>

      {/* Findings */}
      {experiment.findings && experiment.findings.length > 0 && (
        <div className="experiment-findings">
          <h3>📋 Key Findings</h3>
          <ul>
            {experiment.findings.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Stats tables for specific experiments */}
      {experiment.summary && (
        <div className="experiment-stats-grid">
          {Object.entries(experiment.summary).map(([key, val]) => (
            <div key={key} className="stat-card">
              <div className="stat-value">{typeof val === 'number' ? val.toLocaleString() : val}</div>
              <div className="stat-label">{key.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      )}

      {/* SLR info */}
      {experiment.slr && (
        <div className="experiment-card">
          <h3>📐 Simple Linear Regression</h3>
          <div className="experiment-stats-grid">
            <div className="stat-card">
              <div className="stat-value">{experiment.slr.x_column}</div>
              <div className="stat-label">X Variable</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{experiment.slr.y_column}</div>
              <div className="stat-label">Y Variable</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{experiment.slr.correlation}</div>
              <div className="stat-label">Correlation</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{experiment.slr.r_squared}</div>
              <div className="stat-label">R²</div>
            </div>
          </div>
          <div className="experiment-equation">
            <code>{experiment.slr.equation}</code>
          </div>
        </div>
      )}

      {/* MLR info */}
      {experiment.coefficients && (
        <div className="experiment-card">
          <h3>📊 Regression Coefficients</h3>
          <div className="experiment-table-wrapper">
            <table className="experiment-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>Coefficient</th>
                </tr>
              </thead>
              <tbody>
                {experiment.coefficients.map((c, i) => (
                  <tr key={i}>
                    <td>{c.feature}</td>
                    <td><code>{c.coefficient}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {experiment.anova && (
            <div className="experiment-anova">
              <h4>ANOVA Table</h4>
              <div className="experiment-table-wrapper">
                <table className="experiment-table">
                  <thead>
                    <tr><th>Source</th><th>SS</th><th>df</th><th>MS</th><th>F</th><th>p</th></tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Regression</td>
                      <td>{experiment.anova.regression.SS}</td>
                      <td>{experiment.anova.regression.df}</td>
                      <td>{experiment.anova.regression.MS}</td>
                      <td>{experiment.anova.regression.F}</td>
                      <td><code>{experiment.anova.regression.p_value}</code></td>
                    </tr>
                    <tr>
                      <td>Residual</td>
                      <td>{experiment.anova.residual.SS}</td>
                      <td>{experiment.anova.residual.df}</td>
                      <td>{experiment.anova.residual.MS}</td>
                      <td>—</td>
                      <td>—</td>
                    </tr>
                    <tr>
                      <td>Total</td>
                      <td>{experiment.anova.total.SS}</td>
                      <td>{experiment.anova.total.df}</td>
                      <td>—</td>
                      <td>—</td>
                      <td>—</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* T-test / Z-test results */}
      {experiment.results && (experiment.results.one_sample || experiment.results.two_sample) && (
        <div className="experiment-card">
          {experiment.results.one_sample && Object.keys(experiment.results.one_sample).length > 0 && (
            <>
              <h3>🧪 One-Sample Test Results</h3>
              <div className="experiment-table-wrapper">
                <table className="experiment-table">
                  <thead>
                    <tr><th>Column</th><th>Mean</th><th>Statistic</th><th>p-value</th><th>Result</th></tr>
                  </thead>
                  <tbody>
                    {Object.entries(experiment.results.one_sample).map(([col, r]) => (
                      <tr key={col}>
                        <td>{col}</td>
                        <td>{r.sample_mean}</td>
                        <td>{r.t_statistic || r.z_statistic}</td>
                        <td><code>{r.p_value}</code></td>
                        <td>
                          <span className={`test-badge ${r.significant ? 'sig' : 'nsig'}`}>
                            {r.significant ? '✓ Significant' : '✗ Not Sig.'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
          {experiment.results.two_sample && Object.keys(experiment.results.two_sample).length > 0 && (
            <>
              <h3 style={{ marginTop: '20px' }}>🔬 Two-Sample Test</h3>
              <div className="two-sample-card">
                <div className="experiment-stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{experiment.results.two_sample.column_1}</div>
                    <div className="stat-label">Group 1 (μ = {experiment.results.two_sample.mean_1})</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{experiment.results.two_sample.column_2}</div>
                    <div className="stat-label">Group 2 (μ = {experiment.results.two_sample.mean_2})</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{experiment.results.two_sample.t_statistic || experiment.results.two_sample.z_statistic}</div>
                    <div className="stat-label">Test Statistic</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">
                      <span className={`test-badge ${experiment.results.two_sample.significant ? 'sig' : 'nsig'}`}>
                        {experiment.results.two_sample.conclusion}
                      </span>
                    </div>
                    <div className="stat-label">p = {experiment.results.two_sample.p_value}</div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* MLE distributions */}
      {experiment.distributions && (
        <div className="experiment-card">
          <h3>📊 Distribution Fitting Results</h3>
          {Object.entries(experiment.distributions).map(([col, dists]) => (
            <div key={col} className="distribution-card">
              <h4>{col}</h4>
              <div className="experiment-stats-grid">
                {dists.normal && (
                  <div className="stat-card">
                    <div className="stat-value">
                      μ={dists.normal.mu}, σ={dists.normal.sigma}
                    </div>
                    <div className="stat-label">
                      Normal {dists.normal.good_fit ? '✓' : '✗'} (KS p={dists.normal.ks_p_value})
                    </div>
                  </div>
                )}
                {dists.exponential && (
                  <div className="stat-card">
                    <div className="stat-value">λ={dists.exponential.lambda}</div>
                    <div className="stat-label">
                      Exponential {dists.exponential.good_fit ? '✓' : '✗'} (KS p={dists.exponential.ks_p_value})
                    </div>
                  </div>
                )}
                {dists.poisson && (
                  <div className="stat-card">
                    <div className="stat-value">λ={dists.poisson.lambda}</div>
                    <div className="stat-label">Poisson estimate</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sampling info */}
      {experiment.samples && (
        <div className="experiment-card">
          <h3>🎯 Sampling Methods</h3>
          <div className="experiment-stats-grid">
            {Object.entries(experiment.samples).map(([key, s]) => (
              <div key={key} className="stat-card">
                <div className="stat-value">{s.size}</div>
                <div className="stat-label">{s.method}</div>
                <div className="stat-detail">{s.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Multiple R */}
      {experiment.multiple_r && (
        <div className="experiment-card">
          <h3>📐 Multiple Correlation Coefficients</h3>
          <div className="experiment-table-wrapper">
            <table className="experiment-table">
              <thead>
                <tr><th>Variable</th><th>Multiple R</th><th>R²</th></tr>
              </thead>
              <tbody>
                {Object.entries(experiment.multiple_r).map(([col, r]) => (
                  <tr key={col}>
                    <td>{col}</td>
                    <td><code>{r.R}</code></td>
                    <td><code>{r.R_squared}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Plots */}
      {experiment.plots && experiment.plots.length > 0 && (
        <div className="experiment-plots">
          <h3>📈 Visualizations</h3>
          <div className="plots-grid">
            {experiment.plots.map((plot, i) => (
              <div key={i} className="plot-card">
                <h4>{plot.title}</h4>
                <img
                  src={`data:image/png;base64,${plot.image}`}
                  alt={plot.title}
                  className="plot-image"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Descriptive stats table */}
      {experiment.descriptive_stats && (
        <div className="experiment-card">
          <h3
            className="collapsible-heading"
            onClick={() => setExpandedTable(expandedTable === 'desc' ? null : 'desc')}
          >
            📋 Descriptive Statistics {expandedTable === 'desc' ? '▲' : '▼'}
          </h3>
          {expandedTable === 'desc' && (
            <div className="experiment-table-wrapper">
              <table className="experiment-table">
                <thead>
                  <tr>
                    {Object.keys(experiment.descriptive_stats[0] || {}).map(k => (
                      <th key={k}>{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {experiment.descriptive_stats.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((v, j) => (
                        <td key={j}>{v != null ? String(v) : '—'}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
