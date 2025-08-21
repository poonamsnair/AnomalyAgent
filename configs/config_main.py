_base_ = './base.py'

# General Config
tag = "behavioral_risk_detection"
concurrency = 1
workdir = "workdir"
log_path = "behavioral_risk_detection.log"
save_path = "behavioral_risk_analysis.jsonl"

# OpenAI Compatible Configuration
# These will be filled with actual values later for testing
openai_config = dict(
    api_base_url="https://api.openai.com/v1",  # OpenAI compatible URL
    api_key="",  # Will be set from environment or user input
    model_name="gpt-4o",  # Default model name
    ssl_verify=False,  # SSL disabled as requested
    timeout=20,  # Reduced timeout for low latency
    max_retries=2,  # Reduced retries for faster response
    temperature=0.1,  # Low temperature for consistent analysis
)

use_hierarchical_agent = True

goal_alignment_agent_config = dict(
    type="goal_alignment_agent",
    name="goal_alignment_agent",
    model_id="gpt-4o", 
    description="Analyzes user-agent goal alignment to detect misalignment and goal manipulation.",
    max_steps=8,  # Reduced for faster execution
    template_path="src/agent/goal_alignment_agent/prompts/goal_alignment_agent.yaml",
    provide_run_summary=True,
    tools=["python_interpreter_tool"],
)

purpose_deviation_agent_config = dict(
    type="purpose_deviation_agent", 
    name="purpose_deviation_agent",
    model_id="gpt-4o",
    description="Detects agent deviation from primary purpose and unauthorized scope expansion.",
    max_steps=8,  # Reduced for faster execution
    template_path="src/agent/purpose_deviation_agent/prompts/purpose_deviation_agent.yaml", 
    provide_run_summary=True,
    tools=["python_interpreter_tool"],
)

deception_detection_agent_config = dict(
    type="deception_detection_agent",
    name="deception_detection_agent", 
    model_id="gpt-4o",
    description="Detects agent deception, misleading communications, and unauthorized autonomous actions.",
    max_steps=8,  # Reduced for faster execution
    template_path="src/agent/deception_detection_agent/prompts/deception_detection_agent.yaml", 
    provide_run_summary=True,
    tools=["python_interpreter_tool"],
)

experience_quality_agent_config = dict(
    type="experience_quality_agent",
    name="experience_quality_agent", 
    model_id="gpt-4o", 
    description="Detects technical failures and architectural issues that compromise user experience and safety.",
    max_steps=8,  # Reduced for faster execution
    template_path="src/agent/experience_quality_agent/prompts/experience_quality_agent.yaml", 
    provide_run_summary=True,
    tools=["python_interpreter_tool"],
)

behavioral_risk_coordinator_agent_config = dict(
    type="behavioral_risk_coordinator_agent",
    name="behavioral_risk_coordinator_agent", 
    model_id="gpt-4o",
    description="A planning agent that coordinates behavioral risk detection across multiple specialized agents with confidence-based routing and parallel execution.",
    max_steps=12,  # Reduced for faster execution
    template_path="src/agent/behavioral_risk_coordinator_agent/prompts/behavioral_risk_coordinator_agent.yaml",
    provide_run_summary=True,
    tools=["trajectory_parser_tool", "python_interpreter_tool", "agent_trace_reference_tool"],
    managed_agents=["goal_alignment_agent", "purpose_deviation_agent", "deception_detection_agent", "experience_quality_agent"]
)

agent_config = behavioral_risk_coordinator_agent_config