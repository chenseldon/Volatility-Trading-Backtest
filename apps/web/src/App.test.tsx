import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'

vi.mock('echarts-for-react', () => ({
  default: ({ option }: { option: { title?: { text?: string } } }) => (
    <div data-testid="chart">{option.title?.text}</div>
  ),
}))

afterEach(() => {
  vi.restoreAllMocks()
})

describe('App', () => {
  it('identifies the trading command center', () => {
    render(<App />)

    expect(screen.getByText('Vol Backtester')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Run Backtest' })).toBeEnabled()
    expect(screen.getByText('Risk & Exposure')).toBeInTheDocument()
    expect(screen.getByText('Synthetic option-chain data')).toBeInTheDocument()
  })

  it('opens parameters and runs a backtest through the API', async () => {
    const user = userEvent.setup()
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        run_id: 'abc123',
        status: 'completed',
        data_source: 'synthetic',
        metrics: {
          annualized_return: 0.1876,
          sharpe_ratio: 1.42,
          max_drawdown: -0.1283,
          win_rate: 0.6427,
          profit_factor: 1.78,
          trade_count: 64,
        },
        equity_curve: [],
        factors: [],
        exposures: [],
        trades: [],
        legs: [],
        warnings: [],
        config: {},
      }),
    } as Response)

    render(<App />)
    await user.click(screen.getByRole('button', { name: 'Parameters' }))
    expect(screen.getByRole('dialog', { name: 'Backtest parameters' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Run Backtest' }))

    expect(await screen.findByText('Completed')).toBeInTheDocument()
    expect(screen.getByText('18.76%')).toBeInTheDocument()
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/backtests',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
