from transformers import BertModel, BertPreTrainedModel
from torch import nn
import torch
from torch.autograd import Variable
import torch.nn.functional as F


class FocalLoss(nn.Module):
    r"""
        This criterion is a implemenation of Focal Loss, which is proposed in
        Focal Loss for Dense Object Detection.

            Loss(x, class) = - \alpha (1-softmax(x)[class])^gamma \log(softmax(x)[class])

        The losses are averaged across observations for each minibatch.
        Args:
            alpha(1D Tensor, Variable) : the scalar factor for this criterion
            gamma(float, double) : gamma > 0; reduces the relative loss for well-classiﬁed examples (p > .5),
                                   putting more focus on hard, misclassiﬁed examples
            size_average(bool): size_average(bool): By default, the losses are averaged over observations for each minibatch.
                                However, if the field size_average is set to False, the losses are
                                instead summed for each minibatch.
    """

    def __init__(self, class_num, alpha=None, gamma=2, size_average=True):
        super(FocalLoss, self).__init__()
        if alpha is None:
            self.alpha = Variable(torch.ones(class_num, 1))
        else:
            if isinstance(alpha, Variable):
                self.alpha = alpha
            else:
                self.alpha = Variable(alpha)
        self.gamma = gamma
        self.class_num = class_num
        self.size_average = size_average

    def forward(self, inputs, targets):
        N = inputs.size(0)
        C = inputs.size(1)
        P = F.softmax(inputs)

        class_mask = inputs.data.new(N, C).fill_(0)
        class_mask = Variable(class_mask)
        ids = targets.view(-1, 1)
        class_mask.scatter_(1, ids.data, 1.)

        if inputs.is_cuda and not self.alpha.is_cuda:
            self.alpha = self.alpha.cuda()
        alpha = self.alpha[ids.data.view(-1)]

        probs = (P * class_mask).sum(1).view(-1, 1)

        log_p = probs.log()

        batch_loss = -alpha * (torch.pow((1 - probs), self.gamma)) * log_p

        if self.size_average:
            loss = batch_loss.mean()
        else:
            loss = batch_loss.sum()
        return loss


class BertForMultipleClass(BertPreTrainedModel):
    def __init__(self, config, device="cpu", drp=False):
        super().__init__(config)

        if drp:
            config.hidden_dropout_prob = 0.0
            config.attention_probs_dropout_prob = 0.0

        self.cur_device = device
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.num_classes = 3

        self.clf = nn.Linear(config.hidden_size, self.num_classes)
        self.alphas = torch.tensor([[0.67, 1.3, 1.32]]).to(self.cur_device)
        classifiers = []
        self.criterion = []
        for item in range(1):
            classifiers.append(nn.Linear(config.hidden_size, self.num_classes))
            self.criterion.append(FocalLoss(alpha=self.alphas[item], class_num=self.num_classes, gamma=2))
        self.classifiers = nn.ModuleList(classifiers)
        self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax()

        self.init_weights()

    def forward(
            self,
            input_ids=None,
            attention_mask=None,
            token_type_ids=None,
            position_ids=None,
            head_mask=None,
            inputs_embeds=None,
            labels=None,
    ):
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
        )

        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)

        logits = []

        for ind in range(1):
            logit = self.classifiers[ind](pooled_output)

            logits.append(logit.squeeze(0))

        if labels is not None:
            loss = 0
            out_logits = []
            for ind, logit in enumerate(logits):
                loss += self.criterion[ind](logit.unsqueeze(0), labels[ind].unsqueeze(0))
                out_logits.append(self.softmax(logit))
            outputs = (loss, torch.stack(out_logits),) + outputs[2:]

        return outputs


class BertForBooleanQuestion3ClassYN(BertPreTrainedModel):
    # TODO: Rewrite this
    def __init__(self, config, device="cpu", drp=False):
        super().__init__(config)

        if drp:
            config.hidden_dropout_prob = 0.0
            config.attention_probs_dropout_prob = 0.0

        self.cur_device = device
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.num_classes = 2

        self.classifier = nn.Linear(config.hidden_size, self.num_classes)
        self.alphas = torch.tensor([[0.5, 0.5], [0.5, 0.5], [1, 0]]).to(self.cur_device)
        classifiers = []
        self.criterion = []
        # Create three output from the model
        for item in range(3):
            classifiers.append(nn.Linear(config.hidden_size, self.num_classes))
            self.criterion.append(FocalLoss(alpha=self.alphas[item], class_num=self.num_classes, gamma=2))
        self.classifiers = nn.ModuleList(classifiers)
        self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax()

        self.init_weights()

    # @add_start_docstrings_to_callable(BERT_INPUTS_DOCSTRING)
    def forward(
            self,
            input_ids=None,
            attention_mask=None,
            token_type_ids=None,
            position_ids=None,
            head_mask=None,
            inputs_embeds=None,
            labels=None,
    ):
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
        )

        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        #         print('$',pooled_output.shape)
        logits = []
        #         for ind, logit in enumerate(pooled_output):
        #             logit = self.classifiers[ind](pooled_output[ind])
        #             logits.append(logit)
        for ind in range(3):
            logit = self.classifiers[ind](pooled_output)
            #             print("#", logit.squeeze(0).shape)
            logits.append(logit.squeeze(0))

        if labels is not None:

            loss = 0
            out_logits = []
            for ind, logit in enumerate(logits):
                sent_logit = logit.unsqueeze(0) if logit.dim() == 1 else logit
                loss += self.criterion[ind](sent_logit, labels[ind].unsqueeze(0))

                out_logits.append(self.softmax(logit).unsqueeze(0) if logit.dim() == 1 else self.softmax(logit))

            outputs = (loss, torch.stack(out_logits),) + outputs[2:]

        return outputs
