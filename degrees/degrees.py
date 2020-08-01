#Solution Code to CS50 Ai course Degree's problem by Alberto Pascal Garza
#albertopascalgarza@gmail.com

import csv
import sys
import copy

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        #print("my path is: ", path) #remove
        for i in range(degrees):
            #print(i) #remove
            person1 = people[path[i][1]]["name"]
            #print(person1) #remove
            person2 = people[path[i + 1][1]]["name"]
            #print(person2) #remove
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    #I will declare my source as my start node on my frontier. 
    frontier = QueueFrontier()
    #setup my starting node:
    initial_node = Node(source, None, neighbors_for_person(source))
    #append my initial node:
    frontier.add(initial_node)
    found_solution = False
    explored_nodes = {}
    explored_states = {}
    states_in_frontier = {}
    i = 0
    #Start iterating to determine the path:
    while(not frontier.empty()):
               
        #This conuter is used in my print to keep track of the attempts
        i= i+1
        
        #I extract one node:
        current_node = frontier.remove()
        #I will only explore the actions if I have not visited this node before:
        explored_states[current_node.state] = "explored" #append(current_node.state)
        explored_nodes[current_node] = "explored"
        #I check if my current node is my solution:
        if (current_node.state == target):
            print("I have explored: ", len(explored_states), " states")
            print("Found my solution")
            found_solution = True
            break
        
        else:
            #Check if neighbor is in frontier.
            neighbor_list = neighbors_for_person(current_node.state)
            
            for neighbor in neighbor_list:
                #I setup my new node
                new_state = neighbor[1]
                new_parent = current_node
                action_taken = neighbor[0]
                new_node = Node(new_state, new_parent, action_taken)
                #I check if this neighbor is actually my target. If it is, I can skip some frontier iterations:
                
                if (new_node.state == target):
                    print("Found solution in a neighbor! Skipping unnecesary searches")
                    frontier = QueueFrontier()
                    frontier.add(new_node)
                    states_in_frontier = {}
                    states_in_frontier [new_node.state] = "seen"
                    break;            
                
                #else, I add my new node to the frontier if it is not there already.
                #Adittional note: I do not use the class method because on deep seaches it slows way too much the execution. Dictionaries have linear search time.
                elif((not states_in_frontier.get(new_node.state)) and new_node.state != current_node.state and (not explored_states.get(new_node.state)) and (not explored_nodes.get(new_node))):
                    frontier.add(new_node)
                    states_in_frontier [new_node.state] = "seen"
        if(i%10000 == 0):
             print("I have explored: ", len(explored_states))
    path = []
    if (found_solution):
        #I need to iterate backwards from my last explored node's parents. 
        Solution_node = current_node
        while(Solution_node.parent is not None):
            path.append((Solution_node.action, Solution_node.state))
            Solution_node = Solution_node.parent
           
        path.reverse()
        #print(path)
      
        return path
    
    else:
        #If we reach this point it means there is no available solution
        print("I could not find a solution")
        return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
