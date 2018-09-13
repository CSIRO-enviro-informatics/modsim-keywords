import os
import multiprocessing
from PDF_Keywords_Extractor import QualityControl, PdfExtractor
import collections


def extractpdfs(listofpdfs, extractor, errorfiles, folder,qc):
    # -this function extracts text from a list of keywords
    # Inputs:
    # -  [listofpdfs : list[strings] - list of pdfs to extract keywords from
    # -  [extractor : KeywordExtract - extraction object
    # -  [errorfiles : multiprocess.Queue] - queue used to store files names with potential problems
    # -  [folder : string] - the folder where the pdfs are
    file = open("error" + str(os.getpid()) + ".txt","w", encoding='utf-8')
    keywordsout = open("keywords" + str(os.getpid()) + ".txt","w", encoding='utf-8')
    totalcount = 0
    sizeoflist = len(listofpdfs)
    templist = []
    for pdf in listofpdfs:
        # print("extracting ... " + folder + pdf)
        keywords = extractor.extract(folder + pdf)
        totalcount += 1

        #checks for error
        if qc.check(keywords):
            print("potential error in ", pdf)
            print(pdf, keywords)
            #errorfiles.put(pdf + "\t" + keywords)
            templist.append(pdf + "\t" + keywords)
            file.write(pdf + "\t" + qc.trimoutjunk(keywords) + "\n")
        else:
            #save keywords
            keywordsout.write(pdf + "\t" + qc.trimoutjunk(keywords) + "\n")

        #prints progress
        print("[",os.getpid(), "]:",'\t',totalcount, "/", sizeoflist)
    keywordsout.close()
    file.close()
    return templist


if __name__ == '__main__':

    #-settings
    cores = 4 #number of cores to use
    folder = "downloads/" # the folder pdfs are in

    #-testing vars
    #listofpdfs2 = ['-MODSIM03-Volume_03-B02-04_Cao.pdf']
    #folder = "testpdf/"

    #-grabs files in folder
    completelistofpdfs = os.listdir(folder)

    #-clean up pdfs removing non modsim files
    listofpdfs = []

    for pdf in completelistofpdfs:
        #removes all none pdfs/ non modsim files / abstract books
        pdflower = pdf.lower()
        if ".pdf" in pdflower and "modsim" in pdflower and "abstracts" not in pdflower:
            listofpdfs.append(pdf)

    #-counter vars
    errorcount = 0
    totalcount = 0
    sizeoflist = len(listofpdfs)

    #-extract object
    Test = PdfExtractor.KeywordExtract()
    qc = QualityControl.KeywordQualityControl()


    #- Process vars
    errorfiles = multiprocessing.JoinableQueue()
    processes = []


    #-split the list into sections for multiprocessing
    start = 0
    interval = int(sizeoflist/cores)
    end = interval

    #-creates the list of processes to run
    for i in range(0,cores):
        if i == cores - 1:
            processes.append(multiprocessing.Process(target=extractpdfs, args=(listofpdfs[start:], Test, errorfiles, folder,qc)))
        else:
            processes.append(multiprocessing.Process(target=extractpdfs, args=(listofpdfs[start:end],Test, errorfiles,folder,qc)))
            start += interval
            end += interval

    #-runs the proceses
    for p in processes:
        p.start()

    #-closes the completed processes
    for p in processes:
        p.join()


    #Loads files with errors and performs OCR
    loadederrors = []
    for filename in os.listdir():
        if "error" in filename:
           loadederrors = loadederrors + [line.rstrip('\n') for line in open(filename,'r',encoding='utf-8')]


    ocrkeywords = collections.defaultdict(list)
    #use OCr
    print(loadederrors)
    progresscounter = 0
    for error in loadederrors:
        print(error)
        tempfilename = error.split('\t')[0]
        progresscounter += 1
        print("currently at ",progresscounter, "/", len(loadederrors))
        if ".pdf" in tempfilename:
            try:
                ocrkeywords[tempfilename] = Test.extract2( folder + tempfilename)
                print(ocrkeywords[tempfilename])
            except:
                print("Failed " + error)


    # checks for error
    tempcount = 0
    print(ocrkeywords)
    #store ocr keywords
    ocrfile = open("ocrkeywords.txt","rw", encoding="utf-8")

    for word in ocrkeywords.keys():
        if qc.check(ocrkeywords[word]):
            print("potential error in ", word)
            # errorfiles.put(pdf + "\t" + keywords)
            print(ocrkeywords[word], "\t" + word + "\n")
            tempcount+=1
        else:

            print("writing ", word, ocrkeywords[word])
            ocrfile.write(qc.trimoutjunk(ocrkeywords[word]) + '\n')

    # prints total count of keywords under 3 letters and not over 150 letters
    print("Errors: ", len(loadederrors),"/",sizeoflist, "left over ", tempcount, " /", len(loadederrors))
