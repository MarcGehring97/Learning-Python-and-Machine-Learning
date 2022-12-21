###########################
# 6.00.2x Problem Set 1: Space Cows 

#From codereview.stackexchange.com                    
def partitions(set_):
    if not set_:
        yield []
        return
    for i in range(2**len(set_)//2):
        parts = [set(), set()]
        for item in set_:
            parts[i&1].add(item)
            i >>= 1
        for b in partitions(parts[1]):
            yield [parts[0]]+b


# This is a helper function that will fetch all of the available 
# partitions for you to use for your brute force algorithm.
def get_partitions(set_):
    for partition in partitions(set_):
        yield [list(elt) for elt in partition]

### Uncomment the following code  and run this file
### to see what get_partitions does if you want to visualize it:

#for item in (get_partitions(['a','b','c','d'])):
#     print(item)
        
import time

#================================
# Part A: Transporting Space Cows
#================================

def load_cows(filename):
    """
    Read the contents of the given file.  Assumes the file contents contain
    data in the form of comma-separated cow name, weight pairs, and return a
    dictionary containing cow names as keys and corresponding weights as values.

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a dictionary of cow name (string), weight (int) pairs
    """

    cow_dict = dict()

    f = open(filename, 'r')
    
    for line in f:
        line_data = line.split(',')
        cow_dict[line_data[0]] = int(line_data[1])
    return cow_dict


# Problem 1
def greedy_cow_transport(cows,limit=10):
    """
    Uses a greedy heuristic to determine an allocation of cows that attempts to
    minimize the number of spaceship trips needed to transport all the cows. The
    returned allocation of cows may or may not be optimal.
    The greedy heuristic should follow the following method:

    1. As long as the current trip can fit another cow, add the largest cow that will fit
        to the trip
    2. Once the trip is full, begin a new trip to transport the remaining cows

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)
    
    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    cowsCopy=sorted(cows.items(),key=lambda x:x[1],reverse=True)
    results=[]
    while len(cowsCopy)!=0:
        result=[]
        totalWeight=0.0
        for i in range(len(cowsCopy)):
            if(totalWeight+cowsCopy[i][1])<=limit:
                result.append(cowsCopy[i][0])
                totalWeight+=cowsCopy[i][1]
        results.append(result)
        for i in result:
            cowsLeft=cowsCopy.copy()
            for j in range(len(cowsLeft)):
                if i==cowsLeft[j][0]:
                    cowsCopy.pop(j)
    return(results)
    

# Problem 2
def brute_force_cow_transport(cows,limit=10):
    """
    Finds the allocation of cows that minimizes the number of spaceship trips
    via brute force.  The brute force algorithm should follow the following method:

    1. Enumerate all possible ways that the cows can be divided into separate trips
    2. Select the allocation that minimizes the number of trips without making any trip
        that does not obey the weight limitation
            
    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)
    
    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    cowsPartition=[]
    for partition in get_partitions(cows.keys()):
        cowsPartition.append(partition)
    check=False
    while check==False:
        for partition in cowsPartition:
            result=partition
            partialCheck=True
            for cowNames in partition:
                totalWeight=0.0
                for i in cowNames:
                    totalWeight+=cows[i]
                if totalWeight>limit:
                    partialCheck*=False
            if partialCheck==True:
                return(result)
        
# Problem 3
def compare_cow_transport_algorithms():
    """
    Using the data from ps1_cow_data.txt and the specified weight limit, run your
    greedy_cow_transport and brute_force_cow_transport functions here. Use the
    default weight limits of 10 for both greedy_cow_transport and
    brute_force_cow_transport.
    
    Print out the number of trips returned by each method, and how long each
    method takes to run in seconds.

    Returns:
    Does not return anything.
    """
    # TODO: Your code here
    pass


"""
Here is some test data for you to see the results of your algorithms with. 
Do not submit this along with any of your answers. Uncomment the last two
lines to print the result of your problem.
"""

cows = {"Maggie":3,
"Herman":7,
"Betsy":9,
"Oreo":6,
"Moo Moo":3,
"Milkshake":2,
"Millie":5,
"Lola":2,
"Florence":2,
"Henrietta":9}
limit=10
print(cows)
start = time.time()
print(greedy_cow_transport(cows, limit))
end = time.time()
print(end - start)
start = time.time()
print(brute_force_cow_transport(cows, limit))
end = time.time()
print(end - start)

