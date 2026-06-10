import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('App', () => {
  it('identifies the trading command center', () => {
    render(<App />)

    expect(screen.getByText('Vol Backtester')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Run Backtest' })).toBeEnabled()
  })
})
