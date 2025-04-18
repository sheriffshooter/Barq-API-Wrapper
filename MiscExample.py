import torch
import numpy as np
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import json

# the ai stuff in this file is ai generated. I dont usually like ai but this scope of this project was to do something fun. it ended up turning into too big of a project
# Load BERT-Large model and tokenizer
model_name = "bert-large-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

with open("allBios.json", "r", encoding="utf-8") as file:
    users = json.load(file)

idealBio = "Hi. I’m a furry who likes spending time 'outside', engaging in meaningful conversations, and hanging out with friends. I’m also a big fan of the outdoors and enjoy exploring nature."

def get_sentence_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

ideal_embedding = get_sentence_embedding(idealBio)

done = 0
for user in users:
    bio = user[2]
    bio_embedding = get_sentence_embedding(bio)
    similarity_score = cosine_similarity(ideal_embedding, bio_embedding)[0][0]
    
    if len(user) == 5:
        user[4] = str(similarity_score)
    else:
        user.append(str(similarity_score))#(int(((similarity_score + 1) / 2) * 1000))
    done = done + 1
    if done >= 25: break

with open("allBios.json", "w", encoding="utf-8") as file:
    json.dump(users, file, indent=4)
