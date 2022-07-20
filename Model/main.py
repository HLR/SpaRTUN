import torch.optim

from reader import data_loader
from BertModels import BertForMultipleClass, BertForBooleanQuestion3ClassYN
from train import train
from eval import eval
import argparse


def main(args):
    training_file = "../Dataset/train.json"
    training_dataset = data_loader(training_file, args.qtype, size=args.training_size, batch_size=args.batch_size)
    testing_file = "../Dataset/test.json" if args.test_set != "human" else "../Dataset/human_test.json"
    testing_dataset = data_loader(testing_file, args.qtype, size=args.testing_size, batch_size=args.batch_size)

    # Set the cuda number we want to use
    cuda_number = args.cuda_number
    if cuda_number == -1:
        device = 'cpu'
    else:
        device = "cuda:" + str(cuda_number) if torch.cuda.is_available() else 'cpu'
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
    output_file = open("result_run.txt", "a")
    print("Result:", file=output_file)
    print("Epoch: ", args.epoch,  "lr: ", args.lr, file=output_file)
    print("Training: ", args.training_size, "Testing: ", args.testing_size, file=output_file)
    print("Test set: ", args.test_set, file=output_file)
    print("Model: ", args.pretrain, file=output_file)
    eval(model, testing_dataset, args.pretrain, output_file, device)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch", dest="epoch", type=int, default=1,
                        help="")
    parser.add_argument("--lr", dest="lr", type=float, default=1e-5,
                        help="")
    parser.add_argument("--cuda_number", dest="cuda_number", type=int, default=0,
                        help="")
    parser.add_argument("--training_size", dest="training_size", type=int, default=300000)
    parser.add_argument("--testing_size", dest="testing_size", type=int, default=300000)
    parser.add_argument("--test_set", dest="test_set", type=str, default="spartun",
                        help="Name of the testing dataset. Options is spartun or human")
    parser.add_argument("--batch_size", dest="batch_size", type=int, default=8)
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
