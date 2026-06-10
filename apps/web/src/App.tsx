import './styles.css'

export default function App() {
  return (
    <main className="app-shell">
      <header className="command-bar">
        <div>
          <strong>Vol Backtester</strong>
          <span>Command Center</span>
        </div>
        <button type="button">Run Backtest</button>
      </header>
      <section className="empty-state">
        <h1>SPY Volatility Research</h1>
        <p>Synthetic option-chain data · Local research environment</p>
      </section>
    </main>
  )
}

