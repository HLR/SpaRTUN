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

    features = []
    target = []
    count = 0
    answer_count = {}
    for story in data["data"][:size]:
        story_txt = story['story'][0]
        for question in story["questions"]:
            if count == size:
                break
            question_txt = question["question"]
            q_type = question["q_type"]
            candidates = question['candidate_answers']
            answer = question['answer'][0]
            if q_type != question_type:
                continue
            features.append((question_txt, story_txt, q_type, candidates))
            target.append(answer)
            if answer[0] not in answer_count:
                answer_count[answer[0]] = 0
            answer_count[answer[0]] += 1
            count += 1

    return features, target


def data_loader(file, question_type, size=None, batch_size=1):
    return DataLoader(SpaRTUNDataset(file, question_type, size), batch_size=batch_size)
