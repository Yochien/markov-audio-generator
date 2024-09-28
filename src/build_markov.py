import json
import yaml
import numpy as np
from pydub import AudioSegment
import random
import argparse

from typing import List


class Node:
    def __init__(self, state_name: str, is_accept_state: bool = False):
        self.state_name = state_name
        self.is_accept_state = is_accept_state

    def __str__(self):
        return f"Node[state_name: {self.state_name}, isAcceptState: {self.is_accept_state}]"


class Link:
    def find_transition_chance(self, link_text):
        if link_text == "":
            return 1
        else:
            return float(link_text)

    def __init__(self, from_node: Node, to_node: Node, link_text: str):
        self.from_node = from_node
        self.to_node = to_node
        self.transition_chance = self.find_transition_chance(link_text)

    def __str__(self):
        return f"{self.from_node.state_name} --> {self.to_node.state_name} w/ {self.transition_chance * 100:.0f}% chance"


class Sampler():
    def __init__(self, config):
        self.config = config
        self.audio_groups = self.load_audio_groups()
        self.state_group_map = self.config["state_group_map"]

    def load_audio_groups(self):
        audio_groups = {}
        group_audio_map = self.config["group_audio_map"]

        for group_name, sample_locations in group_audio_map.items():
            group_samples = []
            for sample_location in sample_locations:
                sample = AudioSegment.empty()
                try:
                    sample = AudioSegment.from_file(sample_location)
                except FileNotFoundError:
                    print("Could not find file for", sample_location)
                    sample = AudioSegment.empty()
                group_samples.append(sample)

            audio_groups[group_name] = group_samples

        return audio_groups

    def getRandomSample(self, choices: list[AudioSegment]):
        return choices[random.randrange(len(choices))]

    def getRandomSampleByState(self, state_name: str):
        if state_name in self.state_group_map:
            group_name = self.state_group_map[state_name]
            choices = self.audio_groups[group_name]
            return self.getRandomSample(choices)
        else:
            return AudioSegment.empty()


parser = argparse.ArgumentParser(prog = "Markov Audio Generator",
                                 description = "Generates an audio file based on the input FSM file.")
parser.add_argument("input_fsm", type = str, help = "The exact location and name of the input FSM file.")
parser.add_argument("config_file", type = str, help = "The exact location and name of the config file (generated from the Markov Audio Config Builder).")
parser.add_argument("-o", "--output_file", type = str, help = "The exact desired location and name of the final output file.",
                    default = "../output/markov_audio.wav")
args = parser.parse_args()
INPUT_FILE_NAME = args.input_fsm
CONFIG_FILE_NAME = args.config_file
OUTPUT_FILE_NAME = args.output_file

nodes: List[Node] = []
links: List[Link] = []

with open(INPUT_FILE_NAME, mode="r") as file:
    data = json.load(file)
    for data_node in data["nodes"]:
        node = Node(data_node["text"], data_node["isAcceptState"])
        nodes.append(node)
    for data_link in data["links"]:
        if data_link["type"] == "Link":
            nodeA = nodes[int(data_link["nodeA"])]
            nodeB = nodes[int(data_link["nodeB"])]
            link = Link(nodeA, nodeB, data_link["text"])
            links.append(link)
        elif data_link["type"] == "SelfLink":
            node = nodes[int(data_link["node"])]
            link = Link(node, node, data_link["text"])
            links.append(link)

# Initialize transition table
transition_table = []
num_nodes = len(nodes)
for node in nodes:
    row = (node.state_name, [0 for _ in range(num_nodes)])
    transition_table.append(row)

# Fill in transition values from links
for row in transition_table:
    row_state_name = row[0]
    row_links = [link for link in links if link.from_node.state_name == row_state_name]

    for link in row_links:
        state_index = nodes.index(link.to_node)
        row[1][state_index] = link.transition_chance


with open(CONFIG_FILE_NAME, 'r') as file:
    STATE_NAMES = [node.state_name for node in nodes]
    config = yaml.safe_load(file)
    min_sim_len = config["minimum_simulation_length"]
    max_sim_len = config["maximum_simulation_length"]
    current_sim_cycles = 0
    sampler = Sampler(config)

    sim_result = []
    while (len(sim_result) < min_sim_len) and (current_sim_cycles < max_sim_len):
        sim_result.clear()
        current_state = transition_table[0][0]
        sim_result.append(current_state)
        current_sim_cycles += 1

        while (current_state != "end") and (current_sim_cycles < max_sim_len):
            current_state = np.random.choice(STATE_NAMES, p = transition_table[STATE_NAMES.index(current_state)][1])
            sim_result.append(current_state)
            current_sim_cycles += 1

    if current_sim_cycles >= max_sim_len:
        print("Audio generation ended early due to reaching maximum allowed cycles.")
        print("Raise this in your config if this is stopping you from generating the length of piece you want.")

    final = AudioSegment.empty()

    print("Generated states:", ", ".join(sim_result))

    for state_name in sim_result:
        final = final + sampler.getRandomSampleByState(state_name)

    final.export(OUTPUT_FILE_NAME, format="wav")
