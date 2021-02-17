import random
import numpy as np
import collections
from scipy.stats import norm, kurtosis, binom
import matplotlib.pyplot as plt

#https://stg.som.yale.edu/overview
#I decided for a relatively simple nonparametric model (a ranking) as opposed to 
#a parametric model, since I did not manage to understand the statistics to more 
#statistical inferences and create Monte Carlo simulations, though I tried both 
#approaches. A machine learning appraoch failed, since I couldn't manage to convert 
#the privite information peeks into labels that could be read by the sklearn module.

#Important consideration: SAR information is virtually useless
#Replacement / no replacement differences plus double drawing of cards makes the modeling
#very difficult

#Decks
x = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 20]
red = np.array(x*2)*-1
black = np.array(x*2)*2
fulldeck = np.concatenate((red,black))

'''
plt.hist(fulldeck, bins='auto')
plt.title("Histogram with 'auto' bins")
plt.show()
'''

#Probability calculations
probdict = {}
freqdict = {}
for card in fulldeck:
    if card not in probdict.keys():
        freqdict[card] = 1
        probdict[card] = 1/52
    else:
        freqdict[card] += 1
        probdict[card] += 1/52
cumprobdict = {}
temp = 0
for key in probdict:
    cumprobdict[key] = probdict[key] + temp
    temp += probdict[key]
freqdictwithout4 = freqdict.copy()
freqdict[4] = 10
#Allowing the mean value to be added for estimation purposes



#Intrinsic value calculation
permissioncheck = 0
def intval(privinfos, epsinfo):
    length = 0
    for info in privinfos:
        length += len(info)
    certinfos = {}
    for card in fulldeck:
        if card not in certinfos.keys():
            certinfos[card] = 0
    uncertinfos = certinfos.copy()
    probdiff = certinfos.copy()
    criterion = certinfos.copy()
    
    for i in range(len(privinfos)):
        tempdict = {}
        for j in range(3):
            if privinfos[i][j] not in freqdict.keys():
                print("Impermissible value")
                global permissioncheck 
                permissioncheck = 1
                break
            if privinfos[i][j] not in tempdict.keys():
                tempdict[privinfos[i][j]] = 1
            else:
                tempdict[privinfos[i][j]] += 1
            if certinfos[privinfos[i][j]] == 0:
                certinfos[privinfos[i][j]] = 1
            elif certinfos[privinfos[i][j]] <= freqdict[privinfos[i][j]] and tempdict[privinfos[i][j]] > certinfos[privinfos[i][j]]:
                certinfos[privinfos[i][j]] += 1
            elif freqdict[privinfos[i][j]] > 1:
                uncertinfos[privinfos[i][j]] += 1

    x = sum(certinfos.values())

    if sum(certinfos.values()) < 10:
        for key in certinfos.keys():
            if certinfos[key] > 0:
                probdiff[key] = min((10 - sum(certinfos.values()))/10, freqdict[key]/10 - certinfos[key]/10)
        for key in certinfos.keys():
            try:
                criterion[key] = uncertinfos[key]/min(10 - x, probdict[key]*52 - certinfos[key])
            except:
                criterion[key] = 0
        criterion = {k: v for k, v in sorted(criterion.items(), key=lambda item: item[1])}
        i = 0
        j = 0
        while j < 10 - x:
            y = list(criterion.keys())[-(i + 1)]
            z = list(criterion.keys())[-(i + 2)]
            if certinfos[y] < freqdictwithout4[y]:
                if criterion[y] > 0:
                    if y == z:
                        a = random.choice((y, z))
                        certinfos[a] += 1
                        j += 1
                        if j < 10 - x:
                            certinfos[y + z - a] += 1
                            j += 1
                            i += 1
                    else:
                        certinfos[y] += 1
                        j += 1
                else:
                    certinfos[4] += 1
                    j += 1
                    #4being the mean card value (unlikely case here)
            i += 1
        
    intval = 0
    for key in certinfos:
        intval += key*certinfos[key]
    #print(collections.OrderedDict(sorted(criterion.items())))
    #print(collections.OrderedDict(sorted(certinfos.items())))
        
    return intval + epsinfo, x, certinfos
    #Program adds the values to certinfos that have the highest division of 
    #uncertinfos and the "space" there would be for a value given its frequency
    #Big assumption: there is no values twice among the unknown cards
    #x is the number of certain cards

#Values EPS can take on
posepsvals = []
for key1 in freqdict.keys():
    for key2 in freqdict.keys():
        posepsvals.append(key1 - key2)
#There are certainly more efficient algorithms
        
#Function to estimate EPS based no the certain card values and the remaining
#cards in the deck
def epsestimate(privinfos, epsinfos):
    certinfos = intval(privinfos, epsinfos)[2]
    replacedcardval = 0
    replacingcardval = 0
    for key in certinfos.keys():
            replacedcardval += key * certinfos[key]
            replacingcardval += key * (freqdictwithout4[key] - certinfos[key])
    replacedcardval /= 10
    replacingcardval /= 42
    x = replacingcardval - replacedcardval
    minindex = 10000
    for val in posepsvals:
        if x < minindex:
            minindex = val
    return minindex
    

#Portfolio class
class Portfolio:
    def __init__(self, stocks):
        #self.weights = weights
        self.stocks = stocks
        self.intvals = [None]*4
        self.certainty = [None]*4
        self.numprivinfos = [None]*4
        self.epsests = [None]*4
    
    def get_intvals(self):
        for i in range(4):
            self.intvals[i] = self.stocks[i].get_intval()[0]
        #self.intvals[4] = 1
        return self.intvals
    
    def get_certainty(self):
        for i in range(4):
            self.certainty[i] = self.stocks[i].get_intval()[1]
        return self.certainty     

    def get_numprivinfos(self):
        for i in range(4):
            self.numprivinfos[i] = len(self.stocks[i].get_privinfo())
        return self.numprivinfos     

    def get_epsestimates(self):   
        for i in range(4):        
            self.epsests[i] = self.stocks[i].get_epsestimate()
        return self.epsests
            
#Stock class
class Stock:
    def __init__(self):
        self.intval = 40
        self.epsinfo = 0
        self.privinfo = []
        self.epscounter = 0

    def get_intval(self):
        if not not self.privinfo:
            return intval(self.privinfo, self.epsinfo)[:2]
        else:
            return self.intval + self.epsinfo, 0

    def get_epsinfo(self):
        return self.epsinfo

    def set_epsinfo(self, epsinfo):
        self.epsinfo = epsinfo
        self.epscounter = 1
    
    def del_lastepsinfo(self):
        self.epsinfo = 0
        self.epscounter = 0

    def get_privinfo(self):
        return self.privinfo

    def add_privinfo(self, privinfo):
        self.privinfo.append(privinfo)
        
    def del_lastprivinfo(self):
        self.privinfo.pop(-1)
        
    def del_allprivinfo(self):
        self.privinfo = []
        
    def get_epsestimate(self):
        if self.epscounter == 0:
            return epsestimate(self.privinfo, self. epsinfo)
        else:
            return "EPS known already and considered in intrinsic value"

#Initiation of stocks and portfolio
G = Stock()
Q = Stock()
R = Stock()
B = Stock()
stocks = [G, Q, R, B]
portfolio = Portfolio(stocks)

#Input after each update
print("\nPlease provide information in the following order: G, Q, R, B")
lastinput = ""
laststock = ""
while True:    
    inp1 = ""
    while inp1 != "priv" and inp1 != "eps":
        inp1 = input("\nDo you want to add private or EPS information? priv/eps ")
          
    if inp1 == "priv":
        
        #Private information
        counter = 0
        while True:
            try:
                if counter ==0:
                    comp = ""
                    while comp != "g" and comp != "q" and comp != "r" and comp != "b":
                        comp = input("\nWhat is the letter of the company? g/q/r/b ")
                    if comp == "g":
                        i = 0
                    elif comp == "q":
                        i = 1
                    elif comp == "r":
                        i = 2
                    elif comp == "b":
                        i = 3   
                if stocks[i].get_intval()[1] == 10:
                    break
                inp = (input("\nWhat are the new private information? ").split(", "))
                #Expected input: 12, 23, 13
                inp = [ int(x) for x in inp ]
                #Converting entries into integers
                if len(inp) < 3:
                    raise ValueError
                for value in inp:
                    if value not in freqdictwithout4:
                        raise ValueError
                stocks[i].add_privinfo(inp)
                if stocks[i].get_intval()[1] == 10:
                    break
                if stocks[i].get_intval()[1] > 10:
                    stocks[i].del_lastprivinfo()
                    raise ValueError
                counter += 1
                inp = ""
                print("\n" + str(stocks[i].get_intval()[1]) + " certain cards!")
                while inp != "y" and inp != "n":
                    inp = input("\nWould you like to add private information? y/n ")
                if inp == "n":
                    break
                
            except:
                print("\nInsertion failed")
                continue
            #Reveals three random cards of one of three of the companies
            #Remember that there are different ways to get a value of 20 and -10
            #There are also always
        lastinput = "priv"
        laststock = stocks[i]
    
    elif inp1 == "eps":
    
        #EPS information
        while True:
            try:
                comp = ""
                while comp != "g" and comp != "q" and comp != "r" and comp != "b":
                    comp = str(input("\nWhat is the letter of the company? g/q/r/b "))
                if comp == "g":
                    i = 0
                elif comp == "q":
                    i = 1
                elif comp == "r":
                    i = 2
                elif comp == "b":
                    i = 3
                inp = int(input("\nWhat is the new EPS information? "))
                if inp not in posepsvals:
                    raise ValueError
                #Expected input: 12
                stocks[i].set_epsinfo(inp)
                break
            except:
                print("\nInsertion failed")
                continue
            #For one company at a time
            #Changes estimated intrinsic value by the given number 
            #by permanently deleting a card and then adding a new card
        lastinput = "eps"
        laststock = stocks[i]
        
    print("\nEstimated intrinsic values; # certain cards; # private information peeks; Estimated EPS\n")
    #f-string implementation would've been better
    print("G: " + str(portfolio.get_intvals()[0]) + ", " + str(portfolio.get_certainty()[0]) + ", " + str(portfolio.get_numprivinfos()[0]) + ", " + str(portfolio.get_epsestimates()[0]))
    print("Q: " + str(portfolio.get_intvals()[1]) + ", " + str(portfolio.get_certainty()[1]) + ", " + str(portfolio.get_numprivinfos()[1]) + ", " + str(portfolio.get_epsestimates()[1]))
    print("R: " + str(portfolio.get_intvals()[2]) + ", " + str(portfolio.get_certainty()[2]) + ", " + str(portfolio.get_numprivinfos()[2]) + ", " + str(portfolio.get_epsestimates()[2]))
    print("B: " + str(portfolio.get_intvals()[3]) + ", " + str(portfolio.get_certainty()[3]) + ", " + str(portfolio.get_numprivinfos()[3]) + ", " + str(portfolio.get_epsestimates()[3]))
    print("")
    print("For 75% accuracy, buy 19 peeks")
    print("For 80% accuracy, buy 23 peeks")
    print("For 85% accuracy, buy 27 peeks (recommended)")
    print("For 90% accuracy, buy 34 peeks (recommended)")
    print("For 95% accuracy, buy 48 peeks")
    print("")
    
    inp = ""
    while inp != "y" and inp != "n":
        inp = input("Would you like to remove your last input? y/n ")
    if  inp == "y":
        if lastinput == "priv" and permissioncheck == 0:
            laststock.del_lastprivinfo()
        elif lastinput == "eps":
            laststock.del_lastepsinfo()
        permissioncheck = 0
        print("\nG: " + str(portfolio.get_intvals()[0]) + ", " + str(portfolio.get_certainty()[0]) + ", " + str(portfolio.get_numprivinfos()[0]) + ", " + str(portfolio.get_epsestimates()[0]))
        print("Q: " + str(portfolio.get_intvals()[1]) + ", " + str(portfolio.get_certainty()[1]) + ", " + str(portfolio.get_numprivinfos()[1]) + ", " + str(portfolio.get_epsestimates()[1]))
        print("R: " + str(portfolio.get_intvals()[2]) + ", " + str(portfolio.get_certainty()[2]) + ", " + str(portfolio.get_numprivinfos()[2]) + ", " + str(portfolio.get_epsestimates()[2]))
        print("B: " + str(portfolio.get_intvals()[3]) + ", " + str(portfolio.get_certainty()[3]) + ", " + str(portfolio.get_numprivinfos()[3]) + ", " + str(portfolio.get_epsestimates()[3]))
       
    inp = ""
    while inp != "y" and inp != "n":
        inp = input("\nWould you like to erase all your peek information? y/n ")
    if  inp == "y":
        laststock.del_allprivinfo()
        permissioncheck = 0
        print("\nG: " + str(portfolio.get_intvals()[0]) + ", " + str(portfolio.get_certainty()[0]) + ", " + str(portfolio.get_numprivinfos()[0]) + ", " + str(portfolio.get_epsestimates()[0]))
        print("Q: " + str(portfolio.get_intvals()[1]) + ", " + str(portfolio.get_certainty()[1]) + ", " + str(portfolio.get_numprivinfos()[1]) + ", " + str(portfolio.get_epsestimates()[1]))
        print("R: " + str(portfolio.get_intvals()[2]) + ", " + str(portfolio.get_certainty()[2]) + ", " + str(portfolio.get_numprivinfos()[2]) + ", " + str(portfolio.get_epsestimates()[2]))
        print("B: " + str(portfolio.get_intvals()[3]) + ", " + str(portfolio.get_certainty()[3]) + ", " + str(portfolio.get_numprivinfos()[3]) + ", " + str(portfolio.get_epsestimates()[3]))        
        
    inp = ""
    while inp != "y" and inp != "n":
        inp = input("\nWould you like to continue? y/n ")
    if  inp == "n":
        break
    print("")

"+ - + - + - + - + - + - + Performance Simulations + - + - + - + - + - + - +" 


#Test for the intval function
def modeltest(numpeeks, numtrials = 100000):
    output1 = 0
    output2 = 0
    for i in range(numtrials):
        x, y = randomdrawer(numpeeks)
        z = intval(x, 0)
        if abs(z[0] - y) <= 0:
            output1 += 1
        output2 += z[1]
        if i%(numtrials/20) == 0:
            print(str(int(i/numtrials*100))+"%")
    return output1/numtrials, output2/numtrials
#First value is how often the model predicted correctly (confidence), second 
#value is a measure of uncertaintly

#Benefit per cost calculation
def slopingtest():
    temp = modeltest(9, 1000)[0]
    maxi = 0
    for i in range(10, 100):
        x = modeltest(i, 1000)[0]
        if x - temp > maxi:
            maxi = i
        temp = x
        if i%5 == 0:
            print(str(int(i))+"%")
    return maxi
#Find the number of draws where the marginal confidence is maximum
#Cost does not increase with draws
#Simulation result: marginal benefit of information is steadily decreasing

#Identify the number of draws to reach a level of confidence
def accuracyfinder():
    output75 = []
    output80 = []
    output85 = []
    output90 = []
    output95 = []
    accuracy = 0
    for i in range(100):
        accuracy = modeltest(i)[0]
        if accuracy >= 0.75:
            output75.append(i)
        if accuracy >= 0.8:
            output80.append(i)
        if accuracy >= 0.85:
            output85.append(i)
        if accuracy >= 0.90:
            output90.append(i)
        if accuracy >= 0.95:
            output95.append(i)
            break
        print("\nPeek " + str(i + 1) + " completed! Accuracy is " + str(accuracy) + "\n")
    return output75[0], output80[0], output85[0], output90[0], output95[0]

#Results:
#For 75%, we need to draw 19
#For 80%, we need to draw 23
#For 85%, we need to draw 27
#For 90%, we need to draw 34
#For 95%, we need to draw 48
    
def certaintyfinder():
    output7 = []
    output8 = []
    output9 = []
    output925 = []
    output95 = []
    certainty = 0
    for i in range(100):
        certainty = modeltest(i)[1]
        if certainty >= 7:
            output7.append(i)
        if certainty >= 8:
            output8.append(i)
        if certainty >= 9:
            output9.append(i)
        if certainty >= 9.25:
            output925.append(i)
        if certainty >= 9.5:
            output95.append(i)
            break
        print("\nPeek " + str(i + 1) + " completed! Certainty is " + str(certainty) + "\n")
    return output7[0], output8[0], output9[0], output925[0], output95[0]

#Results:
#For 7, we need to draw 5
#For 8, we need to draw 7
#For 9, we need to draw 13
#For 9.25, we need to draw 18
#For 9.5, we need to draw 28

#Simulating the random behavior of the underlying samples
def randomdrawer(numpeeks):
    output =[] 
    x = list(np.random.choice(fulldeck, 10, False))
    for i in range(numpeeks):
        y = list(np.random.choice(x, 3, False))
        output.append(y)
    return output, sum(x)