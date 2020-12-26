import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1
nltk.download('stopwords')

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_information = {}
    for tuple_value in os.walk(directory):
        root_directory = tuple_value[0]
        sub_directories = tuple_value[1]
        files = tuple_value[2]
        for file in files:
            file_information[str(file)] = None
            curr_file = open(os.path.join(root_directory, file), "r")
            file_information[str(file)] = curr_file.read()
            curr_file.close()
    
    return file_information

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    #First I translate the sentence into lowercase
    lower_sentence = document.lower()
    #I register the possible stopwords
    stopwords = nltk.corpus.stopwords.words("english")
    #I create all tokens
    tokens = nltk.word_tokenize(lower_sentence)
    #Register possible punctuation
    punctuation = string.punctuation
    #prepare to store clean words
    clean_words = []
    for word in tokens:
        #for every word in the tokens, we add it if it is not punctuation nor stopword
        if word not in punctuation and word not in stopwords:
            clean_words.append(word)
            
    return clean_words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    word_lists = documents.values()
    word_set = set()
    for list_of_words in word_lists:
        for word in list_of_words:
            word_set.add(word)
            
    idf_dictionary = {}
    
    for word in word_set:
        documents_with_word = 0
        curr_idf = 0
        for content in documents.values():
            if word in content:
                documents_with_word +=1
        if documents_with_word >0:
            curr_idf = math.log(len(documents.keys())/documents_with_word)
        idf_dictionary[word] = curr_idf
    
    return idf_dictionary
        


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    frequencies = {}
    tf_idfs = {}

    for file, content in files.items():
        tf_idfs[file] = 0
        word_list = list(content)
        word_frequency = {word:word_list.count(word) for word in word_list}
        
        #print(word_frequency)
            #word_frequency = {word:word_list.count(word) for word in word_list}
        frequencies[file] = word_frequency

    #Now that I have the term frequencies in each file, I can look for the tf-idfs. 
    for word in query:
        #I look for the tf value:
        for file in frequencies:
            if idfs.get(word):
                tf = 0
                if frequencies[file].get(word):
                    #the word appears in the document:
                    tf = frequencies[file][word]
                else:
                    tf = 0
                #each word will result in one td-idf value. These values must be summed. 
                tf_idfs[file] += tf * idfs[word]
            else:
                #means that word doesn't exist in the text. 
                continue
    #Now I sort my values in terms of the best match first:
    sorted_tf_idfs = {file:tf_idfs for file, tf_idfs in sorted(tf_idfs.items(), key=lambda x:x[1], reverse = True)}

    return list(sorted_tf_idfs.keys())[:n]
            


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    #store an array representing idf, density for each sentence. 
    sentence_ranks = {sentence:[0,0] for sentence in sentences}
    print(query)
    for sentence in sentences:
        # for each sentences, I'll go through the query words. 
        query_words_in_sentence = 0
        
        for word in query:
            if word in set(sentences[sentence]):
                query_words_in_sentence +=1
                sentence_ranks[sentence][0] +=idfs[word]
        sentence_ranks[sentence][1] += query_words_in_sentence / len(sentences[sentence])
                
        
    
    sorted_sentence_ranks = {sentence:values for sentence,values in sorted(sentence_ranks.items(), key=lambda x:(x[1][0], x[1][1]), reverse = True)}
    return list(sorted_sentence_ranks.keys())[:n]

if __name__ == "__main__":
    main()
