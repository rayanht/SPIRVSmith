#!bash
DD_AGENT_MAJOR_VERSION=7 DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
mv datadog_conf.yaml /etc/datadog-agent/conf.d/python.d/conf.yaml
git clone https://github.com/Gallore/yaml_cli
cd yaml_cli
pip install .
yaml_cli -f /etc/datadog-agent/datadog.yaml -b logs_enabled true
python3 run.py hydra.run.dir=. hydra.output_subdir=null hydra/job_logging=none hydra/hydra_logging=none
