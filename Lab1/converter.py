import os
import json

corrected_filename = "results\\гиис3.json"
note = "123"
word = "министерство"

with open(corrected_filename, 'r', encoding='utf-8') as json_file:
    word_freq = json.load(json_file)

try:
    os.remove(corrected_filename)
    print("success")
except OSError as e: # name the Exception `e`
    print ("Failed with:", e.strerror) # look what it says
    print ("Error code:", e.code )

if word in word_freq:
    word_freq[word]['note'] = note

with open(corrected_filename, 'w', encoding='utf-8') as json_file:
    json.dump(word_freq, json_file, ensure_ascii=False)
