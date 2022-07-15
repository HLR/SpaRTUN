from tqdm import tqdm
from transformers import BertTokenizer, BertTokenizerFast
import torch


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokenizerFast = BertTokenizerFast.from_pretrained('bert-base-uncased')


def predict_label(result_list):
    label = torch.argmax(result_list).item()
    return ["Yes"] if label == 0 else ["No"] if label == 1 else ["DK"]


def boolean_classification(model, question, text, q_types, candidate, correct_labels, device):
    encoding = tokenizer(question, text, padding="max_length")
    input_ids = encoding["input_ids"]

    # To prevent outside to know about this
    labels = []
    for ind, correct_label in enumerate(correct_labels[0]):
        q_type = q_types[ind]
        label = [0]
        if q_type == "YN":
            if correct_label == "Yes":
                label = [1, 0, 0]
            elif correct_label == "No":
                label = [0, 1, 0]
            else:
                label = [0, 0, 1]
        labels.append(label)
    labels = torch.LongTensor(labels).to(device).transpose(0, 1)
    input_ids = torch.LongTensor(input_ids).to(device)
    outputs = model(input_ids, labels=labels)
    loss, pred_label = outputs[0], predict_label(outputs[1])

    return loss, pred_label


def multiple_classification(model, question, text, q_types, candidate, correct_labels, device):
    encoding = tokenizer(question, text, padding="max_length")
    input_ids = encoding["input_ids"]

    # To prevent outside to know about this
    labels = []
    for ind, correct_label in enumerate(correct_labels[0]):
        q_type = q_types[ind]
        label = [0]
        if q_type == "YN":
            if correct_label == "Yes":
                label = [0]
            elif correct_label == "No":
                label = [1]
            else:
                label = [2]
        labels.append(label)
    labels = torch.LongTensor(labels).to(device).transpose(0, 1)
    input_ids = torch.LongTensor(input_ids).to(device)
    outputs = model(input_ids, labels=labels)
    loss, pred_label = outputs[0], predict_label(outputs[1])

    return loss, pred_label