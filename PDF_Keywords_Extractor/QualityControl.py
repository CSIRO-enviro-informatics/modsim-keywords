#from nltk.corpus import brown
import re


class KeywordQualityControl():
    #-this class handles quality of the keywords
    #-Its purpose is to determine positives and negatives
    #-Aims to minimise false positives, and false negatives and
    #  maximise true positives and true negatives
    def __init__(self):
        pass
        #prepare the spelling check words
        #word_list = brown.words()
        #self.word_set = set(word_list)
        #self.word_set2 = set()
        #file = open("dictofwords.txt", "r")
        #for line in file:
        #    self.word_set2.add(line.strip())

    def check(self,keywords):
        # -this function determines if the keywords are correct based on basic checks
        # Inputs:
        # -  [keywords : string] the keywords to check
        # Output:
        # - [result : boolean] if it is an error or not

        # -size errors
        if len(keywords) < 4 or len(keywords) > 250:
            return True

        # -basic counting of words
        temp = keywords.split()

        # keywords vs number of words (+2 extra slack for 2 keywords)
        if len(temp) > max(keywords.count(','), keywords.count(';')) * 5 + 2:
            return True

        return False

    def formatKeywords(self, keywords):
        #- this function formats the keywords into a better structure for storing
        #- Remove newlines
        keywords = keywords.replace("\n","")
        #- remove more then one space

    def trimoutjunk(self,text):
        # -this function cleans out junk from keywords (special cases, whitespace)
        # Inputs:
        # -  [text : string] keywords to be cleaned
        # Output:
        # - [data : string] clearned keywords
        if len(text) > 1:
            temptext = text.lower()
            end = []
            #special cases
            caseend = [' 22nd international congress', "\s*[0-9]*\s*.[0-9]*\s*introduction"]
            #casestart = ["keywords:\s*(\w*\s*[,;]*)*."]
            for case in caseend:
                match = re.search(case, text)
                if match:
                    end.append(match.start())
            '''
            for case in casesend:
                match = re.search(case, text)
                if match:
                    print(text[match.start():match.end() - 1])
            '''
            if len(end) is not 0:
                text = text[0:min(end)]

            #trim white space
            cases = ['  ', '   ', '\t', '\n']
            for case in cases:
                text.replace(case, '')

            #trim ends
            cases = [' ', ',', '.', ';']
            for case in cases:
                if text[len(text)-1] == case:
                    text = text[0:len(text)-2]
            return text
        return ""
'''
    def spellingCheck(self, check_words):
        #counts number of spelling mistakes
        browncounter = 0
        print(len(self.word_set))
        for word in check_words:
            if word.lower() not in self.word_set and word not in self.word_set:
                print("Did not find ", word)
                browncounter += 1

        unixdictcounter = 0
        print(len(self.word_set2))
        for word in check_words:
            if word.lower() not in self.word_set2 and word not in self.word_set2:
                print("Did not find ", word)
                unixdictcounter += 1
        return min(unixdictcounter,browncounter)

#    def spellCorrect(self,word):
'''