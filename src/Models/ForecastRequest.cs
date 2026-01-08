using System;

namespace TurbineForecast.Api.Models
{
    public class ForecastRequest
    {
        public string TurbineId { get; set; } = string.Empty;
        public DateTime StartTime { get; set; }
    }
}
