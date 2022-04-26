#!bash
DD_SERVICE="spirvsmith" DD_ENV="prod" DD_LOGS_INJECTION=true DD_PROFILING_ENABLED=true ddtrace-run python3 run.py hydra.run.dir=. hydra.output_subdir=null hydra/job_logging=none hydra/hydra_logging=none
