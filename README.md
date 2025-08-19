# AnomalyAgent - Behavioral Risk Detection API

[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com)

🤖 **AI-powered behavioral risk detection for agent trajectories**

Detect goal misalignment, deception, privacy violations, and other behavioral risks in AI agent interactions using a multi-agent analysis system.

**🚀 Quick Start**: Run `python run.py` to get started  
**📖 API Docs**: Available at `/docs` endpoint when server is running

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

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key

### Installation
```bash
# Clone the repository
git clone https://github.com/poonamsnair/AnomalyAgent.git
cd AnomalyAgent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start the API server
python3 run.py
```

The server will be available at the URLs shown in the startup output.

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
# Quick test scenarios
cd tests
python3 quick_scenario_test.py --list
python3 quick_scenario_test.py --scenario risky_001

# Full test suite
python3 runtime_test_runner.py
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
