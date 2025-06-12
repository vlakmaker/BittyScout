# utils/source_config_loader.py
import yaml
import os

def load_job_sources(path="config/job_sources.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
