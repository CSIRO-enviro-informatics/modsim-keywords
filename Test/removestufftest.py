
with open("keywords13460.txt","r", encoding="utf-8") as file:
    str = file.read()
    str = str.replace("\n\n","\n")
    str = str.replace("\n\r", "\n")
    str = str.replace("\r\n", "\n")
    str = str.replace("\r\r", "\n")
    str = str.rstrip()
    str = str.lstrip()
    with open('keywordsfixed13460.txt',"w",encoding="utf-8") as file2:
        file2.write(str)