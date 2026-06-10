import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'edge-desktop',
      use: { ...devices['Desktop Edge'], channel: 'msedge', viewport: { width: 1488, height: 1058 } },
    },
    {
      name: 'edge-mobile',
      use: { ...devices['Pixel 7'], channel: 'msedge' },
    },
  ],
})

