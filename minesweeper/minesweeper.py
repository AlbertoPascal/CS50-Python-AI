#Alberto Pascal
#Cs50: Ai Python Course by Harvard
#Minesweeper Knowledge Algorithms Project
import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #If we know that we have {A,B,C} = 2, then A,B and C must be mines. 
        if len(self.cells) == self.count:
            return self.cells
        #Otherwise, we can have something like {A,B,C} = 2 and not be sure which are mines. 
        else:
            return None
            
        #raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #Similar to known_mines, if I have {A,B,C} = 0, then I know all of them are safe. 
        if self.count == 0:
            return self.cells
        #Otherwise, I cannot eb sure and return nothing. 
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #Means I had something like {A,B,C} = 2 and then learnt that C is safe. therefore, I remove it from the suspicious list. 
        if(cell in self.cells):
            self.cells.remove(cell)
            self.count = self.count -1
        else:
            pass
        
        #raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #Similar to mark mine, except I don't decrease counter. 
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #1) marking the cell as a made move:
        self.moves_made.add(cell)
        #2)marking the cell as safe. 
        #print("Adding safe move to: ", self.safes)
        self.mark_safe(cell)
        #2.2) Now we need to update my knowledge to remove this cell from all sentences since it is a safe cell. 
        for sentence in self.knowledge:
            #remove current cell from knowledge in sentences because it is marked as safe now.
            if sentence.count < len(sentence.cells) and cell in sentence.cells:
                #I only want to remove from those "uncertainities" I had. 
                sentence.cells.remove(cell)
        #3) Adding the new knowledge. I need to explore the boundering cells and add what I know based on my count. 
        #Checking for boundering cells:
        boundering_cells = []
        for x in range(cell[0]-1, cell[0]+2):
            if not (x>=0 and x<=7):
                continue
            else:
                for y in range(cell[1]-1, cell[1]+2):
                    if not(y>=0 and y<=7):
                        continue
                    else:
                        if (x,y) not in self.safes: #check. Maybe I don't need to add mines. 
                            #we only add this to our sentence if we are sure it is not already marked as safe nor mine. 
                            boundering_cells.append((x,y))
                        

        #Add the new knowledge rule:
        new_knowledge = Sentence(boundering_cells, count)
        self.knowledge.append(new_knowledge)
        
        #4) Mark any additional cells as safe or mines depending on my knowledge:
        for sentence in self.knowledge:
            new_sentence = copy.deepcopy(sentence)
            new_safes = copy.deepcopy(self.safes)
            new_mines = copy.deepcopy(self.mines)
            for cell in sentence.cells:
                if sentence.count == len(sentence.cells):
                    #print("securing another mine...", cell)
                    new_sentence.mark_mine(cell)
                    new_mines.add(cell)
                elif sentence.count == 0:
                    #print("securing another safe cell...", cell)
                    new_sentence.mark_safe(cell)
                    new_safes.add(cell)
            sentence = new_sentence
            self.safes.update(new_safes)
            self.mines.update(new_mines)
                        
        #5) make any other inferences that are possible. 
        self.make_possible_inferences()
       # raise NotImplementedError
        #self.print_remaining_safes()
    def print_remaining_safes(self):
        test = []
        for cell in list(self.safes):
            if not cell in list(self.moves_made):
                test.append(cell)
        print("remaining safes: ", test)
    def make_possible_inferences(self):
        """
        This function will try to apply the subset rule to make inferences and create any new rules. 
        If Set1 is subset of Set2, then it is true that Set2-Set1 = Count2 -Count1. 
        """
        knowledge_list = list(self.knowledge)
        print("Infering new rules....")
        for i in range(0,len(knowledge_list)):
            if i+1 == len(knowledge_list):
                break
            else:
                new_safes = copy.deepcopy(self.safes)
                new_mines = copy.deepcopy(self.mines)
                new_cells = []
                new_count = -1
                did_something = False
                if(knowledge_list[i].cells.issubset(knowledge_list[i+1].cells) and bool(knowledge_list[i].cells)):
                    did_something = True
                    new_cells = knowledge_list[i+1].cells - knowledge_list[i].cells
                    new_count = knowledge_list[i+1].count - knowledge_list[i].count
                elif(knowledge_list[i+1].cells.issubset(knowledge_list[i].cells) and bool(knowledge_list[i+1].cells)):
                    did_something = True
                    new_cells = knowledge_list[i].cells - knowledge_list[i+1].cells
                    new_count = knowledge_list[i].count - knowledge_list[i+1].count
                else:
                    pass
                if(did_something):
                    new_sentence = Sentence(new_cells, new_count)
                    if(new_sentence not in self.knowledge):
                        for cell in new_cells:
                            if new_count == len(new_cells):
                                #I found new mine spots: 
                                new_sentence.mark_mine(cell)
                                new_mines.add(cell)
                            elif( new_count== 0):
                                new_sentence.mark_safe(cell)
                                new_safes.add(cell)
                        self.safes.update(new_safes)
                        self.mines.update(new_mines)
                        self.knowledge.append(Sentence(new_cells,new_count))
                        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        #print("I will search for a safe move in ", self.safes)
        if (bool(self.safes)):
            #means I have at least one safe move. 
            safe_moves = list(self.safes)
            for move in safe_moves:
                if move not in self.moves_made:
                    #I have a safe move that I have not used.    
                    print("found my safe move ", move)
                    return move
            print("I did not find my safe move")
            return None
        #if I reach this point in code, there were no safe moves left that I have not done. 
        print("I did not find a safe move")
        return None
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("creating a random move ")
        #print("My confirmed mines are: ", self.mines)
        
        board_cells = set(itertools.product(range(0,self.height), range(0,self.width)))
        #remove moves made
        available_cells = set(board_cells.symmetric_difference(self.moves_made))
        #remove mines
        available_cells = available_cells.symmetric_difference(self.mines)
        
        if len(available_cells)>0:
            return random.choice(list(available_cells))
        else:
            return None