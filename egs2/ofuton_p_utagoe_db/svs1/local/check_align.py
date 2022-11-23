#!/usr/bin/env python3
import argparse
import math
import os
import sys

from espnet2.fileio.read_text import read_label
from espnet2.fileio.score_scp import read_score
from espnet2.text.build_tokenizer import build_tokenizer

customed_dic = {
    "へ": ["h", "e"],
    "は": ["h", "a"],
    "シ": ["sh", "I"],
    "ヴぁ": ["v", "a"],
    "ヴぃ": ["v", "i"],
    "ヴぇ": ["v", "e"],
    "ヴぉ": ["v", "o"],
    "でぇ": ["dy", "e"],
    "くぁ": ["k", "w", "a"],
    "くぃ": ["k", "w", "i"],
    "くぅ": ["k", "w", "u"],
    "くぇ": ["k", "w", "e"],
    "くぉ": ["k", "w", "o"],
    "ぐぁ": ["g", "w", "a"],
    "ぐぃ": ["g", "w", "i"],
    "ぐぅ": ["g", "w", "u"],
    "ぐぇ": ["g", "w", "e"],
    "ぐぉ": ["g", "w", "o"],
    "くぉっ": ["k", "w", "o", "cl"],
}


def compare(key, score, label):
    tokenizer = build_tokenizer(
        token_type="phn",
        bpemodel=None,
        delimiter=None,
        space_symbol="<space>",
        non_linguistic_symbols=None,
        g2p_type=args.g2p,
    )
    index = 0
    score_error = -1
    phoneme_error = -1
    for i in range(len(score)):
        syb = score[i][2]
        phns = tokenizer.g2p(syb)
        if syb in customed_dic:
            phns = customed_dic[syb]
        score[i].append("_".join(phns))
        for p in phns:
            if index >= len(labels):
                raise ValueError("Syllables are longer than phonemes in {}".format(key))
            elif label[index][2] == p:
                index += 1
            else:
                raise ValueError(
                    "Mismatch between syllable [{}]->{} and {}-th phonemes ['{}'] in {}. ".format(
                        syb, phns, index, label[index][2], key
                    )
                )
    if index != len(label):
        raise ValueError("Syllables are shorter than phonemes in {}: ".format(key))
    return score


def get_parser():
    parser = argparse.ArgumentParser(
        description="Compare segments between label and score",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("scp", type=str, help="scp folder")
    parser.add_argument("--g2p", type=str, help="g2p", default="pyopenjtalk")

    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()
    labels = read_label(os.path.join(args.scp, "label"))
    scores = read_score(os.path.join(args.scp, "score"))
    update_score = open(os.path.join(args.scp, "score.tmp"), "w", encoding="utf-8")
    for key in scores:
        scores[key] = scores[key][0], compare(key, scores[key][1], labels[key])
        update_score.write("{}  {}".format(key, scores[key][0]))
        for v in scores[key][1]:
            update_score.write("  {} {} {} {} {}".format(v[0], v[1], v[2], v[3], v[4]))
        update_score.write("\n")
