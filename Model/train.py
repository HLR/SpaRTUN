from tqdm import tqdm
from transformers import BertTokenizer, BertTokenizerFast
import torch
from BertHelp import *


def train(model, training_set, optimizer, pretrain, epoch, device="cpu", rules_text=False):
    model.train()
    # Adding calculate loss, P, R, and F1
    pred_all = []
    actual_all = []
    additional_text = None
    if rules_text:
        rules = open("rules.txt", "r")
        additional_text = rules.readline()
    YN_classification = multiple_classification if pretrain == "bertmc" else boolean_classification
    for cur_epoch in range(epoch):
        pred = []
        actual = []
        for batch, (features, label) in enumerate(tqdm(training_set, desc="Training Epoch " + str(cur_epoch + 1))):
            question, text, q_type, candidate = features
            if additional_text:
                new_text = []
                for ind, story in enumerate(text):
                    new_text.append(story + additional_text)
                text = tuple(new_text)
            loss, output = YN_classification(model, question, text, q_type, candidate, label, device)

            pred.extend(output)
            actual.extend(label[0])

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        pred_all.append(pred)
        actual_all.append(actual)

    return pred_all, actual_all
