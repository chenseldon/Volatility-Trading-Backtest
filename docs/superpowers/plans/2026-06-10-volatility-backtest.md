# Volatility Trading Backtest Implementation Plan

> **For agentic workers:** Implement milestones in order with test-first development
> and one verified commit per milestone.

**Goal:** Build a reproducible options-volatility backtest engine, API, dashboard,
reports, documentation, and public GitHub repository.

**Architecture:** A Python package owns all business behavior. FastAPI and CLI call a
shared service. React/Vite renders and controls runs through the API.

**Tech Stack:** Python 3.12, Pandas, NumPy, Matplotlib, FastAPI, React, TypeScript,
Vite, ECharts, Pytest, Vitest.

Milestones and acceptance criteria are defined in the user-approved plan and tracked
in repository commits `v0.1` through `v1.0`.

