from __future__ import print_function
import random
import sys
# -*- coding: utf-8 -*-
"""
How to use from command line:

[path]>python markov.py [WORDS_PER_LINE] [LINES] [Input text file 1] ...  [Input text file n]

The output will be written to a text file named "[Input text file 1]_output.txt"

"""


# takes a list of strings: each one is the path to a different txt file
def generate_table(files):
    INPUT_TEXT_FILES = files
    table = {}
    w1 = ""
    w2 = ""

    #Generate table from sample input text
    for i in range(len(INPUT_TEXT_FILES)):
        with open(INPUT_TEXT_FILES[i], "r") as ins:
            for line in ins:
                for word in line.split():
                    word = word.lower()
                    table.setdefault((w1, w2), []).append(word)
                    w1, w2 = w2, word
        ins.close()

        return table


#returns a list of strings: each string is a new line
# params: words per line, lines, markov table
def generate_markov_text(wpl, l, table):
    stop_strings = ['.', '!', '?', '*']
    continue_strings = [
        ',',
        'and',
        'i',
        'but',
    ]
    WORDS_PER_LINE = wpl
    LINES = l
    start_words = random.choice(table.keys())
    w1 = start_words[0]
    w2 = start_words[1]
    text = []

    stop_marks = 0

    for j in range(LINES):
        newLine = ""
        for i in range(WORDS_PER_LINE):
            word = random.choice(table[(w1, w2)])
            if word[-1] in stop_strings:
                stop_marks += 1
                if stop_marks >= 3:
                    break
            newLine += " %s" % (word)
            w1, w2 = w2, word
        text.append(newLine)

    return text


# table = generate_table(["titles.txt"])
# title = get_markov_text(15, 1, table)
# print(title)
