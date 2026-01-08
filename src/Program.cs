using TurbineForecast.Api.Services;

var builder = WebApplication.CreateBuilder(args);

// Add CORS support (allow frontend to call API)
builder.Services.AddCors();

// Add Controllers support
builder.Services.AddControllers();

// Configure Python service URL
var pythonUrl = builder.Configuration.GetValue<string>("PythonServiceUrl") ?? "http://localhost:8000";

// Register ForecastService, use HttpClient to call Python service
builder.Services.AddHttpClient<ForecastService>(client =>
{
    client.BaseAddress = new Uri(pythonUrl);
});

var app = builder.Build();

// Enable CORS (development environment: allow all origins)
app.UseCors(policy => policy
    .AllowAnyOrigin()
    .AllowAnyMethod()
    .AllowAnyHeader());

// Map Controller routes
app.MapControllers();

// Start application
app.Run();

// Note: Production environment should restrict CORS origins, for example:
// .WithOrigins("https://your-frontend-domain.com")
