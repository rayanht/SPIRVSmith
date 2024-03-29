#!bash
DD_AGENT_MAJOR_VERSION=7 DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
mv datadog_conf.yaml /etc/datadog-agent/conf.d/python.d/conf.yaml
yq -yi .logs_enabled=true /etc/datadog-agent/datadog.yaml
touch infra/spirvsmith_gcp.json
echo $GOOGLE_CREDENTIALS | base64 -d > infra/spirvsmith_gcp.json
DD_SERVICE="spirvsmith" DD_ENV="prod" DD_LOGS_INJECTION=true DD_PROFILING_ENABLED=true ddtrace-run python3 run.py hydra.run.dir=. hydra.output_subdir=null hydra/job_logging=none hydra/hydra_logging=none
