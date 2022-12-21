def max_pairwise_product(numbers):
    n = len(numbers)
    max_index1 = 0
    for i in range(n):
        if max_index1 == 0 or numbers[i] > numbers[max_index1]:
            max_index1 = i
            print(max_index1)
    max_index2 = 0
    for i in range(n):
        if i != max_index1 and (max_index2 == 0 or numbers[i] > numbers[max_index2]):
            max_index2 = i
            print(max_index2)
    return numbers[max_index1] * numbers[max_index2]
