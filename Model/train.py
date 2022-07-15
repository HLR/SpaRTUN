from tqdm import tqdm
from transformers import BertTokenizer, BertTokenizerFast
import torch
from BertHelp import *


def train(model, training_set, optimizer, pretrain, epoch, device="cpu"):
    model.train()
    # Adding calculate loss, P, R, and F1
    pred = []
    actual = []
    YN_classification = multiple_classification if pretrain == "bertmc" else boolean_classification
    for batch, (features, label) in enumerate(tqdm(training_set, desc="Training Epoch" + str(epoch))):
        question, text, q_type, candidate = features
        loss, output = YN_classification(model, question, text, q_type, candidate, label, device)

        pred.append(pred)
        actual.append(label)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return pred, actual
