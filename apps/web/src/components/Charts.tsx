import ReactECharts from 'echarts-for-react'

import type { BacktestResult } from '../types'

const axis = { axisLine: { lineStyle: { color: '#29404d' } }, axisLabel: { color: '#8da1ad', fontSize: 10 }, splitLine: { lineStyle: { color: '#142733' } } }

export function Charts({ result }: { result: BacktestResult }) {
  const dates = result.equity_curve.map((point) => point.date)
  const equityOption = {
    animationDuration: 500,
    grid: [{ left: 58, right: 24, top: 42, height: '54%' }, { left: 58, right: 24, top: '74%', height: '17%' }],
    tooltip: { trigger: 'axis', backgroundColor: '#0d1b25', borderColor: '#29404d', textStyle: { color: '#edf6fb' } },
    legend: { top: 10, left: 18, textStyle: { color: '#a8bac4' }, data: ['Strategy'] },
    xAxis: [{ type: 'category', data: dates, boundaryGap: false, ...axis }, { type: 'category', data: dates, gridIndex: 1, boundaryGap: false, ...axis }],
    yAxis: [{ type: 'value', ...axis }, { type: 'value', gridIndex: 1, axisLabel: { formatter: (value: number) => `${(value * 100).toFixed(0)}%`, color: '#8da1ad' }, splitLine: { lineStyle: { color: '#142733' } } }],
    series: [
      { name: 'Strategy', type: 'line', data: result.equity_curve.map((point) => point.equity), showSymbol: false, lineStyle: { color: '#18c8ff', width: 1.6 }, areaStyle: { color: 'rgba(24,200,255,.05)' } },
      { name: 'Drawdown', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: result.equity_curve.map((point) => point.drawdown), showSymbol: false, lineStyle: { color: '#ff4d50', width: 1.2 }, areaStyle: { color: 'rgba(255,77,80,.28)' } },
    ],
  }
  const factorDates = result.factors.map((point) => point.date)
  const factorOption = {
    grid: { left: 58, right: 44, top: 44, bottom: 32 },
    tooltip: { trigger: 'axis', backgroundColor: '#0d1b25', borderColor: '#29404d', textStyle: { color: '#edf6fb' } },
    legend: { top: 10, left: 18, textStyle: { color: '#a8bac4' }, data: ['IV Percentile', 'Realized Vol'] },
    xAxis: { type: 'category', data: factorDates, boundaryGap: false, ...axis },
    yAxis: [{ type: 'value', min: 0, max: 100, ...axis }, { type: 'value', axisLabel: { formatter: (value: number) => `${(value * 100).toFixed(0)}%`, color: '#8da1ad' }, splitLine: { show: false } }],
    series: [
      { name: 'IV Percentile', type: 'line', data: result.factors.map((point) => point.iv_percentile_60), showSymbol: false, lineStyle: { color: '#18c8ff', width: 1.5 }, markLine: { symbol: 'none', lineStyle: { color: '#2d6f70', type: 'dashed' }, data: [{ yAxis: 20 }, { yAxis: 80 }] } },
      { name: 'Realized Vol', type: 'line', yAxisIndex: 1, data: result.factors.map((point) => point.rv20), showSymbol: false, lineStyle: { color: '#b8c4cb', width: 1.1 } },
      { name: 'Signals', type: 'scatter', data: result.factors.map((point, index) => point.signal === 'neutral' ? null : [index, point.iv_percentile_60]), symbol: 'triangle', symbolRotate: 0, symbolSize: 9, itemStyle: { color: '#39d875' } },
    ],
  }
  return (
    <div className="chart-stack">
      <section className="chart-panel"><div className="panel-title">Equity Curve <span>Strategy performance and drawdown</span></div><ReactECharts option={equityOption} style={{ height: 410 }} /></section>
      <section className="chart-panel factor-panel"><div className="panel-title">Implied Vol Percentile vs Realized Vol <span>20 / 60-day regime signals</span></div><ReactECharts option={factorOption} style={{ height: 270 }} /></section>
    </div>
  )
}

