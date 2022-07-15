import torch.optim

from reader import data_loader
from BertModels import BertForMultipleClass, BertForBooleanQuestion3ClassYN
from train import train
from eval import eval
import argparse


def main(args):
    training_file = "../Dataset/train.json"
    training_dataset = data_loader(training_file, args.qtype, batch_size=4)

    device = "cpu"
    if args.pretrain == 'bertmc':
        if args.qtype == 'YN':
            model = BertForMultipleClass.from_pretrained('bert-base-uncased', device=device, drp=args.dropout)
            if args.unfreeze:
                for name, param in list(model.bert.named_parameters())[:(-12 * args.unfreeze) - 2]:
                    # print('I will be frozen: {}'.format(name))
                    param.requires_grad = False
            model.to(device)

    else:
        if args.qtype == 'YN':
            model = BertForBooleanQuestion3ClassYN.from_pretrained('bert-base-uncased', device=device, drp=args.dropout)
            if args.unfreeze:
                for name, param in list(model.bert.named_parameters())[:(-12 * args.unfreeze) - 2]:
                    # print('I will be frozen: {}'.format(name))
                    param.requires_grad = False
            model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    pred, actual = train(model, training_dataset, optimizer, args.pretrain, args.epoch, device)
    pred, actual = eval(model, training_dataset, optimizer, args.pretrain, args.epoch, device)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch", dest="epoch", type=int, default=1,
                        help="")
    parser.add_argument("--lr", dest="lr", type=float, default=1e-5,
                        help="")
    parser.add_argument("--pretrain", dest="pretrain", type=str, default="bertbl",
                        help="Name of the pretrained model. Options is bertmc or bertbc")
    parser.add_argument("--qtype", dest="qtype", type=str, default="YN",
                        help="Name of the question type. Options is YN or FR")
    parser.add_argument("--dropout", dest="dropout", type=bool, default=False,
                        help="")
    parser.add_argument("--unfreeze", dest="unfreeze", type=bool, default=False,
                        help="")
    args = parser.parse_args()
    main(args)
