def lowercase_all_tokens_and_tweets(tweetobjlist):
    for tweet in tweetobjlist:
        tweet['tokens'] = [token.lower() for token in tweet['tokens']] 
        tweet['text'] = tweet['text'].lower()

# TODO: Potential pitfall:
#       Not all hashtags are tagged as hashtags. #not especially could escape as a word, 
#           if the tagger deems it to be one
'''
 Hashtags and at-mentions can also serve as words
or phrases within a tweet; e.g. Is #qadaffi going down?
When used in this way, we tag hashtags with their
appropriate part of speech, i.e., as if they did not start
with #
- Part-of-Speech Tagging for Twitter: Annotation, Features, and Experiments. Kevin Gimpel et al., ACL '11.
'''
def lowercase_tokens_and_remove_hashtags(tweetobjlist, hashtags_to_remove):
    hashtags_to_remove = [hashtag.lower() for hashtag in hashtags_to_remove]
    lowercase_all_tokens_and_tweets(tweetobjlist)
    for tweet in tweetobjlist:
        for i,tag in enumerate(tweet['tags']):
            if tag == '#' and tweet['tokens'][i] in hashtags_to_remove:
                tweet['text'] = tweet['text'].replace(tweet['tokens'][i],'')
                tweet['tokens'].pop(i)
                tweet['tags'].pop(i)
                tweet['conf'].pop(i)
