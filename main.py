from os import name, read
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from pandas import ExcelFile
import sys


col0 = []   #list of kanji word
col1 = []   #list of hiragana
col2 = []   #list of "Han Viet"
col3 = []   #list of Vietnamese mean
kanji = []

data = []       #output data
no_data = []    #var for miss data
 

e = 0


# display processing when building
def process_dis(i):
    k = (i+1)/n
    sys.stdout.write('\r')
    sys.stdout.write("[%-35s] %d%% " % ('#'*int(35*k), 100*k))
    sys.stdout.write("              missdata: %d/%d" %(len(no_data),n))
    sys.stdout.flush()
    return

#crawl data from web
def crawl_data(*tex):
    datamissflat = False
    mean_str = []
    try: 
        hira = browser.find_elements_by_css_selector('[class^=\"phonetic-word japanese-char cl-content\"]')
        hira = hira[0].text
    except:
        hira = "-"
        datamissflat = True
        #print("\n missing hiragana: %r"%tex)
    try:
        han = browser.find_elements_by_css_selector('[class^=\"han-viet-word cl-content\"]')
        han = han[0].text
        han = han.replace("「","")
        han = han.replace("」","")
    except:
        han ="-"
        datamissflat = True
        #print("\n missing han tu: %r"%tex)
    if browser.find_elements_by_css_selector('[class^=\"mean-fr-word cl-blue\"]'):
        meanls = browser.find_elements_by_css_selector('[class^=\"mean-fr-word cl-blue\"]')
        for i in range(len(meanls)):
            mean = str(meanls[i].text)
            mean = mean.replace("◆","")
            mean = mean.replace(".","")
            mean_str.append(mean)
            mean = ' /'.join(map(str,mean_str))
    else:
        mean = "-"
        datamissflat = True
        #print("\n unknown meaning %r"%tex)
    if datamissflat is True:
        datamissflat = False
        no_data.append(tex)

    
    return hira, han, mean

#main program 

link = "https://mazii.net/search?hl=vi-VN"
input = r'kotoba.xlsx'

#access web
print("web opening.....")
options = webdriver.ChromeOptions() 
options.headless= True  #hide browser
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(chrome_options=options, executable_path=r'chromedriver.exe') 
browser.get(link)


#load data
print("data reading.....")
df = pd.read_excel(input)
for i in df.index:
    kanji.append(df['Word'][i])
n = len(kanji)
sleep(2)

#LOOP crawl data /////////////////////////////////////////////////////////////////////////////////////////////////


for x in kanji:
    process_dis(e)
    search_data = browser.find_element_by_id("search-text-box")
    search_data.clear()
    search_data.send_keys(x)
    btn = browser.find_element_by_xpath("/html/body/app-root/div/div[1]/div/app-header-search/div[1]/div[1]/div[1]/div[2]/div/button/div")
    btn.click()
    sleep(1)
    hira, han, mean = crawl_data(x)
    col0.append(x)
    col1.append(hira)
    col2.append(han)
    col3.append(mean)
    #print(x,"\t", hira,"\t", han,"\t", mean)
    search_data.clear()
    e+=1


data = ({'Kanji':col0, 'Hira':col1 , 'Han':col2,'Mean':col3})
df= pd.DataFrame.from_dict(data, orient='index')
df = df.transpose()
df.to_csv(r"kanji_conv_file.csv",index=False)
#df.to_excel(r"C:\Users\cgly6\Desktop\HTML\test.xlsx",index=False)
browser.close()
print("\nDone!")
#print("\ndata missing %r/%r\n" %(len(no_data),n))
print(no_data)