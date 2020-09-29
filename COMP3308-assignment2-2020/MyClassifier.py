import sys
import math
import csv
import re


def read_data(fname):
    lines = []
    with open(fname) as f:
        lines = f.readlines()
    return lines


def get_data(fname):
    lines = read_data(fname)

    data = []
    for line in lines:
        line = line.strip()
        data.append(line.split(","))

    for dt in data:
        for i in range(0, len(dt)):
            if dt[i] != "yes" and dt[i] != "no" and "fold" not in dt[i]:
                dt[i] = float(dt[i])

    return data


def Euclid_Distance(training_data, testing_data):
    sum = 0
    for i in range(0, len(training_data) - 1):
        sum = sum + math.pow(training_data[i] - testing_data[i], 2)
    return math.sqrt(sum)


def KNN(k, training_data, test_data):
    ls = []

    for train_data in training_data:
        distance = Euclid_Distance(train_data, test_data)
        ls.append({"distance": distance, "class": train_data[len(train_data) - 1]})

    ls.sort(key=lambda x: (x['distance'], x['class'] != "yes"))

    value = 0
    counter = 0

    for elmnt in ls:
        if counter == k:
            break
        else:
            if elmnt['class'] == "yes":
                value = value + 1
            else:
                value = value - 1
            counter = counter + 1

    if value >= 0:
        print("yes")
    else:
        print("no")


def mean(training_data, index):
    sum_yes = 0
    sum_no = 0
    yes_count = 0
    no_count = 0
    for data in training_data:
        if data[len(data) - 1] == "yes":
            sum_yes = sum_yes + data[index]
            yes_count = yes_count + 1
        else:
            sum_no = sum_no + data[index]
            no_count = no_count + 1
    avg_yes = sum_yes / yes_count
    avg_no = sum_no / no_count

    avg = [avg_yes, avg_no]
    return avg


def standard_dev(training_data, index, average):
    sum_yes = 0
    sum_no = 0
    yes_count = 0
    no_count = 0
    for data in training_data:
        if data[len(data) - 1] == "yes":
            sum_yes = sum_yes + math.pow(data[index] - average[0], 2)
            yes_count = yes_count + 1
        else:
            sum_no = sum_no + math.pow(data[index] - average[1], 2)
            no_count = no_count + 1

    yes = sum_yes / (yes_count - 1)
    no = sum_no / (no_count - 1)
    std_yes = math.sqrt(yes)
    std_no = math.sqrt(no)
    std = [std_yes, std_no, yes_count, no_count]
    return std


def probability_density_function(data, average, std):
    exponent = -math.pow(data - average, 2) / (2 * math.pow(std, 2))
    f = math.exp(exponent) / (std * math.sqrt(math.pi * 2))
    return f


def NB(training_data, testing_data):
    average = []
    std_dev = []
    # range hard coded for pima-folds.csv
    # print(training_data[0])
    for i in range(0, len(training_data[0]) - 1):
        avg = mean(training_data, i)
        std = standard_dev(training_data, i, avg)
        average.append(avg)
        std_dev.append(std)

    yes_prob = std[2] / (std[2] + std[3])
    no_prob = 1 - yes_prob
    for (av, st, data) in zip(average, std_dev, testing_data):
        if st[0] > 0.0:
            yes_prob = yes_prob * probability_density_function(data, av[0], st[0])
        if st[1] > 0.0:
            no_prob = no_prob * probability_density_function(data, av[1], st[1])

    if yes_prob >= no_prob:
        print("yes")
    else:
        print("no")


def create_fold_file(training_data):
    size = int(len(training_data))
    fold_size = int(size / 10)
    print(fold_size)
    remainder = size % 10
    fold = []
    temp = []

    no_data = []
    yes_data = []
    for data in training_data:
        if data[len(data) - 1] == "no":
            no_data.append(data)
        else:
            yes_data.append(data)

    for i in range(0, 10):
        temp1 = []
        for j in range(0, 50):
            temp1.append(no_data[j + i * 50])
        if i == 8:
            for k in range(0, 26):
                temp1.append(yes_data[k + 216])
        elif i == 9:
            for k in range(0, 26):
                temp1.append(yes_data[k + 242])
        else:
            for k in range(0, 27):
                temp1.append(yes_data[k + i * 27])
        temp.append(temp1)

    with open('pima-CFS-folds.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for i in range(0, 10):
            writer.writerow(["fold" + str(i + 1)])
            for item in temp[i]:
                writer.writerow(item)
            writer.writerow("")


def test(training_data):
    folds = []
    temp = []
    for i in range(1, len(training_data)):
        if isinstance(training_data[i][0], str) and 'fold' in training_data[i][0]:
            folds.append(temp)
            temp = []
        else:
            temp.append(training_data[i])
    folds.append(temp)

    accuracy = []
    for i in range(0, 10):
        training = []
        testing = []
        compare = []
        correct = 0
        total = 0
        for k in range(0, 10):
            if k == i:
                testing = folds[k]
            else:
                training.append(folds[k])
        for train in training:
            for test in testing:
                compare.append(KNN(5,train, test))
        for (elmt, test_elmt) in zip(compare, testing):
            if elmt == test_elmt[len(test_elmt) - 1]:
                correct = correct + 1
            total = total + 1
        accurate = correct / total
        accuracy.append(accurate)
    sum = 0
    for elmt in accuracy:
        sum = sum + elmt
    percentage = sum / len(accuracy) * 100
    print(percentage)


def main(argv):
    training_file = argv[0]
    input_file = argv[1]
    methd = argv[2]

    training_dt = get_data(training_file)
    input_dt = get_data(input_file)

    # create_fold_file(training_dt)

    # test(training_dt)

    for input in input_dt:
        if methd == "NB":
            NB(training_dt, input)
        elif "NN" in methd:
            k = methd[0]
            k = int(k)
            KNN(k, training_dt, input)


if __name__ == "__main__":
    main(sys.argv[1:])
