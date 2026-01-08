import React, { useEffect, useState } from 'react'
import MapView from './components/MapView.jsx'
import ForecastChart from './components/ForecastChart.jsx'

const API_URL = 'http://localhost:5000'

export default function App() {
  // 状态管理
  const [turbines, setTurbines] = useState([])      // 所有风机列表
  const [selected, setSelected] = useState(null)    // 选中的风机
  const [forecast, setForecast] = useState(null)    // 预测结果

  // 组件加载时获取风机列表
  useEffect(() => {
    fetch(`${API_URL}/api/turbines`)
      .then(response => response.json())
      .then(data => setTurbines(data))
      .catch(error => console.error('Error loading turbines:', error))
  }, [])

  // 获取预测数据
  const getForecast = async () => {
    if (!selected) return
    
    // Cluster 1 无模型，显示故障停机
    if (selected.clusterId === 1) {
      setForecast({
        turbineId: selected.id,
        message: 'Turbine offline - maintenance required',
        predictions: null
      })
      return
    }
    
    try {
      const response = await fetch(`${API_URL}/api/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          turbineId: selected.id,
          startTime: new Date().toISOString()
        })
      })

      if (!response.ok) {
        alert('Failed to get forecast')
        return
      }

      const data = await response.json()
      setForecast(data)
    } catch (error) {
      console.error('Error getting forecast:', error)
      alert('Error getting forecast')
    }
  }

  return (
    <div>
      <MapView 
        turbines={turbines} 
        selected={selected} 
        onSelect={setSelected} 
      />
      
      <div className="panel">
        <div className="row">
          <div>
            {selected ? (
              <div>
                <div><strong>Turbine ID:</strong> {selected.id}</div>
                <div><strong>Cluster:</strong> {selected.clusterId}</div>
                <div><strong>Capacity:</strong> {selected.capacity} MW</div>
              </div>
            ) : (
              <div>Select a turbine on the map</div>
            )}
          </div>
          <button onClick={getForecast} disabled={!selected}>
            Get Forecast
          </button>
        </div>
        
        {forecast && <ForecastChart forecast={forecast} />}
      </div>
    </div>
  )
}
