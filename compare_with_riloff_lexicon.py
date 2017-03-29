from tabulate import tabulate

ground_predicate_expr = {'dry', 'good', 'ready today', 'awesome', 'so much fun', 'the best feeling', 'ready', 'my favorite thing', 'funny', 'great', 'amazing', 'happy', 'so happy', 'my favorite part', 'nice', 'juicy', 'fun', 'cool', 'better', 'always fun'}
 
ground_pos_expr = {'just stops', 'cannot wait', "can't wait", 'looooove', 'please keep', 'love', 'randomly stop', 'really like', 'stops', 'loves', 'stoked', 'loving', 'enjoy', 'excited', 'appreciate', 'decided', 'goin', 'reading', 'just keeps', 'wanted', 'missed', 'cant wait', 'loveee', 'just live', 'break', 'live', 'get'} 

ground_neg_expr = {'to read', 'being treated', 'reviewing', 'babysitting', "when doesn't text", 'getting ditched', 'leaving', 'scratches', 'gettin better', 'listening', 'to randomly ask', 'going to class', 'being up late', 'hitting', 'getting up early', 'being pushed', 'spending', 'not being able', 'being stuck', 'learning', 'walking', 'being lied too', 'sleeping alone', 'being told', 'seeing people', 'looking', 'crying', 'when ignores', 'being invited', 'getting hacked', 'to be ignored', 'ruined', 'getting ignored', 'being a loner', 'falling', 'being locked', 'driving', 'taking', 'walking home', 'reading', 'coming home', 'standing', 'blamed', 'getting replaced', 'cuddling', 'getting blown', 'being up early', 'being stood', 'being awake', 'doing nothing', 'to spend', 'not sleeping', 'fixing', 'to run', 'peeing', 'not seeing', 'dropping', 'buying', 'to sit', 'forgetting', 'riding', 'taking care', 'to sit here', 'doing laundry', 'waking up not', 'sounding', 'walking to school', 'cleaning', 'to wake', 'teaching', 'being woken', 'sitting in traffic', 'having insomnia', 'getting played', 'being called names', 'coming to school', 'editing', 'being reminded', 'working', 'invited', 'spending my day', 'having bruises', 'being accused', 'getting texts', 'being taken', 'getting back', 'sending', 'shoveling', 'laying', 'being hit', 'getting no sleep', 'almost getting', 'trying', 'paying', 'sitting here', 'being called', 'replying', 'staying', 'living', 'finding', 'not feeling', 'burning', 'getting phone', 'being ditched', 'getting sick', 'calling', 'missing', 'to learn', 'wakin', 'smelling', 'failing', 'getting called', 'only getting', 'getting bad news', 'getting', 'getting my ass', 'to study', 'being home', 'getting invited', 'being ignored', 'to miss', 'posting', 'texting', 'not getting', 'spending all day', 'to clean', 'coughing', 'being used', 'getting locked', 'waiting', 'being left', 'setting', 'putting', 'arguing', 'coming back', 'hearing', 'eating', 'going there', 'to drive', 'getting bitched', 'being late', 'waking up early', 'fighting', 'sitting alone', 'to start', 'telling me', 'working all day', 'sharing', 'watching scary movies', 'burnt', 'not being invited', 'being blamed', 'to pay', 'being put', 'breaking', 'running', 'passing', 'getting screwed', 'getting woken up', 'picking', 'getting hate', 'walking to class', 'sitting', 'doing homework', 'going', 'getting punched', 'losing', 'coming', 'paying bills', 'to find out', 'receiving', 'being talked', 'checking', 'getting stared', 'practicing', 'starting', 'wasting', 'writing', 'being surrounded', 'having homework', 'getting made', 'sitting at home', 'getting home', 'gettin', 'having nothing', 'being bored', 'being yelled', 'being cussed', 'getting woken', 'to see pictures', 'traveling', 'being sick', 'dealing', 'listening to women', 'cancelled', 'feeling', 'stepping', 'closing', 'being woke', 'bring', 'being lied', 'being called fat', 'being stood up', 'getting ready', 'when falls', 'texting someone', 'seeing', 'scrolling', 'ending', 'running late', 'being grounded', 'being at work', 'not talking', 'sweating', 'hurting', 'cutting', 'having practice', 'to go back', 'going weeks', 'being able', 'finishing', 'being invited places', 'getting hit', 'getting treated', 'reading tweets', 'showing', 'taking tests', 'to get up', 'having class', 'getting lied', 'waking', 'getting yelled', 'being at school', 'studying', 'throwing', 'going to bed'}

def compare(lexicon,discards,print_discards_intersect=False,print_retrieved_intersect=False,tablefmt='html',algorithm_name='This algorithm'):


    table3 = tabulate([["","Retrieved","Retrieved","Discarded","Discarded"],
                       ["","Pos","Neg","Pos","Neg"],
                       ["Original Paper",len(ground_pos_expr),len(ground_neg_expr),"N/A","N/A"],
                       [algorithm_name,len(lexicon['pos']),len(lexicon['neg']),len(discards['pos']),len(discards['neg'])]], tablefmt=tablefmt)
              
    posdisc = ground_pos_expr & discards['pos']
    numposdisc = len(posdisc)
    negdisc = ground_neg_expr & discards['neg']
    numnegdisc = len(negdisc)
    
    poslex = ground_pos_expr & lexicon['pos']
    numposlex = len(poslex)
    neglex = ground_neg_expr & lexicon['neg']
    numneglex = len(neglex)
    
    if print_discards_intersect:
        print("Discards that were in the ground truth dataset:")
        print()
        print("Pos:\n",posdisc)
        print()
        print("Neg:\n",negdisc)
        print()
        print()
        
    if print_retrieved_intersect:
        print("Retrieved lexicon words that were in the ground truth dataset:")
        print()
        print("Pos:\n",poslex)
        print()
        print("Neg:\n",neglex)
        print()
        print()  
    
        
    table4 = tabulate([["","Ret & orig","Ret & orig","Disc & orig","Disc & orig"],
                       ["","Pos","Neg","Pos","Neg"],
                       [algorithm_name,numposlex,numneglex,numposdisc,numnegdisc]], tablefmt=tablefmt)
                       
    return table3,table4
                        
