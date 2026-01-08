using Microsoft.AspNetCore.Mvc;
using TurbineForecast.Api.Models;

namespace TurbineForecast.Api.Controllers
{
    // 风机信息API控制器
    [ApiController]
    [Route("api/[controller]")]
    public class TurbinesController : ControllerBase
    {
        // 获取所有风机列表 - GET /api/turbines
        [HttpGet]
        public IActionResult GetAllTurbines()
        {
            return Ok(Turbine.All);
        }

        // 根据ID获取单个风机信息 - GET /api/turbines/{id}
        [HttpGet("{id}")]
        public IActionResult GetTurbineById(string id)
        {
            var turbine = Turbine.All.FirstOrDefault(t => 
                t.Id.Equals(id, StringComparison.OrdinalIgnoreCase));
            
            if (turbine == null)
            {
                return NotFound();
            }
            
            return Ok(turbine);
        }
    }
}
