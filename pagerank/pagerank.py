#Alberto Pascal
#CS50: Python AI Page Rank Algorithm.
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #define my probabilities dictionary
    probabilities = {}
    
    #links that I can go to with a damping_factor probability. 
    page_links = corpus[page]

    #pages that I could go to with a 1-damping_factor probability
    available_links = []
    for page in corpus:
        available_links.append(page)
        #initialize my dictionary
        probabilities[page] = 0
    #Fill in the transition model for whenever I visit a link within my page
    for link in page_links:
        probabilities[link] = (damping_factor) * (1/len(page_links))
    
    for link in available_links:
        probabilities[link] = probabilities[link] + ((1-damping_factor) * (1/len(available_links)))
    #print(probabilities)
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #get my list of pages
    pages = list(corpus.keys())
    #Prepare the dictionary containing the sample probabilities
    created_pages = {}
    #Generate a random first page from those available
    first_page = random.choice(pages)
    #for each page, set a starting probability of 0
    for page in pages:
        created_pages[page] = 0
    #Update the probability of the first page I have drawn to 1/n because it is 1 appearance out of n samples
    created_pages[first_page] = 1/n
    #calculate the probabilities of going to other pages based on current page
    current_probabilities = transition_model(corpus, first_page, damping_factor)
    #sample over n-1 probabilities because I already had the first sample above    
    for i in range(0,n-1):
        #get a random new page based on the probabilities I had
        new_page = random.choices(list(current_probabilities.keys()), list(current_probabilities.values()), k=1)
        #add this page's appearance probability over my whole sample to the count
        created_pages[new_page[0]] = created_pages[new_page[0]] + 1/n
        #calculate the new probabilities
        current_probabilities = transition_model(corpus,new_page[0],damping_factor)

    return created_pages

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    iteration_page_rank = {}
    pages = list(corpus.keys())
    #Define the starting page ranks for each page. 
    for page in pages:
        iteration_page_rank[page] = (1/len(corpus.keys()))
    #prepare a flag to see when my values start to converge
    finished_iterating = False
    #I will now calculate iteratively my page rank values until I have a difference lower than 0.001 when compared to the previous iteration
    while not finished_iterating:
        previous_page_rank_values = iteration_page_rank.copy()
        #assume I will finish in this iteration
        finished_iterating = True
        for page in pages:
            #for each page, I calculate the new iteration_page_rank value calling the function
            iteration_page_rank[page] = ((1-damping_factor)/len(corpus.keys())) + (damping_factor * sum_of_ranks(previous_page_rank_values, page, corpus))
            if not abs(iteration_page_rank[page] - previous_page_rank_values[page])< 0.001:
                #I need to keep iterating
                finished_iterating = False
    return iteration_page_rank

def sum_of_ranks(prev_values, current_page, corpus):
    """
    This function calculates the sumation part of the page rank formula. 
    """ 
    prev_value_pages = prev_values.keys()
    sum_of_values = 0
   
    for page in prev_value_pages:
        if current_page in corpus[page]:
            sum_of_values += prev_values[page]/len(corpus[page])
        else:
            continue
    return sum_of_values
        
if __name__ == "__main__":
    main()
