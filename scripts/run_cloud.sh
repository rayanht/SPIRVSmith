#!bash
DD_AGENT_MAJOR_VERSION=7 DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
python3 run.py hydra.run.dir=. hydra.output_subdir=null hydra/job_logging=none hydra/hydra_logging=none
