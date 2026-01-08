import React, { useEffect } from 'react'
import L from 'leaflet'

export default function MapView({ turbines, selected, onSelect }) {
  useEffect(() => {
    // 创建地图，中心点设在丹麦Zealand岛
    const map = L.map('map').setView([55.5, 12.0], 9)
    
    // 添加OpenStreetMap图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap'
    }).addTo(map)

    // 定义7个集群的颜色
    const clusterColors = [
      '#FF6B6B',  // Cluster 0: 红色
      '#4ECDC4',  // Cluster 1: 青色
      '#45B7D1',  // Cluster 2: 蓝色
      '#FFA07A',  // Cluster 3: 橙色
      '#98D8C8',  // Cluster 4: 绿色
      '#F7DC6F',  // Cluster 5: 黄色
      '#BB8FCE'   // Cluster 6: 紫色
    ]

    // 为每个风机添加带颜色的标记
    const markers = []
    turbines.forEach(turbine => {
      const color = clusterColors[turbine.clusterId] || '#3388ff'
      
      // 创建自定义图标（带颜色的圆点）
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.4);"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
      })
      
      const marker = L.marker([turbine.latitude, turbine.longitude], { icon })
        .addTo(map)
        .bindPopup(`${turbine.name}<br/>Cluster ${turbine.clusterId}`)
        .on('click', () => onSelect(turbine))
      
      markers.push(marker)
    })

    // 组件卸载时清理地图
    return () => {
      markers.forEach(m => m.remove())
      map.remove()
    }
  }, [turbines, onSelect])

  return <div id="map"></div>
}
