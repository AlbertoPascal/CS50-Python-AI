import nltk
import sys
nltk.download('punkt')

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> CS | RS
AP -> Adj | Det Adj | Adj NP | Det AP | Adj AP
NP -> N | Det N | AP | N Adv 
VP -> V | V AP | V NP | VP PP
PP -> P NP | P NP PP | Det NP | Det NP PP 
CS -> RS Conj RS | RS Conj VP
RS -> NP VP | NP VP Adv


"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    
    #Since sentence is a string, we can just convert it to lowercase first:
    lower_sentence = sentence.lower()
    tokens = nltk.word_tokenize(lower_sentence)
    for word in tokens:
        if len(word) == 1 and ((ord(word) >=32 and ord(word) <= 64) or (ord(word)>=91 and ord(word) <= 96) or (ord(word)>=123 and ord(word) <=127)):
            tokens.remove(word)
    print(tokens)
    return tokens
    

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    formatted_tree = nltk.Tree.fromstring(str(tree))
    np_trees = []
    for tr in formatted_tree.subtrees():
        #print("my tree is ", tr.label())
        if tr.label() == "NP" and tr not in np_trees:
            np_trees.append(tr)
    return np_trees
    #raise NotImplementedError


if __name__ == "__main__":
    main()
