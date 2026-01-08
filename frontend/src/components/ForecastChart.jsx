import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'

// 注册Chart.js组件
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function ForecastChart({ forecast }) {
  if (!forecast) {
    return <div>No forecast data</div>
  }
  
  // 如果是故障停机消息
  if (forecast.message && !forecast.predictions) {
    return (
      <div style={{ 
        padding: '20px', 
        textAlign: 'center', 
        color: '#e74c3c', 
        fontSize: '18px',
        fontWeight: 'bold'
      }}>
        ⚠️ {forecast.message}
      </div>
    )
  }
  
  if (!forecast.predictions) {
    return <div>No forecast data</div>
  }
  
  // 准备图表数据
  const hours = forecast.predictions.map(p => p.hour)
  const powers = forecast.predictions.map(p => p.power)
  const maxPower = Math.max(...powers)
  
  const chartData = {
    labels: hours,
    datasets: [{
      label: `Power Forecast (${forecast.turbineId}) - MW`,
      data: powers,
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.3  // 使曲线平滑
    }]
  }
  
  const chartOptions = {
    responsive: true,
    plugins: { 
      legend: { position: 'top' },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.y.toFixed(2)} MW`
        }
      }
    },
    scales: {
      x: {
        title: { display: true, text: 'Hour' }
      },
      y: { 
        min: 0, 
        max: Math.ceil(maxPower * 1.1),  // Y轴最大值为最大功率的1.1倍
        title: { display: true, text: 'Power (MW)' }
      }
    }
  }

  return <Line data={chartData} options={chartOptions} />
}
