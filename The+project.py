
# coding: utf-8

# In[14]:

import glob
from collections import defaultdict
from pprint import pprint
import pickle
import operator


# In[2]:

# First I reproduce Riloff et al.'s bootstrapping experiments exactly.
# The gist of it is: 
#    - Sarcasm in a sentence can be modeled as 
#         the presence of a positive sentiment followed by a negative situation.
#    - Self-labeled sarcastic tweets, marked #sarcasm or #sarcastic 
#         were used in a bootstrapping process
#         to automatically discover positive and negative phrases.
# I start with 
# a) reproducing this bootstrappping method exactly
# b) using other markers of sarcasm such as #yeahright, #not 
#        to discover the positive and negative phrases
# Possible next step:
#     Is the bootstrapping method invariant to initialization?
#         It should be if it is robust. Try with a different initial word than love.


# In[4]:

# "positive sentiments that are expressed as a 
#    verb phrase or as a predicative expression 
#    (predicate adjective or predicate nominal),
#    and negative activities or states that can be a
#    complement to a verb phrase."

# "we try to recognize these syntactic structures heuristically using
#     only part-of-speech tags and proximity"


# In[11]:

def bootstrap(seedword,tweets):
    '''
    Input: A seed positive word and a set of tweets
    Output: A set of positive sentiments and negative situations that indicate a possibly sarcastic tweet

    negphrases_count1 = 0
    posphrases_count1 = 1
    
    new_neg_phrases = learn_new_negative_phrases(seedword,tweets)
    neg_phrases_count2 = len(new_neg_phrases) + neg_phrases_count1
    
    while neg_phrases_count1 != neg_phrases_count2 and pos_phrases_count1
    
    new_pos_phrases = []
    for neg_phrase in new_neg_phrases:
        new_pos_phrases.extend(learn_new_positive_phrases(neg_phrase,tweets))
        
    for pos_phrase in new_pos_phrases
    pprint(neg_best_candidates)
    '''    
    pprint(learn_new_phrases(seedword,'neg',tweets))
    
    
def learn_new_phrases(seed,pos_or_neg,tweets):
    candidates_sarc = defaultdict(int)
    candidates_no_sarc = defaultdict(int)
    
    for tweet in tweets:
        if pos_or_neg == 'pos':
            candidate_phrases = get_possibly_pos_phrase(seed,tweet)
        elif pos_or_neg == 'neg':
            candidate_phrases = get_possibly_neg_phrase(seed,tweet)
        
        for phrase in candidate_phrases:
            if pos_or_neg == 'pos':
                res = pos_phrase_with_desired_syntactic_structure(phrase)
            elif pos_or_neg == 'neg':
                res = neg_phrase_with_desired_syntactic_structure(phrase)
            
            for p in res:
                if tweet['label'] == 'SARCASM':
                    candidates_sarc[p] += 1
                elif tweet['label'] == 'NOT_SARCASM':
                    candidates_no_sarc[p] += 1
                    
    return best_candidates(candidates_sarc,candidates_no_sarc)
    
'''
def learn_new_positive_phrases(negative_phrase,tweets):
    candidate_pos_phrase_sarcasm = defaultdict(int)
    candidate_pos_phrase_not_sarcasm = defaultdict(int)
    
    for tweet in tweets:
        pos_phrase_n_grams = get_possibly_pos_phrase(negative_phrase,tweet)
        for pos_phrase in neg_phrase_n_grams:
            res = neg_phrase_with_desired_syntactic_structure(neg_phrase)
            for p in res:
                if tweet['label'] == 'SARCASM':
                    candidate_neg_phrase_sarcasm[p] += 1
                elif tweet['label'] == 'NOT_SARCASM':
                    candidate_neg_phrase_not_sarcasm[p] += 1
    
    #pprint(candidate_neg_phrase_sarcasm)
    #pprint(candidate_neg_phrase_not_sarcasm)
    
    return best_candidates(candidate_pos_phrase_sarcasm,candidate_pos_phrase_not_sarcasm)
    
    
def learn_new_negative_phrases(positive_phrase,tweets):
    #"The learning process relies on an assumption that
    #    a positive sentiment verb phrase usually appears to
    #    the left of a negative situation phrase and in close
    #    proximity (usually, but not always, adjacent)."
    candidate_neg_phrase_sarcasm = defaultdict(int)
    candidate_neg_phrase_not_sarcasm = defaultdict(int)
    
    for tweet in tweets:
        neg_phrase_n_grams = get_possibly_neg_phrase(positive_word,tweet)
        for neg_phrase in neg_phrase_n_grams:
            res = neg_phrase_with_desired_syntactic_structure(neg_phrase)
            for p in res:
                if tweet['label'] == 'SARCASM':
                    candidate_neg_phrase_sarcasm[p] += 1
                elif tweet['label'] == 'NOT_SARCASM':
                    candidate_neg_phrase_not_sarcasm[p] += 1
    
    #pprint(candidate_neg_phrase_sarcasm)
    #pprint(candidate_neg_phrase_not_sarcasm)
    
    return best_candidates(candidate_neg_phrase_sarcasm,candidate_neg_phrase_not_sarcasm)
'''
    
def best_candidates(sarc_phrase_counts,not_sarc_phrase_counts):
    prob = {}
    for phrase,count in sarc_phrase_counts.items():
        if count >= 3:
            if phrase not in not_sarc_phrase_counts:
                #TODO: Is this the right thing to do
                #  or can there be more nuance?
                prob[phrase] = 1
            else:
                prob[phrase] = count/not_sarc_phrase_counts[phrase]
        else:
            print("Discarded cuz too few ({})".format(count),phrase)
    prob = sorted(prob.items(), key=operator.itemgetter(1), reverse=True)
    res = [x[0] for x in prob[:20] if x[1]>=0.8]
    print("Discarded cuz not probable enough:",prob[len(res):])
    return res
    
        
#The 7 POS bigram patterns are:
#  V+V, V+ADV, ADV+V, “to”+V,
#  V+NOUN, V+PRO, V+ADJ
def has_POS_bigram_pattern(tokens,tags):
    if tokens[0] == 'to' and tags[1] == 'V':
        return True
    if tags[0] == 'R' and tags[1] in ['V','T']:
        return True
    if tags[0] in ['V','T'] and tags[1] in ['N','O','^','S','Z','A','V','R','T']:
        return True

'''
The 20 POS trigram patterns are designed to capture 
    seven general types of verb phrases: 
        #verb and adverb mixtures,
        #an infinitive VP that includes an adverb, 
        a verb phrase followed by a noun phrase, 
        a verb phrase followed by a prepositional phrase,
        a verb followed by an adjective phrase, 
        #or an infinitive VP followed by an adjective, noun, or pronoun.
        
Made my own thing up with this as a guide:
    http://examples.yourdictionary.com/verb-phrase-examples.html
    
TODO: This certainly needs more attention
'''
def has_POS_trigram_pattern(tokens,tags):
    third_tag_candidates = set(['N','O','^','S','Z','A','V','R','T','P'])
    if tokens[0] == 'to' and tags[1] == 'V' and tags[2] in third_tag_candidates:
        return True
    if tags[0] == 'V' and tags[1] == 'V' and tags[2] in third_tag_candidates:
        return True
    

#TODO: This could use a 4-gram pattern for better accuracy
def neg_phrase_with_desired_syntactic_structure(phrase):
    # The inverted order should take care of subsumption
    
    if len(phrase['tokens']) == 3 and has_POS_trigram_pattern(phrase['tokens'],phrase['tags']):
        return [' '.join(phrase['tokens'])]
    
    if len(phrase['tokens']) >= 2 and has_POS_bigram_pattern(phrase['tokens'][:2],phrase['tags'][:2]):
        return [' '.join(phrase['tokens'][:2])]

    if len(phrase['tokens']) >= 1 and phrase['tags'][0] == 'V':
        return [phrase['tokens'][0]]

    return []
    
    
def get_possibly_neg_phrase(pos_phrase,tweetobj):
    '''
    In: a positive sentiment word or phrase and a tweet object
    Out: 1,2,3-grams of words on the right of the given phrase
    '''
    out = []
    tokens = tweetobj['tokens']
    postags = tweetobj['tags']
    for i,token in enumerate(tokens):
        if token == pos_phrase:
            subout = {'tokens':[],'tags':[]}
            j = 1
            while j + i < len(tokens) and j <= 3:
                subout['tokens'].append(tokens[i+j])
                subout['tags'].append(postags[i+j])
                j += 1
            out.append(subout)
    return out


# In[12]:

###Discard pile
"""def neg_phrase_with_desired_syntactic_structure(phrase):
    res = []
    #for n in range(len(phrase['tokens'])):
    #if n == 1:
    print(phrase)
    if phrase['tags'][0] == 'V':
        res.append(phrase['tokens'][0])
    #elif n == 2:
    if has_POS_bigram_pattern(phrase['tokens'][:2],phrase['tags'][:2]):
        res.append(' '.join(phrase['tokens'][:2]))
    #elif n == 3:
    if has_POS_trigram_pattern(phrase['tokens'],phrase['tags']):
        res.append(' '.join(phrase['tokens']))
    #else:
    #    print('Oops, fell through sieve')
    return res"""
###Guard
print()


# In[15]:

def test_get_possibly_neg_phrase():
    for tweet in original_tweets:
        if tweet['label'] == 'SARCASM':
            res = get_possibly_neg_phrase('love',tweet)
            if res:
                print(res)

#test_get_possibly_neg_phrase()

bootstrap('love',original_riloff_tweets)


# In[149]:

original_riloff_tweets = []
with open('sarcasm-annos-emnlp13-tweets.tsv') as f:
    for line in f:
        try:
            tweetid,label,tweet = line.strip().split('\t')
            original_riloff_tweets.append({'id':int(tweetid),'label':label,'tweet':tweet})
        except ValueError:
            print(line)
            
original_riloff_tweets.append({'appeasing_dummy':None})
            
i = 0
original_riloff_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
with open('riloff-tweets.tagged') as f:
    for line in f:
        if line.strip() == '':
            i += 1
            original_riloff_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
        else:
            word,tag,conf = line.strip().split()
            original_riloff_tweets[i]['tokens'].append(word)
            original_riloff_tweets[i]['tags'].append(tag)
            original_riloff_tweets[i]['conf'].append(conf)


# In[6]:

original_riloff_tweets = pickle.load(open('data/march22/riloff-tokenized-and-tagged.pkl','rb'))


# In[158]:

mv riloff-tokenized-and-tagged.pkl ril data/march22/


# In[174]:

ls -lrt data/


# In[175]:

processed_tweets = pickle.load(open('data/processed-tweets.pkl','rb'))


# In[182]:

ls data/shereen/


# In[196]:

seenalready = set()
with open('data/march22/shereen-sarc.orig','w') as fw:
    for filename in glob.iglob('data/shereen/sarcasm-more-week*.tweet'):
        #print(filename)
        with open(filename) as f:
            for line in f:
                if line not in seenalready:
                    fw.write(line)
                    seenalready.add(line)
                    #They're all unique, turns out.
                    #And there's 75680 of them.
    with open('data/shereen/sarcasm.tweet') as f:
        for line in f:
            if line not in seenalready:
                fw.write(line)
                seenalready.add(line)
                #There might be one here that is a repeat, considering the entire set


# In[197]:

len(seenalready)


# In[199]:

get_ipython().system('wc -l data/march22/shereen-sarc.orig')


# In[215]:

seenalready = set()
repeat_count = 0
with open('data/march22/shereen-not_sarc.orig','w') as fw:
    for filename in glob.iglob('data/shereen/random-*not-sarc*.pkl'):
        with open(filename,'rb') as f:
            for line in pickle.load(f):
                if line not in seenalready:
                    fw.write(line+'\n')
                    seenalready.add(line)
                else:
                    repeat_count += 1
    for filename in glob.iglob('data/shereen/random*.tweet'):
        with open(filename) as f:
            for line in f:
                if line not in seenalready:
                    fw.write(line)
                    seenalready.add(line)
                else:
                    repeat_count += 1

print(repeat_count)
print(len(seenalready))
get_ipython().system('wc -l data/march22/shereen-not_sarc.orig')
# This one has plenty repeats, but nearly 2m non-repeating tweets nontheless.


# In[16]:

original_shereen_sarc_tweets = []
with open('data/march22/shereen-sarc.orig') as f:
    for line in f:
        try:
            tweet = line.strip()
            original_shereen_sarc_tweets.append({'label':'SARCASM','tweet':tweet})
        except ValueError:
            print(line)
            
original_shereen_sarc_tweets.append({'appeasing_dummy':None})
            
i = 0
original_shereen_sarc_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
with open('data/march22/shereen-sarc.tagged') as f:
    for line in f:
        if line.strip() == '':
            i += 1
            original_shereen_sarc_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
        else:
            word,tag,conf = line.strip().split()
            try:
                original_shereen_sarc_tweets[i]['tokens'].append(word)
                original_shereen_sarc_tweets[i]['tags'].append(tag)
                original_shereen_sarc_tweets[i]['conf'].append(conf)
            except KeyError:
                print(line)


# In[17]:

original_shereen_not_sarc_tweets = []
with open('data/march22/shereen-not_sarc.cleaned.orig') as f:
    for line in f:
        try:
            tweet = line.strip()
            original_shereen_not_sarc_tweets.append({'label':'NOT_SARCASM','tweet':tweet})
        except ValueError:
            print(line)
            
original_shereen_not_sarc_tweets.append({'appeasing_dummy':None})
            
i = 0
original_shereen_not_sarc_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
with open('data/march22/shereen-not_sarc.cleaned.tagged') as f:
    for line in f:
        if line.strip() == '':
            i += 1
            original_shereen_not_sarc_tweets[i].update({'tokens':[],'tags':[],'conf':[]})
        else:
            word,tag,conf = line.strip().split()
            original_shereen_not_sarc_tweets[i]['tokens'].append(word)
            original_shereen_not_sarc_tweets[i]['tags'].append(tag)
            original_shereen_not_sarc_tweets[i]['conf'].append(conf)


# In[18]:

original_shereen_not_sarc_tweets[0]


# In[19]:

original_shereen_sarc_tweets[0]


# In[21]:

pickle.dump(original_shereen_not_sarc_tweets+original_shereen_sarc_tweets,open('data/march22/shereen-tokenized-and-tagged.pkl','wb'))


# In[22]:

ls -lrth data/march22/


# In[ ]:



