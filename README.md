# AnomalyAgent - Behavioral Risk Detection API

[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com)

🤖 **AI-powered behavioral risk detection for agent trajectories**

Detect goal misalignment, deception, privacy violations, and other behavioral risks in AI agent interactions using a multi-agent analysis system.

**🚀 Quick Start**: Run `python3 start.py` to get started  
**🎭 Demo**: Run `python3 demo.py` for interactive demonstration  
**🧪 Test**: Run `python3 test.py` for validation  
**📖 API Docs**: Available at `/docs` endpoint when server is running

## 🚀 Features

- **Smart Behavioral Risk Detection**: Analyze AI agent trajectories for goal alignment, purpose deviation, deception, and experience quality issues
- **Confidence-Based Routing**: Early return on high-confidence assessments, full analysis when needed for optimal performance
- **Parallel Agent Execution**: 4x faster analysis with concurrent specialist agent processing
- **Agent Trace Reference**: Built-in guidance tool for optimal execution paths and performance benchmarks
- **Session Management**: In-memory session tracking for incremental risk assessment across multiple API calls
- **Multi-Agent Architecture**: Hierarchical agent system with specialized risk detection agents
- **Real-time Analysis**: Process trajectories in JSON, JSONL, or Skywork formats
- **OpenAI Compatible**: Simplified configuration supporting any OpenAI-compatible endpoint with SSL flexibility

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
- **Coordinator Agent**: Orchestrates multi-agent risk assessment with confidence-based routing and parallel execution

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key

### One-Command Setup
```bash
# Clone and setup with API key
git clone https://github.com/poonamsnair/AnomalyAgent.git
cd AnomalyAgent
chmod +x setup.sh

# Setup with your OpenAI API key
./setup.sh --api-key "your-api-key-here"

# Start the server
python3 start.py
```

### Manual Setup (Alternative)
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"  
export OPENAI_MODEL="gpt-4o"

# Start the server
python3 start.py
```

### Advanced Configuration
```bash
# Custom API endpoint and model
./setup.sh --api-key "sk-..." --api-base "https://custom-api.com/v1" --model "gpt-4"

# View all setup options
./setup.sh --help
```

The server will be available at http://localhost:8081 with API docs at `/docs`.

### Verification
```bash
# Test server health
curl http://localhost:8081/health

# Run quick validation
python3 demo.py

# Performance test
python3 test.py --quick
```

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

The system uses simplified OpenAI-compatible configuration in `configs/` directory:

### OpenAI-Compatible Configuration

**Automated Setup** (Recommended):
```bash
./setup.sh --api-key "your-key" --api-base "https://api.openai.com/v1" --model "gpt-4o"
```

**Manual Configuration**:
```python
openai_config = dict(
    api_base_url="https://api.openai.com/v1",  # Any OpenAI-compatible URL
    api_key="your-api-key-here",              # API key for authentication
    model_name="gpt-4o",                      # Model to use for analysis
    ssl_verify=False,                         # SSL verification disabled
    timeout=20,                               # Optimized for low latency
    max_retries=2,                           # Reduced for faster response
    temperature=0.1,                         # Low temperature for consistent analysis
)
```

**Environment Variables**:
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4o"
```

### Performance Optimizations
- **Low Latency**: 20s timeout, 8-12 max steps, 0.1 temperature
- **Confidence-Based Routing**: Early return on high confidence (60% time savings)
- **Parallel Execution**: 4x faster with concurrent specialist agents  
- **Agent Trace Reference**: Built-in optimal path guidance for performance tuning

## 🧪 Testing

```bash
# Quick validation
python3 test.py --quick

# Comprehensive test suite
python3 test.py

# Interactive demonstration
python3 demo.py
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

### v2.0.0 - Performance & Routing Improvements
- **Confidence-based routing**: Early return on high confidence assessments
- **Parallel agent execution**: 4x performance improvement with concurrent processing
- **Agent trace reference tool**: Optimal execution path guidance and benchmarks
- **Simplified OpenAI configuration**: SSL-flexible, any OpenAI-compatible endpoint
- **Smart behavioral analysis**: Intelligent routing based on initial risk assessment

### v1.0.0
- Initial release with core risk detection
- Session management system
- Multi-agent architecture
- OpenAI integration
