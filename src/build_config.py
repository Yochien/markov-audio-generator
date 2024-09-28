import json
import yaml
import argparse

from typing import Dict

parser = argparse.ArgumentParser(prog = "Markov Audio Config Builder",
                                 description = "Generates a template config for the Markov Audio Generator based on an input FSM file.")
parser.add_argument("input_file", type = str, help = "The exact location and name of the FSM file.")
parser.add_argument("-o", "--output_file", type = str, help = "The exact desired location and name of the final output file.",
                    default = "../output/sound_config_template.yaml")
args = parser.parse_args()
INPUT_FILE_NAME = args.input_file
OUTPUT_FILE_NAME = args.output_file

config_data = {}


def set_output_audio_config(config: Dict):
    config["minimum_simulation_length"] = 1
    config["maximum_simulation_length"] = 999


def load_state_names(filename: str):
    with open(filename, mode="r") as file:
        data = json.load(file)
        states = [node["text"] for node in data["nodes"]]
        return states


def set_state_group_map(config: Dict, filename: str):
    state_names = load_state_names(filename)

    state_groups = {}
    for state_name in state_names:
        state_groups[state_name] = f"{state_name}_choices"

    config["state_group_map"] = state_groups


def set_group_audio_map(config: Dict):
    EXAMPLE_FILES = ["./filename1", "./filename2", "./filename3"]
    group_placeholders = {}

    state_groups = config["state_group_map"]

    for group in state_groups:
        group_placeholders[state_groups[group]] = EXAMPLE_FILES.copy()

    config["group_audio_map"] = group_placeholders


def save_config(config_data: str, filename: str = OUTPUT_FILE_NAME):
    config_text = yaml.dump(config_data, default_flow_style=False)

    with open(filename, "w") as config_file:
        config_file.write(config_text)


set_output_audio_config(config_data)
set_state_group_map(config_data, INPUT_FILE_NAME)
set_group_audio_map(config_data)
save_config(config_data)
