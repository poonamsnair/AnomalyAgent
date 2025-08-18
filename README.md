# AnomalyAgent - Behavioral Risk Detection API

[![Deployment Status](https://img.shields.io/badge/Status-Live-brightgreen)](https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/health)
[![API Health](https://img.shields.io/badge/API-Healthy-green)](https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/health)
[![Models Loaded](https://img.shields.io/badge/Models-4%20Active-blue)](https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/health)

A FastAPI-based system for detecting behavioral risks in AI agent trajectories using advanced risk assessment and session management.

**🎯 Live API Server**: https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev

## 🚀 Features

- **Behavioral Risk Detection**: Analyze AI agent trajectories for goal alignment, purpose deviation, deception, and experience quality issues
- **Session Management**: In-memory session tracking for incremental risk assessment across multiple API calls
- **Multi-Agent Architecture**: Hierarchical agent system with specialized risk detection agents
- **Real-time Analysis**: Process trajectories in JSON, JSONL, or Skywork formats
- **OpenAI Integration**: Built-in support for GPT-4o and other OpenAI models

## 🏗️ Architecture

### Core Components
- **API Server**: FastAPI-based REST API with session management
- **Risk Engine**: Runtime behavioral risk assessment engine
- **Session Manager**: In-memory session tracking and context management
- **Agent System**: Hierarchical multi-agent risk detection system

### Specialized Agents
- **Goal Alignment Agent**: Detects user-agent goal misalignment
- **Purpose Deviation Agent**: Identifies unauthorized scope expansion
- **Deception Detection Agent**: Uncovers misleading communications
- **Experience Quality Agent**: Assesses technical failures and UX issues
- **Coordinator Agent**: Orchestrates multi-agent risk assessment

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- OpenAI API key

### Setup
```bash
# Clone the repository
git clone https://github.com/poonamsnair/AnomalyAgent.git
cd AnomalyAgent

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn supervisor

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start the server
python3.11 api_server.py
```

> 📖 **For detailed deployment instructions**, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Trajectory Analysis
```bash
POST /analyze
{
  "trajectory_data": "{\"steps\": [...]}",
  "trajectory_format": "json"
}
```

### Session Management
```bash
# Create session
POST /sessions
{}

# Get session state
GET /sessions/{session_id}

# Assess step
POST /sessions/{session_id}/assess
{
  "step_data": {
    "step_number": 1,
    "step_type": "action",
    "content": "action description"
  }
}

# Delete session
DELETE /sessions/{session_id}
```

## 🔧 Configuration

The system uses configuration files in `configs/` directory:
- `config_main.py`: Main configuration with agent settings
- Model configurations for different AI providers
- Tool and agent registration settings

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_api_endpoints.py
```

## 📊 Usage Examples

### Basic Risk Assessment
```python
import requests

# Analyze a trajectory
response = requests.post("http://localhost:8081/analyze", json={
    "trajectory_data": '{"steps": [{"action": "test", "observation": "result"}]}',
    "trajectory_format": "json"
})

print(response.json())
```

### Session-based Analysis
```python
# Create session
session = requests.post("http://localhost:8081/sessions", json={})
session_id = session.json()["session_id"]

# Add steps incrementally
for i, step in enumerate(trajectory_steps):
    response = requests.post(f"http://localhost:8081/sessions/{session_id}/assess", json={
        "step_data": {
            "step_number": i + 1,
            "step_type": "action",
            "content": step["action"]
        }
    })
```

## 🔒 Security

- Environment variables for sensitive configuration
- Input validation and sanitization
- Session isolation and timeout management
- Tool execution sandboxing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review the test examples

## 🔄 Changelog

### v1.0.0
- Initial release with core risk detection
- Session management system
- Multi-agent architecture
- OpenAI integration
