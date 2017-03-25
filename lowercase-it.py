# coding: utf-8
import pickle
scraped = pickle.load(open('scraped-tokenized-and-tagged.pkl','rb'))
for tweet in scraped:
    tweet['tokens'] = [token.lower() for token in tweet['tokens'] ]
    
pickle.dump(scraped,open('scraped-tokenized-and-tagged-lowercase.pkl','wb'))
