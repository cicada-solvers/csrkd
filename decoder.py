from nltk import everygrams
import enchant, sys, time, math
from math import log
from threading import Thread
from pathlib import Path

#Running key shift decoder for Cicada 3301

#Read in the dictionary for english check in the end
d = enchant.Dict("en_US")

#Threading
threads = 4

#Runes and corresponding letters
runes = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚩ', 'ᚱ', 'ᚳ', 'ᚷ', 'ᚹ', 'ᚻ', 'ᚾ', 'ᛁ', 'ᛄ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛋ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚪ', 'ᚫ', 'ᚣ', 'ᛡ', 'ᛠ']
letters = ['F', 'U', 'TH', 'O', 'R', 'K', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X', 'Z', 'T', 'B', 'E', 'M', 'L', 'ING', 'OE', 'D', 'A', 'AE', 'Y', 'IO', 'EA']

#LP text in runes
cipher = open('pages.txt', encoding='utf-8').read()

#Red Book LP, thanks mortlach
key = open('cipher_key.txt', encoding='utf-8').read()

#Space estimation
words = open("words.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

#Filter the LP (no spaces, only runes)
filtered_text = []
for char in cipher:
    if char in runes:
        filtered_text += char

#Filter the key (Red Book LP, no spaces, only runes, using mortlach's rune version)
filtered_key = []
for char in key:
    if char in runes:
        filtered_key += char

#Generate key function
def generateKey(filtered_text, filtered_key):
    times=len(filtered_text)//len(filtered_key)+1
    key = (times*filtered_key)[:len(filtered_text)]
    return key

# Find the best match for the i first characters, assuming cost has
# been built for the i-1 first characters.
# Returns a pair (match_cost, match_length).
def best_match(i, s, cost):
    candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
    return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

def infer_spaces(s):

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i, s, cost)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i, s, cost)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))

def decoder(minrange, maxrange, filtered_text, filtered_key, runes, letters, d):

    #Shift through the key, generate it, decrypt the page, estimate spaces, check if the output is english and output only that
    #change the first number in range if you want to start from a different cycle

    for cycle in range(minrange, maxrange):
        my_file = Path("data_normal_key/" + str(cycle) + ".txt")
        if my_file.is_file() is True:
            pass
        else:
            cipher_key = filtered_key[cycle:]
            cipher_key = generateKey(filtered_text, cipher_key)

            decrypted_pages = []
            idx = 0
            while idx < len(filtered_text):
                decrypted_index = (runes.index(filtered_text[idx]) - runes.index(cipher_key[idx])  +29) % 29
                decrypted_pages += letters[decrypted_index]
                idx += 1

            decrypted_pages = "".join(decrypted_pages)
            decrypted_pages = infer_spaces(decrypted_pages.lower())
            newt = ""
            with open("data_normal_key/" + str(cycle) + ".txt", "w") as file:
                for word in decrypted_pages.split(" "):
                    if d.check(word) is True:
                        newt = newt + word + " "
                file.write(newt)
            print(cycle)
    print("done")

#Start threading, thanks Taiiwo

num1 = 0
num2 = len(filtered_key)
threads = 4
i = threads


for i in range(threads, 0, -1):
    minrange = round(num1 + ((num2 - num1) / threads) * (i - 1))
    maxrange = round(num1 + ((num2 - num1) / threads) * i)
    Thread(target=decoder, args=(minrange, maxrange, filtered_text, filtered_key, runes, letters, d)).start()
while True:
    time.sleep(1)

#There better be some data cause the last time I ran 16k cycles I messed up the key generation
