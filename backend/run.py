"""
Backend Server Launcher for NBFC Loan Platform
Configures Uvicorn with increased HTTP header buffer (1MB) to prevent HTTP 431 errors
caused by bloated development cookies on localhost.
"""
import uvicorn

if __name__ == "__main__":
    print("\n🚀 Starting NBFC Loan Chatbot API Server...")
    print("📍 URL: http://localhost:8000")
    print("📚 Swagger Docs: http://localhost:8000/docs")
    print("⚡ Max Header Buffer: 1MB (Prevents HTTP 431)\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        http="h11",
        h11_max_incomplete_event_size=1048576,  # 1MB buffer for large browser cookie headers
        ws_max_size=10485760                   # 10MB WebSocket frame limit
    )
