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

all_discards = {'pos':set(),'neg':set()}

def bootstrap(seedword,tweets):
    '''
    Input: A seed positive phrase in the form of a tuple and an iterable of tweetobjects
    Output: A set of positive sentiments and negative situations that indicate a possibly sarcastic tweet
    e.g. call: bootsrap(tuple('really','excited'), [{'tokens':['Hi','sweety'],'tags':['!','N']}]
    '''

    old_pos = set()
    pos_preds = set()
    pos_verbs = set([seedword])
    neg_phrases = set()
    epoch = 1

    while True:

        print("epoch "+str(epoch))

        old_neg = neg_phrases
        new_neg = []
        new_neg.extend(learn_new_phrases(pos_verbs,'neg',tweets))

        neg_phrases = clean_and_add(set(new_neg),neg_phrases)

        new_phrases = neg_phrases - old_neg

        if new_phrases == set():
            print("No new neg phrases found")
            break
        else:
            print("New neg phrases:")
            for tup in new_phrases:
                print('\t{}'.format(' '.join(tup)))


        old_pos = pos_verbs
        new_pos = []
        new_pos.extend(learn_new_phrases(neg_phrases,'pos',tweets))

        pos_verbs = clean_and_add(set(new_pos),pos_verbs)

        new_phrases = pos_verbs - old_pos

        if new_phrases == set():
            print("No new pos phrases found")
            break
        else:
            print("New pos phrases:")
            for tup in new_phrases:
                print('\t{}'.format(' '.join(tup)))

        epoch += 1
        print("\n")

    return {'pos':pos_verbs, 'neg':neg_phrases, 'pospred': None}

def clean_and_add(newset,oldset):

    discard_pile = set()
    combo = newset | oldset
    combo_old = combo
    combo = sort_by_len(combo)
    keys = sorted(combo.keys(),reverse=True)

    for i,k1 in enumerate(keys[:-1]):
        for big in combo[k1]:
            big = ' '.join(big)
            if is_subsumed(big,combo,keys,i):
                discard_pile.add(tuple(big.split()))

    res = combo_old - discard_pile

    return res

def is_subsumed(bigphrase,dict_of_tuples,keys,i):
    for k2 in keys[i+1:]:
        for small in dict_of_tuples[k2]:
            small = ' '.join(small)
            if small in bigphrase:
                return True
    return False

def sort_by_len(set_of_tuples):
    res = defaultdict(set)
    for tup in set_of_tuples:
        res[len(tup)].add(tup)
    return res

def learn_new_phrases(phrases,pos_or_neg,tweets):

    print('Looking for {} phrases'.format(pos_or_neg))

    candidates_sarc = defaultdict(int)
    candidates_no_sarc = defaultdict(int)
    
    for tweet in tweets:
        for seed in phrases:
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
                    
    return best_candidates(candidates_sarc,candidates_no_sarc,pos_or_neg)
    
    
def best_candidates(sarc_phrase_counts,not_sarc_phrase_counts,pos_or_neg):
    global all_discards
    prob = {}
    discards_cuz_too_few = set()
    for phrase,count in sarc_phrase_counts.items():
        if count >= 3:
            if phrase not in not_sarc_phrase_counts:
                prob[phrase] = 1.0
            else:
                prob[phrase] = count/(not_sarc_phrase_counts[phrase]+count)
        else:
            all_discards[pos_or_neg].add(' '.join(phrase))
            discards_cuz_too_few.add("{} ({})".format(' '.join(phrase),count))

    if discards_cuz_too_few:
        print("Discarded because too few:")
        for word in discards_cuz_too_few:
            print('\t'+word)

    prob = sorted(prob.items(), key=operator.itemgetter(1), reverse=True)
    res = [x[0] for x in prob[:20] if x[1]>=0.8]

    if prob[len(res):]:
        print("Discarded because not probable enough:")
        for phrase,p in prob[len(res):]:
            print('\t{} ({})'.format(' '.join(phrase),round(p,4)))
            all_discards[pos_or_neg].add(' '.join(phrase))

    return set(res)
    
        
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
    
TODO: This could certainly use more attention
'''
def has_POS_trigram_pattern(tokens,tags):
    third_tag_candidates = set(['N','O','^','S','Z','A','V','R','T','P'])
    if tokens[0] == 'to' and tags[1] == 'V' and tags[2] in third_tag_candidates:
        return True
    if tags[0] == 'V' and tags[1] == 'V' and tags[2] in third_tag_candidates:
        return True
    
def pos_phrase_with_desired_syntactic_structure(phrase):
    # The inverted order should take care of subsumption
    
    if len(phrase['tokens']) == 2 and not  set(phrase['tags'][:2]) - set(['V','R']):
        return [tuple(phrase['tokens'][:2])]

    if len(phrase['tokens']) >= 1 and phrase['tags'][0] == 'V':
        return [tuple(phrase['tokens'][:1])]

    return []

#TODO: This could use a 4-gram pattern for better accuracy
def neg_phrase_with_desired_syntactic_structure(phrase):
    # Corrects the order of subsumption
    
    if len(phrase['tokens']) >= 1 and phrase['tags'][0] == 'V':
        return [tuple(phrase['tokens'][:1])]
    
    if len(phrase['tokens']) >= 2 and has_POS_bigram_pattern(phrase['tokens'][:2],phrase['tags'][:2]):
        return [tuple(phrase['tokens'][:2])]

    if len(phrase['tokens']) == 3 and has_POS_trigram_pattern(phrase['tokens'],phrase['tags']):
        return [tuple(phrase['tokens'][:3])]

    return []
    
    
def get_possibly_neg_phrase(pos_phrase,tweetobj):
    '''
    In: a positive sentiment word or phrase and a tweet object
    Out: 1,2,3-grams of words on the right of the given phrase
    '''
    out = []
    tokens = tweetobj['tokens']
    postags = tweetobj['tags']
    l = len(pos_phrase)
    for i,token in enumerate(tokens):
        if tuple(tokens[i:i+l]) == pos_phrase:
            subout = {'tokens':[],'tags':[]}
            j = 0
            while j + i + l < len(tokens) and j < 3:
                subout['tokens'].append(tokens[i+l+j])
                subout['tags'].append(postags[i+l+j])
                j += 1
            out.append(subout)
    return out
    
    
def get_possibly_pos_phrase(neg_phrase,tweetobj):
    '''
    In: a negative sentiment word or phrase as a tuple and a tweet object
    Out: 1,2-grams of words on the left of the given phrase
    '''
    out = []
    tokens = tweetobj['tokens']
    postags = tweetobj['tags']
    l = len(neg_phrase)
    for i,token in enumerate(tokens):
        if tuple(tokens[i:i+l]) == neg_phrase:
            subout = {'tokens':[],'tags':[]}
            j = 1
            while i-j >=0 and j <= 2:
                subout['tokens'].insert(0,tokens[i-j])
                subout['tags'].insert(0,postags[i-j])
                j += 1
            out.append(subout)
    return out


# In[6]:
if __name__ == '__main__':
    import sys
    dataset = sys.argv[1]
    if dataset == 'riloff':
        alltweets = pickle.load(open('riloff-tokenized-and-tagged-lowercase.pkl','rb'))
    elif dataset == 'shereen':
        alltweets = pickle.load(open('shereen-sarc-tokenized-and-tagged-lowercase.pkl','rb'))
    elif dataset == 'scraped':
        alltweets = pickle.load(open('scraped-tokenized-and-tagged-lowercase.pkl','rb'))

    print(len(alltweets),'sarc tweets')
    alltweets.extend(pickle.load(open('shereen-not_sarc-tokenized-and-tagged-0-lowercase.pkl','rb')))
    print(len(alltweets),'total tweets')

    results = bootstrap(tuple(['love']),alltweets)

    print('\n\n\n')

    print("Final list of all discards:\n",all_discards)
    print()
    print("Final list of POSITIVE phrases:")
    for tup in results['pos']:
        print('\t{}'.format(' '.join(tup)))
    print()
    print("Final list of NEGATIVE phrases:")
    for tup in results['neg']:
        print('\t{}'.format(' '.join(tup)))
    print()

    ground_predicate_expr = set(["great", "so much fun", "good", "so happy", "better", "my favorite thing", "cool", "funny", "nice", "always fun", "fun", "awesome", "the best feeling", "amazing", "happy", "ready today", "ready", "dry", "juicy", "my favorite part"])
    ground_pos_expr = set(["love", "missed", "loves", "enjoy", "cant wait", "excited", "wanted", "can't wait", "get", "appreciate", "decided", "loving", "really like", "looooove", "just keeps", "loveee", "randomly stop", "cannot wait", "just live", "please keep", "live", "stoked", "goin", "reading", "break", "just stops", "stops"])
    ground_neg_expr = set(["being ignored", "being sick", "waiting", "feeling", "waking up early", "being woken", "fighting", "staying", "writing", "being home", "cleaning", "not getting", "crying", "sitting at home", "being stuck", "starting", "being told", "being left", "getting ignored", "being treated", "doing homework", "learning", "getting up early", "going to bed", "getting sick", "riding", "being ditched", "getting ditched", "missing", "not sleeping", "not talking", "trying", "falling", "walking home", "getting yelled", "being awake", "being talked", "taking care", "doing nothing", "wasting", "throwing", "getting woken up", "to spend", "standing", "smelling", "getting woken", "arguing", "paying bills", "being locked", "shoveling", "getting called", "being at work", "having nothing", "getting invited", "getting blown", "dealing", "ending", "to wake", "when doesn't text", "getting ready", "to learn", "picking", "walking to class", "breaking", "being invited", "getting home", "setting", "dropping", "not seeing", "forgetting", "being called fat", "getting lied", "invited", "to sit here", "to be ignored", "being late", "doing laundry", "being taken", "practicing", "babysitting", "getting hit", "being used", "being used", "being reminded", "when falls", "working all day", "running late", "traveling", "peeing", "being hit", "having practice", "not being invited", "being bored", "stepping", "spending my day", "leaving", "almost getting", "being put", "passing", "being at school", "to study", "going to class", "coughing", "sitting in traffic", "being yelled", "fixing", "burning", "walking to school", "wakin", "seeing people", "being accused", "being up early", "scratches", "texting someone", "being invited places", "receiving", "being grounded", "checking", "getting my ass", "getting back", "getting bitched", "getting treated", "only getting", "reviewing", "sitting alone", "getting screwed", "going there", "getting stared", "calling", "watching scary movies", "getting no sleep", "taking tests", "getting locked", "reading tweets", "teaching", "waking up not", "sounding", "getting made", "sleeping alone", "not feeling", "being surrounded", "editing", "being stood up", "to randomly ask", "getting hacked", "getting texts", "having insomnia", "having homework", "blamed", "showing", "being blamed", "getting bad news", "getting played", "being stood", "scrolling", "being lied too", "being a loner", "going weeks", "being up late", "having class", "failing", "being cussed", "listening to women", "when ignores", "cutting", "bring", "burnt", "getting hate", "coming to school", "sitting here", "waking up early", "being called names", "getting replaced", "having bruises", "closing", "coming back", "getting punched", "getting phone", "spending all day", "being pushed", "spending", "not being able", "waking", "working", "sitting", "walking", "coming home", "living", "being lied", "getting", "coming", "going", "running", "to sit", "being called", "to read", "studying", "paying", "texting", "hearing", "replying", "gettin better", "gettin better", "gettin", "eating", "losing", "listening", "to get up", "finding", "to clean", "being able", "seeing", "to run", "to drive", "to go back", "looking", "taking", "putting", "driving", "to start", "posting", "to pay", "telling me", "ruined", "being woke", "hitting", "laying", "cuddling", "reading", "buying", "cancelled", "sending", "to see pictures", "to find out", "sharing", "finishing", "sweating", "to miss", "hurting"])

    print()
    print()
    print("Discards that were in the ground truth dataset")
    print("pos")
    print(ground_pos_expr & all_discards['pos'])
    print("neg")
    print(ground_neg_expr & all_discards['neg'])
    #print("pospred")
    #print(ground_predicate_expr & all_discards['pos'])
    print()
