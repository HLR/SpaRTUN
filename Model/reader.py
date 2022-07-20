import json
import numpy as np
import re
import random

import torch
from torch.utils.data import random_split, DataLoader, Dataset


class SpaRTUNDataset(Dataset):
    __slots__ = ["data", "target"]

    def __init__(self, file, question_type, size):
        self.data, self.target = reader(file, question_type, size)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, ind):
        return self.data[ind], self.target[ind]


def reader(file, question_type, size=None):
    with open(file) as json_file:
        data = json.load(json_file)
    size = len(data["data"]) if not size else size
    size = min(len(data["data"]), size)

    features = []
    target = []
    count = 0
    for story in data["data"]:
        story_txt = story['story'][0]
        for question in story["questions"]:
            if count == size:
                break

            question_txt = question["question"]

            q_type = question["q_type"]
            if q_type != question_type:
                continue

            candidates = question['candidate_answers']

            answer = ""
            if q_type == "YN":
                answer = question['answer'][0]

            features.append((question_txt, story_txt, q_type, candidates))
            target.append(answer)
            count += 1

    return features, target


def data_loader(file, question_type, size=None, batch_size=1):
    return DataLoader(SpaRTUNDataset(file, question_type, size), batch_size=batch_size)
