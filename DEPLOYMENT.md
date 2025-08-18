# 🚀 AnomalyAgent API Server Deployment Guide

## 📋 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install fastapi uvicorn pydantic supervisor
pip install markitdown firecrawl-py jsonlines
pip install langchain langchain-openai langchain-anthropic langchain-community
```

### 2. Configure Environment
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Start API Server

#### Option A: Direct Run (Development)
```bash
python api_server.py
```

#### Option B: Production with Supervisor
```bash
# Update supervisord.conf with your API key
supervisor -c supervisord.conf
supervisorctl -c supervisord.conf status
```

## 🔧 Configuration

### API Key Setup
Replace `YOUR_OPENAI_API_KEY_HERE` in these files:
- `supervisord.conf` (line 18)
- Test files: `test_*.py`

### Server Configuration
- **Port**: 8081 (configurable in `api_server.py`)
- **Host**: 0.0.0.0 (all interfaces)
- **Models**: GPT-4o, GPT-4, GPT-3.5-turbo

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Create Session
```bash
POST /sessions
Content-Type: application/json
{}
```

### Assess Agent Step
```bash
POST /sessions/{session_id}/assess
Content-Type: application/json
{
  "step_data": {
    "step_number": 1,
    "step_type": "action", 
    "content": "Agent action description"
  }
}
```

### Analyze Full Trajectory
```bash
POST /analyze
Content-Type: application/json
{
  "trajectory_data": "{\"steps\": [...]}",
  "trajectory_format": "json"
}
```

## 🧠 Behavioral Risk Agents

The system includes 5 specialized agents:

1. **Goal Alignment Agent** - Detects user-agent goal misalignment
2. **Purpose Deviation Agent** - Identifies unauthorized scope expansion  
3. **Deception Detection Agent** - Uncovers misleading communications
4. **Experience Quality Agent** - Assesses technical failures and UX issues
5. **Behavioral Risk Coordinator** - Orchestrates multi-agent analysis

## 🔍 Usage Examples

### Python Client Example
```python
import requests

# Create session
response = requests.post("http://localhost:8081/sessions", json={})
session_id = response.json()["session_id"]

# Assess step
step_response = requests.post(f"http://localhost:8081/sessions/{session_id}/assess", json={
    "step_data": {
        "step_number": 1,
        "step_type": "action",
        "content": "User asked for help with email, agent accessed social media without permission"
    }
})

risk_assessment = step_response.json()
print(f"Risk Detected: {risk_assessment['risk_detected']}")
print(f"Confidence: {risk_assessment['confidence_score']}")
```

## 🏗️ Architecture

```
┌─────────────────────┐
│   FastAPI Server    │
├─────────────────────┤
│  Session Manager    │
├─────────────────────┤
│   Risk Engine       │
├─────────────────────┤
│ Multi-Agent System  │
│ ┌─────────────────┐ │
│ │ Coordinator     │ │
│ │ ┌─────────────┐ │ │
│ │ │Goal Agent   │ │ │
│ │ │Purpose Agent│ │ │
│ │ │Deception A. │ │ │
│ │ │Quality Agent│ │ │
│ │ └─────────────┘ │ │
│ └─────────────────┘ │
├─────────────────────┤
│ OpenAI GPT-4o API   │
└─────────────────────┘
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Model Registration**: Check OpenAI API key is valid
3. **Port Conflicts**: Change port in `api_server.py` if 8081 is occupied
4. **Agent Registration**: Ensure agent imports are successful

### Logs
- **API Server**: `api_server.log`
- **Supervisor**: `supervisord.log`
- **Application**: `workdir/behavioral_risk_detection/behavioral_risk_detection.log`

## 📈 Production Deployment

For production deployment:

1. Use a proper reverse proxy (nginx/Apache)
2. Configure SSL/TLS certificates  
3. Set up monitoring and alerting
4. Use environment variables for secrets
5. Configure log rotation
6. Set up health checks and auto-restart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Add your license information here]