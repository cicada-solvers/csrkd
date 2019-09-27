import enchant, sys, time, math
from math import log
from threading import Thread
from pathlib import Path
from pybar import *

#Running key shift decoder for Cicada 3301

#Read in the dictionary for english check in the end
d = enchant.Dict("en_US")

#Choose key mode (0 = normal key, 1 = reversed key)
reverse_mode = input("Choose the key mode (0 = normal key, 1 = reversed key): ")

#Number of threads to use
threads = int(input("Number of threads to use: "))

#Runes and corresponding letters
runes = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚩ', 'ᚱ', 'ᚳ', 'ᚷ', 'ᚹ', 'ᚻ', 'ᚾ', 'ᛁ', 'ᛄ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛋ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚪ', 'ᚫ', 'ᚣ', 'ᛡ', 'ᛠ']
letters = ['F', 'U', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X', 'S', 'T', 'B', 'E', 'M', 'L', 'ING', 'OE', 'D', 'A', 'AE', 'Y', 'IO', 'EA']

#LP text in runes
cipher = open('cipher_text.txt', encoding='utf-8').read()

#Red Book LP, thanks mortlach
key = open('cipher_key.txt', encoding='utf-8').read()

#Space estimation stuff
words = open("words.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

#Reverse key if reverse_mode is enabled
if reverse_mode == "1":
    key = "".join(reversed(key))
else:
    pass

#Filter the LP (no spaces, only runes)
filtered_cipher = []
for char in cipher:
    if char in runes:
        filtered_cipher += char

#Filter the key (Red Book LP, no spaces, only runes, using mortlach's rune version)
filtered_key = []
for char in key:
    if char in runes:
        filtered_key += char

#Generate key function
def generateKey(filtered_cipher, filtered_key):
    times=len(filtered_cipher)//len(filtered_key)+1
    cipher_key = (times*filtered_key)[:len(filtered_cipher)]
    return cipher_key

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

def decoder(minrange, maxrange, filtered_cipher, filtered_key, runes, letters, d, reverse_mode, tracker):

    #Shift through the key, generate it, decrypt the page, estimate spaces, check if the output is english and output only that
    #change the first number in range if you want to start from a different cycle

    #Set data path
    if reverse_mode == "1":
        data_path = "data_reverse_key/"
    else:
        data_path = "data_normal_key/"

    #Main loop for decoding
    for cycle in range(minrange, maxrange):
        my_file = Path(str(data_path) + str(cycle) + ".txt")

        #Check if an output file already exists, if it does, skip it and progress the bar, otherwise decode
        if my_file.is_file() is True:
            tracker.next()
        else:
            #Generate cipher key
            cipher_key = generateKey(filtered_cipher, filtered_key[cycle:])

            #Decoding
            decrypted_pages = []
            idx = 0
            while idx < len(filtered_cipher):
                decrypted_index = (runes.index(filtered_cipher[idx]) - runes.index(cipher_key[idx])  +29) % 29
                decrypted_pages += letters[decrypted_index]
                idx += 1

            #Try to estimate where spaces should be, add them, do a dictionary check, save the output and progress the bar
            decrypted_pages = "".join(decrypted_pages)
            decrypted_pages = infer_spaces(decrypted_pages.lower())
            newt = ""
            with open(str(data_path) + str(cycle) + ".txt", "w") as file:
                for word in decrypted_pages.split(" "):
                    if d.check(word) is True:
                        newt = newt + word + " "
                file.write(newt)
                tracker.next()
    bar.done("Finished!")


#Start threading and progress bars
#Threading stuff
num1 = 0
num2 = len(filtered_key)
i = threads

#Progress bar stuff
barlength = len(filtered_key)//threads
bar = PyBar(max = 1, poll=0)
trackers = []

#Calculate range for thread and make a tracker for that thread
for i in range(threads, 0, -1):
    minrange = num1 + ((num2 - num1) // threads) * (i - 1)
    maxrange = num1 + ((num2 - num1) // threads) * i
    tracker = Tracker(max = maxrange - minrange)
    trackers.append(tracker)
    Thread(target=decoder, args=(minrange, maxrange, filtered_cipher, filtered_key, runes, letters, d, reverse_mode, tracker)).start()

#Add all the stuff bar.update() has to update
bar_items = []
for i in range(threads):
    tracker = trackers[i]
    bar_items.append(bar.bar(tracker=tracker))
    bar_items.append(bar.percent(tracker=tracker))
    bar_items.append(bar.eta(tracker=tracker))

#Update the bars
while True:
    time.sleep(1)
    bar.update(*bar_items)


#There better be some data cause the last time I ran 16k cycles I messed up the key generation
#Special thanks to mortlach and Taiwoo
