import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import ssl
import pandas as pd

############# SINGSAVER HOME LOAN DETAILS ##################################

url2='https://www.singsaver.com.sg/home-loan'
resp=requests.get(url2)

soup = BeautifulSoup(resp.text,'html.parser')
div = soup.find_all("div", {"class": "swarp-item active"}) #dont change
card_sticky = soup.find_all("div", {"class": "card-sticky"}) #dont change
num_cards=len(card_sticky)

biglist=[]
small=[]
longlist = [i.text.split() for i in div]

for x in range(0,len(longlist)+1):
    if x%11 ==0 and len(small)>0:
        biglist.append(small)
        small=[]
    try:
        if len(longlist[x])>0:
            small.append(longlist[x])
    except:
        pass

def createLoanDict(b):
  loan_dict={}
  for loan in b:
      inner_dict={}
      for j in range(0,len(loan[2:]),2):
          if j+1<len(loan[2:]) :
              inner_dict[' '.join(i for i in loan[2:][j])]=' '.join(i for i in loan[2:][j+1])
      loan_dict[' '.join(i for i in loan[1])]=inner_dict
  return loan_dict

def addToLoanDict(ld):
    details=soup.find_all("div", {"class": "card-details hidden"})
    details_list=[i.text for i in details]
    for k in ld.keys():
        if len(details_list)!=0:
            ld[k]['More details: \n\n']=details_list[0].strip()
            details_list.pop(0)
        else:
            return ld
    return ld

def beautifyDict(d):
  return "\n".join("{}\t{}".format(k, v) for k, v in d.items())

loan_dict= createLoanDict(biglist)
loan_dict_w_more_details=addToLoanDict(loan_dict)
loan_det='\n\nhere are the loan details\n\n'

############# SIBOR ##################################

url="https://www.abs.org.sg/benchmark-rates/rates-sibor"


ssl._create_default_https_context = ssl._create_unverified_context
response = urllib.request.urlopen(url)

bsObj = BeautifulSoup(response,features="lxml")
table=bsObj.find_all('table')
table1=table[0]
rows = table1.find_all('tr')
ths = table1.find_all('th')
header=[i.text.strip() for i in ths]
header[0]='Period'
result=[]

for row in rows[1:]:
    result.append([i.text for i in row.find_all('td')])

df_s = pd.DataFrame(result,columns=header)
df_s.set_index('Period',inplace=True)