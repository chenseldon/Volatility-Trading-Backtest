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

  it('uploads an option-chain CSV and selects it for the next run', async () => {
    const user = userEvent.setup()
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        dataset: 'upload:abc123',
        name: 'chain.csv',
        rows: 120,
      }),
    } as Response)

    render(<App />)
    const file = new File(['date,expiry\n'], 'chain.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText('Upload option-chain CSV'), file)

    expect(await screen.findByText('Imported CSV: chain.csv (120 rows)')).toBeInTheDocument()
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/datasets/upload',
      expect.objectContaining({ method: 'POST', body: expect.any(FormData) }),
    )
  })

  it('rejects invalid signal thresholds before calling the API', async () => {
    const user = userEvent.setup()
    const request = vi.spyOn(globalThis, 'fetch')

    render(<App />)
    await user.click(screen.getByRole('button', { name: 'Parameters' }))
    await user.clear(screen.getByLabelText('High IV percentile'))
    await user.type(screen.getByLabelText('High IV percentile'), '10')
    await user.click(screen.getByRole('button', { name: 'Run Backtest' }))

    expect(
      screen.getByText('Low IV percentile must be below high IV percentile'),
    ).toBeInTheDocument()
    expect(request).not.toHaveBeenCalled()
  })
})
