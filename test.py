from math import log

# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
words = open("words.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

runes = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚩ', 'ᚱ', 'ᚳ', 'ᚷ', 'ᚹ', 'ᚻ', 'ᚾ', 'ᛁ', 'ᛄ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛋ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛝ', 'ᛟ', 'ᛞ', 'ᚪ', 'ᚫ', 'ᚣ', 'ᛡ', 'ᛠ']
letters = ['F', 'U', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X', 'S', 'T', 'B', 'E', 'M', 'L', 'ING', 'OE', 'D', 'A', 'AE', 'Y', 'IO', 'EA']

def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))
cipher = "ᛖᛠᚢᚣᚦᛈᚦᚳᚦᚳᚦᚳᚢᚳᚫᚫᛚᛗᚪᚣᛝ"
key = "ᛏᛖᛋᛏ"

def generateKey(filtered_text, filtered_key):
    times=len(filtered_text)//len(filtered_key)+1
    key = (times*filtered_key)[:len(filtered_text)]
    return key

def decoder(cipher, key):

    #Shift through the key, generate it, decrypt the page, estimate spaces, check if the output is english and output only that
    #change the first number in range if you want to start from a different cycle


        cipher_key = generateKey(cipher, key)
        decrypted_pages = []
        idx = 0
        while idx < len(cipher):
            decrypted_index = (runes.index(cipher[idx]) - runes.index(cipher_key[idx])  +29) % 29
            decrypted_pages += letters[decrypted_index]
            idx += 1

        decrypted_pages = "".join(decrypted_pages)
        decrypted_pages = infer_spaces(decrypted_pages.lower())
        print(decrypted_pages)
decoder(cipher, key)
print("done")
