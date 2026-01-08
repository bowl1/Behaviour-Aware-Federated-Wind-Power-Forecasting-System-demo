using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace TurbineForecast.Api.Services
{
    // Service class for calling Python prediction service
    public class ForecastService
    {
        private readonly HttpClient _httpClient;

        public ForecastService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        // Get 24-hour power forecast
        public async Task<ForecastResponse?> GetForecastAsync(
            string turbineId, 
            int clusterId, 
            double capacity, 
            DateTime startTime)
        {
            // 1. Prepare request data
            var requestData = new
            {
                turbineId,
                clusterId,
                capacity,
                startTime = startTime.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            };

            try
            {
                // 2. Call Python service /predict endpoint
                var response = await _httpClient.PostAsJsonAsync("predict", requestData);
                
                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Python service error: {response.StatusCode}");
                    return null;
                }

                // 3. Parse response result
                var result = await response.Content.ReadFromJsonAsync<ForecastResponse>();
                return result;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error calling Python service: {ex.Message}");
                return null;
            }
        }
        
        // Single prediction point (one hour of power prediction)
        public class PredictionPoint
        {
            [JsonPropertyName("hour")] 
            public int Hour { get; set; }
            
            [JsonPropertyName("power")] 
            public double Power { get; set; }
        }

        // Forecast response (containing 24-hour predictions)
        public class ForecastResponse
        {
            [JsonPropertyName("turbineId")] 
            public string TurbineId { get; set; } = string.Empty;
            
            [JsonPropertyName("clusterId")] 
            public int ClusterId { get; set; }
            
            [JsonPropertyName("predictions")] 
            public List<PredictionPoint> Predictions { get; set; } = new();
        }
    }
}
