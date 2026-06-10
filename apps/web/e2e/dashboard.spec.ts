import { expect, test } from '@playwright/test'

test('loads the command center and opens parameters', async ({ page }, testInfo) => {
  const consoleErrors: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })

  await page.goto('/')
  await expect(page).toHaveTitle('Vol Backtester')
  if (testInfo.project.name === 'edge-desktop') {
    await expect(page.getByText('Vol Backtester')).toBeVisible()
  } else {
    await expect(page.getByRole('button', { name: 'Run Backtest' })).toBeVisible()
  }
  await expect(page.getByText('Risk & Exposure')).toBeVisible()
  await expect(page.locator('.panel-title').filter({ hasText: 'Equity Curve' })).toBeVisible()
  await expect(page.getByText('Loading analytics...')).toHaveCount(0)
  await page.waitForTimeout(700)
  await page.screenshot({
    path: testInfo.outputPath(`command-center-overview-${testInfo.project.name}.png`),
    fullPage: false,
  })
  await page.getByRole('button', { name: 'Parameters' }).click()
  await expect(page.getByRole('dialog', { name: 'Backtest parameters' })).toBeVisible()
  await page.screenshot({
    path: testInfo.outputPath(`command-center-${testInfo.project.name}.png`),
    fullPage: true,
  })

  expect(consoleErrors).toEqual([])
})

test('runs a real API backtest and updates the dashboard', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Run Backtest' }).click()
  await expect(page.getByText('Completed')).toBeVisible({ timeout: 45_000 })
  await expect(page.getByText('Ready')).toHaveCount(0)
})

test('uploads a CSV dataset through the command bar', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Upload option-chain CSV').setInputFiles({
    name: 'edge-chain.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from(
      'date,expiry,option_type,strike,bid,ask,implied_volatility,underlying_price\n' +
        '2025-01-02,2025-02-21,call,100,4.0,4.2,0.2,100\n',
    ),
  })

  await expect(page.getByText('Imported CSV: edge-chain.csv (1 rows)')).toBeVisible()
})

test('desktop sidebar navigation is interactive', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'edge-desktop', 'The mobile layout hides the sidebar.')
  await page.goto('/')
  const navigation = page.getByLabel('Primary navigation')

  await navigation.getByRole('button', { name: 'Strategies' }).click()
  await expect(page.getByRole('dialog', { name: 'Backtest parameters' })).toBeVisible()
  await page.getByRole('button', { name: 'Close parameters' }).click()

  for (const item of ['Backtests', 'Results', 'Positions', 'Data']) {
    await navigation.getByRole('button', { name: item }).click()
    await expect(navigation.getByRole('button', { name: item })).toHaveAttribute(
      'aria-current',
      'page',
    )
  }

  await navigation.getByRole('button', { name: 'Trade Log' }).click()
  await expect(page.getByRole('columnheader', { name: 'P/L' })).toBeVisible()

  await navigation.getByRole('button', { name: 'Settings' }).click()
  await expect(page.getByRole('dialog', { name: 'Backtest parameters' })).toBeVisible()
  await page.getByRole('button', { name: 'Close parameters' }).click()

  await page.getByRole('button', { name: 'Collapse sidebar' }).click()
  await expect(page.getByRole('button', { name: 'Expand sidebar' })).toBeVisible()
})
