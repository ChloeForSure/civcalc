#Loads exchange
#returns a dict, where the keys are the different itemname
#And each value is the sell price for the item
#SellPrice text should follow the pattern:
#k,l,name
#where n are the price in diamonds, l is the number of items sold for that price, 
# #and name is the items name with small leters, singular form.
def loadExchanges(path):
    f=open(path,"r")
    data={}
    lines=f.readlines()
    for i in range(len(lines)):
        l=lines[i].replace('\n','').strip()
        if l=="":
            continue
        elif l[0]=="#":
            continue
        ls=l.split(',')
        if len(ls)!=3:
            raise Exception(f"Line {i+1} is not properly fomated.")
        data[ls[2].strip()]=float(ls[0].strip())/float(ls[1].strip())
    return data

#Loads sell prices
#returns a dict, where the keys are the different itemname
#And each value is the sell price for the item
#SellPrice text should follow the pattern:
#k,l,name
#where n are the price in diamonds, l is the number of items sold for that price, 
# #and name is the items name with small leters, singular form.
def loadSellPrices(path):
    f=open(path,"r")
    data={}
    lines=f.readlines()
    for i in range(len(lines)):
        l=lines[i].replace('\n','').strip()
        if l=="":
            continue
        elif l[0]=="#":
            continue
        ls=l.split(',')
        if len(ls)!=3:
            raise Exception(f"Line {i+1} is not properly fomated.")
        data[ls[2].strip()]=float(ls[0].strip())/float(ls[1].strip())
    return data


#This is way overcomplicated
#But this loads factory data.
#All of the factories should be in the same file.
#All items mentions follow the same pattern, using:
#k,name
#where k is the number of items, and name is the name of the item with small letters, singular form.
#All factories follow this pattern:
#name of the factory
#Factory setup cost, each item in a new line.
#An empty line
#Factory repair cost, each item in a new line.
#an empty line
#The recipes, in the following pattern:
#Output item(s), each item in a new line
#-
#input items, each item in a new line
#an empty line between recipes
#If a given factory doesn't have any more recipes, make two empty lines to start a new factory
#At the end of a file, there should be 3 empty lines.
#The output will be a dict, the keys are the factory names.
#Each key has it's own dict, with 3 keys: 'setup', 'repair' and 'recipes'
#'setup' key contains a dict, where each key is the itemname, and each value is the required amount
#'repair' follows the same pattern as 'setup'
#'recipes' contain a list, where each element is a recipe, that is a two element list.
#The 0 element contains a dict, where the keys are the output items, and the values are the amounts.
#The 1 element contains a dict, where the keys are the input items, and the values are the amounts
#As I said way overly complicated.
#You can find all the available factories here:
#https://civwiki.org/wiki/Factories_(CivMC)
def loadFactories(path):
    f=open(path,"r")
    data={}
    lines=f.readlines()
    state=0
    #states:
    #0 New factory
    #1 Collecting creation cost
    #2 collecting repair cost
    #3 collecting recipe output
    #4 collecting recipe input
    cfn="" #current factory name
    temp={} #temporary dict
    crec=[{},{}]#current recipe
    crecs=[]#current recipes for the factory
    for i in range(len(lines)):
        currentLine=lines[i].replace("\n","").strip()
        if len(currentLine)!=0:
            if currentLine[0]=='#':
                continue
        if state==0:
            if(currentLine!=""):
                data[currentLine]={}
                cfn=currentLine
                state=1
        elif state==1:
            if(currentLine==""):
                data[cfn]["setup"]=temp
                temp={}
                state=2
            else:
                l=currentLine.split(',')
                temp[l[1].strip()]=int(l[0].strip())
        elif state==2:
            if(currentLine==""):
                data[cfn]["repair"]=temp
                temp={}
                state=3
            else:
                l=currentLine.split(',')
                temp[l[1].strip()]=int(l[0].strip())
        elif state==3:
            if(currentLine==""):
                data[cfn]["recipes"]=crecs
                crecs=[]
                state=0
            elif(currentLine=="-"):
                crec[0]=temp
                temp={}
                state=4
            else:
                l=currentLine.split(',')
                temp[l[1].strip()]=int(l[0].strip())
        elif state==4:
            if(currentLine==""):
                crec[1]=temp
                crecs.append(crec)
                crec=[{},{}]
                temp={}
                state=3
            else:
                l=currentLine.split(',')
                temp[l[1].strip()]=int(l[0].strip())
    if(state!=0):
        raise Exception("Did not finish at the end of a factory")
    return data

#Recursively calculating the craft price of an item. Returns the price.
#Returns None if the price cannot be calculated
def calculatePrice(name,eData,fData,getRecipe=True,returnFactory=False):
    #getRecipe prints the optimal recipe
    #returnFactory changes the output to a list to include the factory name
    #First we check if it directly has a price on the exchanges
    exkeys=eData.keys()
    for i in exkeys:
        #If a key matches the itemname, it has, and it returns that price
        if name==i:
            return eData[i]
    potRec=[] #If not, we check every factories every recipe if it outputs the item.
    potRecPath=[] #It gathers all the available recipes in a list to figure out the cheapest one.
    fNames=fData.keys()
    for i in fNames: #iterates through factories
        rcount=len(fData[i]["recipes"])
        for j in range(rcount): #iterates through recipes
            outputs=fData[i]["recipes"][j][0].keys()
            for k in outputs:
                if name==k: #Checks if the recipe outputs the item
                    price=0 
                    inputs=fData[i]["recipes"][j][1].keys()
                    for l in inputs: #Iterate through all the input items
                        curPrice=calculatePrice(l,eData,fData,getRecipe=False,returnFactory=False) #Calculates it's price
                        if curPrice==None: #If one of the input materials doesn't have a price, the price of the recipe cannot be caluclated
                            price=None 
                            break
                        price+=fData[i]["recipes"][j][1][l]*curPrice #And ads it to the current price.
                    if price!=None: #If the price can be calculated, ads it to the potential recipes.
                        potRec.append(price/fData[i]["recipes"][j][0][k])
                        potRecPath.append([i,j])
                    break
    cpr=len(potRec)
    if cpr==0: #If the item has no calculateable recipes, then it returns none.
        if getRecipe: 
            print(f"The price of {name} couldn't be calculated.")
        return None
    else: #If it has calculateable recipes, finds the cheapest one.
        ind=0
        min = potRec[0]
        for i in range(1,len(potRec)):
            if potRec[i] < min:
                min = potRec[i]
                ind=i
        if getRecipe: #Prints things nicely.
            print(f"The cost of a(n) {name} is {potRec[ind]}d\n")
            print(f"Using the following recipe in the {potRecPath[ind][0]}:\nInput")
            recipe=fData[potRecPath[ind][0]]["recipes"][potRecPath[ind][1]]
            for i in recipe[1].keys():
                print(f"{recipe[1][i]} {i}")
            print("Output:")
            for i in recipe[0].keys():
                print(f"{recipe[0][i]} {i}")
        if returnFactory: #If returnFactory is true, it returns a list. The first element is the price, 
            #the second is the name of the factory with the cheapest recipe
            return [potRec[ind],potRecPath[ind][0]] #I only made this so we can neatly calculate the profitability.
        else:
            #If returnFactory is false, it simply returns the price.
            return potRec[ind]

#Calculates the price of setting up a factory. Returns the price
def calculateSetupPrice(name,eData,fData):
    if name in fData.keys():
        price=0
        mats=fData[name]["setup"].keys()
        for i in mats:
            cp=calculatePrice(i,eData,fData,False) #using the calculatePrice.
            if cp==None:#If one of the items cannot be calculated, then the whole setup cost cannot be calculated
                print(f"Price cannot be calculated, as {i} does not have a price.")
                return None
            price+=cp*fData[name]["setup"][i]
        return price
    else: #If a factory doesn't exists returns None.
        print(f"There is no factory called {name}")
        return None

#Exactly the same as calculateSetupPrice, just for the repair cost.
def calculateRepairPrice(name,eData,fData):
    if name in fData.keys():
        price=0
        mats=fData[name]["repair"].keys()
        for i in mats:
            cp=calculatePrice(i,eData,fData,False)
            if cp==None:
                print(f"Price cannot be calculated, as {i} does not have a price.")
                return None
            price+=cp*fData[name]["repair"][i]
        return price
    else:
        print(f"There is no factory called {name}")

#Calculates the profitability of an item. Returns the number of items required to sell within a repair cycle to be profitable
#If printing, prints out all of the data nicely.
#Retrn time is the number of cycles, within which we want to get a return on investment on the factory
def calculateProfitability(name,eData,fData,sData,printing=True, returnTime=15):
    if name in sData.keys():
        sellprice=sData[name]#Gets sellprice of the item
        getprice=calculatePrice(name,eData,fData,False,True) #Calculates price of the item
        if getprice==None:
            print(f"The price of {name} couldn't be calculated.")
            return None
        factory=getprice[1] #Gets the factory of the cheapest recipe
        getprice=getprice[0]
        profit=sellprice-getprice #Gets the profit/item
        repprice=calculateRepairPrice(factory,eData,fData) #Gets the repair cost of the factory
        setupcost=calculateSetupPrice(factory,eData,fData) #Gets the setup cost of the factory
        returnTimeCost=setupcost+repprice*returnTime #Calculates the cost of setting up and maintaining the factory
        #for returnTime cycles
        returnTimeSells=returnTimeCost/profit
        #Calculates the number of items that we have to sell within returnTime cycles to get a profit.
        cycleSells=returnTimeSells/returnTime
        #Calculates the number of items that we have to sell per cycle to be profitable within returnTime cycles
        if repprice == None:
            print(f"The repair price of {factory} couldn't be calculated.")
            return None
        sellsper20days=repprice/profit
        #Disregarding the setup cost, the number of items required to be sold within a cycle to make more money then
        #the repair cost 
        if printing:
            print(f"The price of making a(n) {name} is {getprice}d")
            print(f"The sellprice of {name} is {sellprice}d")
            print(f"The profit is {profit}d")
            print(f"The repair cost of {factory} is {repprice}d")
            print(f"To make a profit, you have to sell {sellsper20days} {name} every repair cycle (20 day)")
            print(f"To get return on investment in {returnTime} cycles (about {returnTime/1.5} months), you have to sell {cycleSells} {name} every repair cycle")
        return sellsper20days
    else: #If something doesn't exist or doesn't have a price returns none
        print(f"{name} does not have a sell price")
        return None
