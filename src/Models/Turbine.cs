using System.Text.Json;
using System.Text.Json.Serialization;

namespace TurbineForecast.Api.Models
{
    // 风机数据模型
    public class Turbine
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
        
        [JsonPropertyName("latitude")]
        public double Latitude { get; set; }
        
        [JsonPropertyName("longitude")]
        public double Longitude { get; set; }
        
        [JsonPropertyName("clusterId")]
        public int ClusterId { get; set; }
        
        [JsonPropertyName("capacity")]
        public double Capacity { get; set; } = 3.0;

        // 静态属性：所有风机数据（缓存）
        private static List<Turbine>? _allTurbines;
        public static List<Turbine> All
        {
            get
            {
                if (_allTurbines == null)
                {
                    _allTurbines = LoadTurbinesFromFile();
                }
                return _allTurbines;
            }
        }

        // 从JSON文件加载风机数据
        private static List<Turbine> LoadTurbinesFromFile()
        {
            try
            {
                // 查找data/turbines.json文件
                var projectRoot = Path.Combine(AppContext.BaseDirectory, "..", "..", "..");
                var dataPath = Path.Combine(projectRoot, "data", "turbines.json");
                var fullPath = Path.GetFullPath(dataPath);

                if (!File.Exists(fullPath))
                {
                    Console.WriteLine($"⚠ turbines.json not found at {fullPath}");
                    return GenerateFallbackData();
                }

                // 读取并解析JSON
                var json = File.ReadAllText(fullPath);
                using var doc = JsonDocument.Parse(json);
                var turbinesArray = doc.RootElement.GetProperty("turbines");
                
                var turbines = new List<Turbine>();
                foreach (var item in turbinesArray.EnumerateArray())
                {
                    turbines.Add(new Turbine
                    {
                        Id = item.GetProperty("turbineId").GetString() ?? "unknown",
                        Name = item.GetProperty("turbineId").GetString() ?? "Turbine",
                        ClusterId = item.GetProperty("clusterId").GetInt32(),
                        Latitude = item.GetProperty("latitude").GetDouble(),
                        Longitude = item.GetProperty("longitude").GetDouble(),
                        Capacity = item.TryGetProperty("capacity", out var cap) ? cap.GetDouble() : 3.0
                    });
                }

                Console.WriteLine($"✓ Loaded {turbines.Count} turbines from {fullPath}");
                return turbines;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"⚠ Error loading turbines: {ex.Message}");
                return GenerateFallbackData();
            }
        }

        // 生成备用数据（当JSON文件不存在时）
        private static List<Turbine> GenerateFallbackData()
        {
            Console.WriteLine("⚠ Using fallback turbine data");
            
            var turbines = new List<Turbine>();
            var random = new Random(42);

            // 在丹麦Zealand岛随机生成400个风机，完全覆盖整个岛屿
            // 西兰岛完整范围：纬度54.9-56.1，经度11.2-12.7
            // 不同集群的风机随机穿插分布
            
            for (int i = 0; i < 400; i++)
            {
                turbines.Add(new Turbine
                {
                    Id = $"T{i:000}",
                    Name = $"Turbine T{i:000}",
                    Latitude = Math.Round(54.9 + random.NextDouble() * 1.2, 4),    // 54.9 到 56.1
                    Longitude = Math.Round(11.2 + random.NextDouble() * 1.5, 4),   // 11.2 到 12.7
                    ClusterId = random.Next(0, 7),  // 随机分配集群0-6
                    Capacity = Math.Round(2.0 + random.NextDouble() * 2.5, 2)      // 2.0-4.5 MW
                });
            }

            return turbines.OrderBy(t => t.Id).ToList();
        }
    }
}
