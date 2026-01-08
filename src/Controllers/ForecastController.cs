using Microsoft.AspNetCore.Mvc;
using TurbineForecast.Api.Models;
using TurbineForecast.Api.Services;

namespace TurbineForecast.Api.Controllers
{
    // Wind power forecasting API controller
    [ApiController]
    [Route("api/[controller]")]
    public class ForecastController : ControllerBase
    {
        private readonly ForecastService _forecastService;
        
        public ForecastController(ForecastService forecastService)
        {
            _forecastService = forecastService;
        }
            //Get the 24-hour power forecast of the wind turbine -POST /api/forecast
        [HttpPost]
        public async Task<IActionResult> GetForecast([FromBody] ForecastRequest request)
        {
            // 1. Find turbine information
            var turbine = Turbine.All.FirstOrDefault(t =>
                t.Id.Equals(request.TurbineId, StringComparison.OrdinalIgnoreCase));
            
            if (turbine == null)
            {
                return NotFound(new { message = "Turbine not found" });
            }
            // 2. Call the Python service to obtain prediction results
            var forecast = await _forecastService.GetForecastAsync(
                turbine.Id,
                turbine.ClusterId,
                turbine.Capacity,
                request.StartTime);
            
            if (forecast == null)
            {
                return StatusCode(502, new { message = "Python service error" });
            }

            // 3. Return the prediction result
            return Ok(forecast);
        }
    }
}