import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # I need to first order my information. Who from these have no bad genes?
    number_of_genes = 0
    no_genes = []
    probabilities = []
    shows_trait = False
    joint_prob = 1.0

    Gene_probabilities = {
        "mother":{},
        "father":{},
        "no_parents":{}
    }
    

    for person in people:
        #Prepare my probability dictionary
        for gene in range (0,3):
            Gene_probabilities["mother"][gene] = {"good": 0, "bad": 0}
            Gene_probabilities["father"][gene] = {"good": 0, "bad": 0}
            Gene_probabilities["no_parents"][gene] = {"good": 1-PROBS["gene"][gene], "bad": PROBS["gene"][gene] }

        #First determine the number of genes a person has.
        #print("I am now in person: ", person)
        if person in one_gene:
            number_of_genes = 1
        elif person in two_genes:
            number_of_genes = 2
        else:
            number_of_genes = 0
        
        #Next, determine whether the person shows the trait or not. 
        if person in have_trait:
            shows_trait = True
        else:
            shows_trait = False

        #Finally, fill the parent's dictionary information:
        mother = people[person]["mother"]
        father = people[person]["father"]

        #If the person has no parents, we fetch the unconditional probability. 
        if mother is None and father is None:
            joint_prob *= Gene_probabilities["no_parents"][number_of_genes]["bad"]
        else:
            #Else, we check the corresponding probabilities:
            num_gens_mom = 0
            num_gens_dad = 0
            if mother in one_gene:
                """
                    Given by: 
                    Probability of giving a good gene and the gene NOT mutating OR
                    Probability of giving a bad gene and the gene mutating into a good one.
                """
                Gene_probabilities["mother"][1]["good"] = (0.5 * PROBS["mutation"]) + (0.5 * (1-PROBS["mutation"]))
                Gene_probabilities["mother"][1]["bad"] = 1- Gene_probabilities["mother"][1]["good"]
                num_genes_mom = 1
            elif mother in two_genes: 
                """
                    Given by:
                    Probability of giving a bad gene and it mutating
                """
                Gene_probabilities["mother"][2]["good"] = (PROBS["mutation"])
                Gene_probabilities["mother"][2]["bad"] = 1- Gene_probabilities["mother"][2]["good"]
                num_genes_mom = 2
            else:
                """
                    Given by:
                    Probability of mother giving a good gene and it NOT mutating
                """
                Gene_probabilities["mother"][0]["good"] = (1-PROBS["mutation"])
                Gene_probabilities["mother"][0]["bad"] = 1- Gene_probabilities["mother"][0]["good"]
                num_genes_mom = 0

            if father in one_gene:
                """
                    Given by: 
                    Probability of giving a good gene and the gene NOT mutating OR
                    Probability of giving a bad gene and the gene mutating into a good one.
                """
                Gene_probabilities["father"][1]["good"] = (0.5 * PROBS["mutation"]) + (0.5 * (1-PROBS["mutation"]))
                Gene_probabilities["father"][1]["bad"] = 1- Gene_probabilities["father"][1]["good"]
                num_genes_dad = 1

            elif father in two_genes: 
                """
                    Given by:
                    Probability of giving a bad gene and it mutating
                """
                Gene_probabilities["father"][2]["good"] = (PROBS["mutation"])
                Gene_probabilities["father"][2]["bad"] = 1- Gene_probabilities["father"][2]["good"]
                num_genes_dad = 2

            else:
                """
                    Given by:
                    Probability of father giving a good gene and it NOT mutating
                """
                Gene_probabilities["father"][0]["good"] = (1-PROBS["mutation"])
                Gene_probabilities["father"][0]["bad"] = 1- Gene_probabilities["father"][0]["good"]
                num_genes_dad = 0
            
            #print("PROBABILITY OF BAD:", {father: Gene_probabilities["father"][num_genes_dad]["bad"], mother: Gene_probabilities["mother"][num_genes_mom]["bad"]})
            
            #Calculating the probabilities for the genes:
            if number_of_genes == 2:
                """
                    This means I received both a bad gene from mom and a bad gene from dad by:
                    Received a bad gene from mom and a bad gene from dad
                    Received a bad gene from mom and a good gene from dad that mutated.
                    Received a good gene from mom that mutated and a bad gene from dad
                    Received a good gene from both and both mutated.
                """
                joint_prob*=Gene_probabilities["mother"][num_genes_mom]["bad"] * Gene_probabilities["father"][num_genes_dad]["bad"]
            elif number_of_genes == 1:
                """
                    This will mean I have one bad gene. I can get that gene by:
                    Having mother give me the bad gene 
                                OR (makes it a + of probabilities)
                    Having father give me the bad gene.

                    In case i don't have a mother or father, the probability becomes generic. 
                """
                joint_prob *= Gene_probabilities["mother"][num_genes_mom]["bad"] * Gene_probabilities["father"][num_genes_dad]["good"] + Gene_probabilities["mother"][num_genes_mom]["good"] * Gene_probabilities["father"][num_genes_dad]["bad"]
            else:
                """
                    This will mean I will not have to calculate any complex probabilities.
                    The probability is given by receiving a good gene from mom and a good gene from dad. 
                """
                joint_prob *= Gene_probabilities["mother"][num_genes_mom]["good"] * Gene_probabilities["father"][num_genes_dad]["good"]
            
            #Finally, we calculate the join probability of showing traits:
        joint_prob *= PROBS["trait"][number_of_genes][shows_trait]
    #print("Returning probability of ", joint_prob)
    return joint_prob
    #raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        number_of_genes = 0
        shows_trait = False
        if person in one_gene:
            number_of_genes = 1
        elif person in two_genes:
            number_of_genes = 2

        if person in have_trait:
            shows_trait = True

        probabilities[person]["gene"][number_of_genes] = probabilities[person]["gene"][number_of_genes] + p
        probabilities[person]["trait"][shows_trait] = probabilities[person]["trait"][shows_trait] + p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        #I will now fetch the contets of that person's distribution:
        for distribution in probabilities[person]:
            sum_of_values = 0
            for value in probabilities[person][distribution].values():
                sum_of_values+=value
            #Run the same cycle but now updating everything:
            for value in probabilities[person][distribution]:
                probabilities[person][distribution][value] = probabilities[person][distribution][value] / sum_of_values



if __name__ == "__main__":
    main()