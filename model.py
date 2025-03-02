import torch
import torch.nn as nn
from modules import measure_embedding_network
from modules import classify_network, RIS_phase_optimization_network
from torch.nn import LSTMCell
import time

class RecurrentAttention(nn.Module):

    def __init__(self, measure_embedding_hidden_size, RIS_phase_power_embedding_hidden_size, RIS_phase_optimization_hidden_size,
                 classify_hidden_size, used_channel, rnn_hidden_size, num_classes, learned_start, transmit_scale):
        super(RecurrentAttention, self).__init__()
        self.used_channel = used_channel
        self.measure_embedding = measure_embedding_network(measure_embedding_hidden_size, RIS_phase_power_embedding_hidden_size, 
                                                           learned_start, self.used_channel, transmit_scale)
        self.lstm = LSTMCell(RIS_phase_power_embedding_hidden_size[-1], rnn_hidden_size)
        self.classifier = classify_network(rnn_hidden_size, classify_hidden_size[0], num_classes)
        self.RIS_phase_optimization = RIS_phase_optimization_network(rnn_hidden_size, RIS_phase_optimization_hidden_size[0], used_channel[0].shape[1])


    def forward(self, x, RIS_phase_power_t_prev, state_t_prev):

        measure_embedding_t = self.measure_embedding(x, RIS_phase_power_t_prev)
        state_t = self.lstm(torch.squeeze(measure_embedding_t), state_t_prev) # state_t includes two components: hidden state and cell state
        classifier_log_prob = self.classifier(state_t[0])
        RIS_phase_power_next = self.RIS_phase_optimization(state_t[0].unsqueeze(dim=1))
        
        return state_t, RIS_phase_power_next, classifier_log_prob
