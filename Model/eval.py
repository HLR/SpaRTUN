from tqdm import tqdm
from transformers import BertTokenizer, BertTokenizerFast
import torch
from BertHelp import *
import numpy as np
import pandas as pd


def eval(model, testing_set, pretrain, output_file, device="cpu", rules_text=False):
    model.eval()
    # Adding calculate loss, P, R, and F1
    pred_all = []
    actual_all = []
    error_data = {"story": [], "question": [], "actual": [], "pred": []}
    additional_text = None
    if rules_text:
        rules = open("rules.txt", "r")
        additional_text = rules.readline()
    YN_classification = multiple_classification if pretrain == "bertmc" else boolean_classification
    for batch, (features, label) in enumerate(tqdm(testing_set, desc="Testing")):
        questions, text, q_type, candidate = features
        if additional_text:
            new_text = []
            for ind, story in enumerate(text):
                new_text.append(story + additional_text)
            text = tuple(new_text)
        loss, output = YN_classification(model, questions, text, q_type, candidate, label, device)

        pred_all.extend(output)
        actual_all.extend(label)
        for ind, question in enumerate(questions):
            if output[ind] != label[ind]:
                error_data["story"].append(text[ind])
                error_data["question"].append(question)
                error_data["actual"].append(label[ind])
                error_data["pred"].append(output[ind])

    TP, TPFN, TPFP = np.array([0] * 3), np.array([0] * 3), np.array([0] * 3)

    for ind, pred in enumerate(pred_all):
        actual = actual_all[ind]
        if actual == "Yes":
            TPFN[0] += 1
        elif actual == "No":
            TPFN[1] += 1
        else:
            TPFN[2] += 1

        if pred == "Yes":
            TPFP[0] += 1
            if pred == actual:
                TP[0] += 1
        elif pred == "No":
            TPFP[1] += 1
            if pred == actual:
                TP[1] += 1
        else:
            TPFP[2] += 1
            if pred == actual:
                TP[2] += 1

    print('TP:', TP, '  TPFP: ', TPFP, '   TPFN: ', TPFN, file=output_file)
    Precision = np.nan_to_num(TP / TPFP)
    Recall = np.nan_to_num(TP / TPFN)
    F1 = np.nan_to_num((2 * (Precision * Recall)) / (Precision + Recall))
    Macro_F1 = np.average(F1)

    print('Test Final Precision: ', Precision, file=output_file)

    print('Test Final Recall: ', Recall, file=output_file)

    print('Test Final F1: ', F1, file=output_file)

    print('Test Final Macro_F1: ', Macro_F1, file=output_file)

    print("Acc: ", np.sum(TP) / len(pred_all), file=output_file)

    error_data = pd.DataFrame(error_data)
    error_data.to_csv("result.csv")

    return pred_all, actual_all
