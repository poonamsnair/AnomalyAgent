from mmengine.registry import Registry

DATASET = Registry('dataset', locations=['AnomalyAgent.src.dataset'])
TOOL = Registry('tool', locations=['AnomalyAgent.src.tools'])
AGENT = Registry('agent', locations=['AnomalyAgent.src.agent'])
ANOMALY_TOOL = Registry('anomaly_tool', locations=['AnomalyAgent.src.tools'])