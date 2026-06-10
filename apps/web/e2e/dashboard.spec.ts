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
  await expect(page.getByText('Loading analytics…')).toHaveCount(0)
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
