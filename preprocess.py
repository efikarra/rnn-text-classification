import nltk
import itertools
import numpy as np
import os
import argparse
import io

def build_vocabulary(tokenized_seqs, max_freq=0.0, min_freq=0.0):
    # compute word frequencies
    vocab=set()
    freq_dist=nltk.FreqDist(itertools.chain(*tokenized_seqs))
    sorted_words = dict(sorted(freq_dist.items(), key=lambda x: x[1])).keys()
    max_idx=len(vocab)-1
    min_idx=0
    if isinstance(max_freq, float):
        max_idx=len(sorted_words)-int(np.ceil(max_freq * len(sorted_words)))
    if isinstance(min_freq, float):
        min_idx=int(np.ceil(min_freq * len(sorted_words)))
    vocab=sorted_words[min_idx:max_idx]
    return vocab

def tokenize(data, delimiter=" "):
    data_tok=[]
    for d in data:
        data_tok.append(d.split(delimiter))
    return data_tok


def load_data_from_file(filepath):
    with io.open(filepath, "r", encoding="utf-8") as f:
        data=f.read().splitlines()
    return data


def save_to_file(filepath, data):
    with io.open(filepath, 'w', encoding="utf-8") as f:
        newline = ""
        for d in data:
            f.write(unicode(newline+str(d)))
            newline="\n"


def avg_seq_length(seq_tok):
    sum_len=0.0
    max=0.0
    min=10000000
    for seq in seq_tok:
        sum_len+=len(seq)
        if len(seq)>max:max=len(seq)
        if len(seq) < min: min = len(seq)
    return sum_len/len(seq_tok),max,min


def convert_to_ovr(class_one, input_labels):
    ovr_labels = []
    for l in input_labels:
        ovr_labels.append('1' if int(l)==class_one else '0')
    return ovr_labels


def preprocess_data(params):
    data_folder = params.data_folder
    train_input_file = params.train_input_file
    train_target_file = params.train_target_file
    val_input_file = params.dev_input_file
    val_target_file = params.dev_target_file
    test_input_file = params.test_input_file
    test_target_file = params.test_target_file

    train_input=load_data_from_file(os.path.join(data_folder,train_input_file))
    train_target = load_data_from_file(os.path.join(data_folder,train_target_file))
    val_input = load_data_from_file(os.path.join(data_folder,val_input_file))
    val_target = load_data_from_file(os.path.join(data_folder,val_target_file))
    test_input = load_data_from_file(os.path.join(data_folder,test_input_file))
    test_target = load_data_from_file(os.path.join(data_folder,test_target_file))
    print("Train input: %d "% len(train_input))
    print("Train labels: %d " % len(train_target))
    print("Val input: %d " % len(val_input))
    print("Val labels: %d " % len(val_target))
    print("Test size: %d " % len(test_input))
    print("Test labels: %d " % len(test_target))

    # import json
    # lid2lab = json.load(open("experiments/data/lid2lab.json"))
    # lab2shortname = json.load(open("experiments/data/lab2shortname.json"))
    # for i in range(10):
    #     print train_input[i]
    #     print lab2shortname[lid2lab[int(train_target[i])]]

    train_tok=tokenize(train_input)
    val_tok = tokenize(val_input)
    test_tok = tokenize(test_input)

    avg_train_len,max_train_len,min_train_len=avg_seq_length(train_tok)
    avg_val_len, max_val_len, min_val_len =avg_seq_length(val_tok)
    avg_test_len, max_test_len, min_test_len =avg_seq_length(test_tok)
    print("Train: avg_seq_length = %.3f, max seq length = %d, min seq length = %d "%(avg_train_len,max_train_len,min_train_len))
    print("Dev: avg_seq_length = %.3f, max seq length = %d, min seq length = %d " % (avg_val_len, max_val_len, min_val_len))
    print("Test: avg_seq_length = %.3f, max seq length = %d, min seq length = %d " % (avg_test_len, max_test_len, min_test_len))

    vocab = build_vocabulary(train_tok, max_freq=params.max_freq, min_freq=params.min_freq)
    print("Vocab size: %d " % len(vocab))
    save_to_file(os.path.join(data_folder,str(params.max_freq)+str(params.min_freq)+params.vocab_file), vocab)

    create_ovr_data(params, train_target, val_target, test_target, range(32))


def create_ovr_data(params, train_target, val_target, test_target,classes):
    for c in classes:
        train_target_ovr = convert_to_ovr(class_one=c, input_labels=train_target)
        val_target_ovr = convert_to_ovr(class_one=c, input_labels=val_target)
        test_target_ovr = convert_to_ovr(class_one=c, input_labels=test_target)
        save_to_file(os.path.join("experiments/ovr_targets",str(c)+"_"+params.train_target_file), train_target_ovr)
        save_to_file(os.path.join("experiments/ovr_targets",str(c)+"_"+params.dev_target_file), val_target_ovr)
        save_to_file(os.path.join("experiments/ovr_targets",str(c)+"_"+params.test_target_file), test_target_ovr)


def add_arguments(parser):
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--data_folder", type=str, default=None)
    parser.add_argument("--train_input_file", type=str, default=None)
    parser.add_argument("--train_target_file", type=str, default=None)
    parser.add_argument("--dev_input_file", type=str, default=None)
    parser.add_argument("--dev_target_file", type=str, default=None)
    parser.add_argument("--test_input_file", type=str, default=None)
    parser.add_argument("--test_target_file", type=str, default=None)
    parser.add_argument("--vocab_file", type=str, default=None)
    parser.add_argument("--min_freq", type=float, default=0.0)
    parser.add_argument("--max_freq", type=float, default=0.0)

def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    params, unparsed = parser.parse_known_args()
    preprocess_data(params)

if __name__ == '__main__':
    main()