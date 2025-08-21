module.exports = {
  apps: [{
    name: 'anomaly-agent-api',
    script: 'api_server.py',
    interpreter: 'python',
    cwd: '/home/user/webapp',
    env: {
      'OPENAI_API_KEY': 'YOUR_OPENAI_API_KEY_HERE',
      'PYTHONPATH': '/home/user/webapp/src:/home/user/webapp'
    },
    args: '--config configs/config_main.py --host 0.0.0.0 --port 8081',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    log_file: '/home/user/webapp/anomaly_agent.log',
    out_file: '/home/user/webapp/anomaly_agent.out',
    error_file: '/home/user/webapp/anomaly_agent.err',
    time: true
  }]
};
