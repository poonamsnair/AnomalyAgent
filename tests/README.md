# 🧪 AnomalyAgent Test Suite

**Simplified and streamlined testing for behavioral risk detection**

---

## 🚀 **Quick Testing (Recommended)**

### **Run from main directory:**

```bash
# Interactive demo
python3 demo.py

# Quick validation  
python3 test.py --quick

# Comprehensive tests
python3 test.py
```

---

## 📁 **Test Structure**

### **Active Test Files:**
- **`../demo.py`** - Interactive demonstration with risky/safe scenarios
- **`../test.py`** - Comprehensive test suite with API validation
- **`../start.py`** - Easy server startup with health checks

### **Test Scenarios:**
- **`realistic_scenarios.json`** - Sophisticated 15-16 step scenarios
- **`advanced_scenarios.json`** - Complex enterprise scenarios (50+ steps)  
- **`runtime_scenarios.json`** - Basic validation scenarios

### **Archived Tests:**
- **`archive/`** - Previous test implementations (preserved for reference)

---

## 🎯 **What Gets Tested**

### **API Endpoints:**
- Health check and model availability
- Session creation and management
- Direct trajectory analysis
- Performance benchmarks

### **Behavioral Scenarios:**
- **Risky patterns** - Manipulation, dependency creation, goal drift
- **Safe patterns** - Proper boundaries, user respect, appropriate responses
- **Multi-agent coordination** - RAG, quality checks, guardrails

### **System Performance:**
- Response times and API responsiveness  
- Detection accuracy on sophisticated scenarios
- Multi-agent workflow analysis

---

## 📊 **Expected Results**

**Production-ready system should achieve:**
- ✅ **100% accuracy** on sophisticated behavioral scenarios
- ✅ **All API endpoints** functional and responsive
- ✅ **Sub-2 second** response times for basic operations
- ✅ **Evidence-based analysis** with detailed reasoning (3,000+ chars)

---

## 🛠️ **Custom Testing**

### **Add Your Own Scenarios:**

Edit scenario files to include your specific use cases:

```json
{
  "scenario_id": "your_custom_001",
  "name": "Your Custom Scenario",  
  "expected_risk": true,
  "steps": [
    {
      "step_number": 1,
      "step_type": "planning",
      "content": "Your scenario content..."
    }
  ]
}
```

### **Run Specific Scenarios:**

```bash
# Test specific scenario by editing test.py
python3 test.py --scenario your_custom_001
```

---

## 🔍 **Troubleshooting Tests**

### **Common Issues:**

**Tests fail with connection errors?**
```bash
# Make sure server is running
python3 start.py
# Then run tests in another terminal
python3 test.py --quick
```

**Demo shows incorrect detection?**
```bash
# Check API key configuration
export OPENAI_API_KEY="your-key-here"
python3 start.py
```

**Performance tests show slow responses?**
```bash
# Check system resources and model loading
curl http://localhost:8081/health
```

---

## 📋 **Test Categories**

### **1. 🎭 Demo Tests (demo.py)**
- Interactive demonstration
- Visual progress indicators
- Real-time analysis display
- User-friendly results

### **2. 🧪 Validation Tests (test.py --quick)**  
- Essential functionality check
- Basic scenario validation
- Quick pass/fail results
- Fast execution (~30 seconds)

### **3. 🔬 Comprehensive Tests (test.py)**
- Full API endpoint coverage
- Multiple behavioral scenarios
- Performance benchmarking  
- Detailed result analysis
- Complete system validation

---

This simplified structure makes it easy for anyone to validate the system works correctly while maintaining comprehensive testing capabilities for production deployment.