import json

class keywordjsonhandler():

    def createFile(self, path):
        #- creates a empty file
        try:
            file = open(path,'x')
        except IOError:
            print("Error creating the file", path)
            return False
        else:
            file.close()
            return True

    def loadFile(self,path):
        #- returns the file in python format
        try:
            file = open(path,'r')
        except IOError:
            print("Error loading the file", path)
            return ''
        else:
            data = json.loads(file.read())
            file.close()
            return data

    def savetojson(self,path,data):
        #- saves object/data to file in json format
        try:
            file = open(path,'w')
        except IOError:
            print("Error saving the file", path)
            return False
        else:
            file.write(json.dumps(data))
            file.close()
            return True

test = keywordjsonhandler()
test.createFile("test.json")
people = {"Henry" : {"Location" : "1", "In" : True},
         "Joe": {"Location": "2", "In": True},
        "Bob" : {"Location": "0", "In": False},
         }
print(people["Henry"])
test.savetojson("test.json",people)
print(test.loadFile("test.json"))
