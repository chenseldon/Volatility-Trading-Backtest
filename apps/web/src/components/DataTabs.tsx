import { useState } from 'react'

import type { BacktestResult } from '../types'

export function DataTabs({ result }: { result: BacktestResult }) {
  const [tab, setTab] = useState('Positions')
  const tabs = ['Positions', 'Trades', 'Comparison', 'Assumptions']
  const sourceLabel =
    result.data_source === 'synthetic' ? 'Synthetic option-chain data' : 'Imported option-chain CSV'
  return (
    <section className="data-panel">
      <div className="tabs">{tabs.map((name) => <button className={tab === name ? 'active' : ''} onClick={() => setTab(name)} key={name}>{name}</button>)}</div>
      {tab === 'Positions' && <table><thead><tr><th>Type</th><th>Expiry</th><th>Strike</th><th>Qty</th><th>Entry</th></tr></thead><tbody>
        {result.legs.slice(-6).map((leg, index) => <tr key={`${String(leg.strike)}-${index}`}><td>{String(leg.option_type).toUpperCase()}</td><td>{String(leg.expiry)}</td><td>{String(leg.strike)}</td><td className={Number(leg.quantity) < 0 ? 'negative' : 'positive'}>{String(leg.quantity)}</td><td>{Number(leg.entry_price).toFixed(2)}</td></tr>)}
      </tbody></table>}
      {tab === 'Trades' && <table><thead><tr><th>Date</th><th>Event</th><th>Strategy</th><th>Reason / Signal</th><th>P/L</th></tr></thead><tbody>
        {result.trades.slice(-8).reverse().map((trade, index) => <tr key={`${trade.date}-${index}`}><td>{trade.date}</td><td>{trade.event.toUpperCase()}</td><td>{trade.strategy.replaceAll('_', ' ')}</td><td>{trade.reason ?? trade.signal}</td><td className={trade.pnl >= 0 ? 'positive' : 'negative'}>{trade.pnl.toFixed(2)}</td></tr>)}
      </tbody></table>}
      {tab === 'Comparison' && <div className="text-panel"><strong>Parameter comparison</strong><p>Use the sweep API to rank holding periods and signal thresholds by Sharpe ratio.</p></div>}
      {tab === 'Assumptions' && <div className="text-panel"><strong>{sourceLabel}</strong><p>Black-Scholes proxy, no early exercise, bid/ask execution, Reg-T style margin, and explicit commissions/slippage.</p>{result.warnings.map((warning) => <p key={warning}>{warning}</p>)}</div>}
    </section>
  )
}
