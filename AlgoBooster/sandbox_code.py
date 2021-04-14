
saveVarValues = { }

def addToSaveVarValues(var, value):
    found = False
    try:
        for values in saveVarValues.get(str(var)):
            if value == values:
                found = True
    except TypeError:
        saveVarValues[str(var)] = []
    except KeyError:
        found = False

    if not(found):
        saveVarValues[str(var)] += [value]
    else:
        try:
            checkFile = open( "virtualenvs/checkFile.txt", "w")
            checkFile.write("1")
            checkFile.close()
        except IOError as ioe:
            print("Error while writing saved var values to file:", ioe)

addToSaveVarValues('a', [1, 2, 3])
a = [1, 2, 3]
for i in range(0, 10, 1):
    for j in range(0, 10, 1):
        addToSaveVarValues('a', a + [i])
        a = a + [i]
