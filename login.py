import requests
import time

today = int(time.strftime("%Y%m%d"))

#used later to parse ItemsOut page to find books
def find(text, string):
    books = []
    i = -1
    while True:
        i = text.find(string, i+1)
        if i == -1:
            return books
        books.append(i)
#creates a dictionary of books along with due date,
#renewals left, and item number
def book_info(ItemsOut):
        books = find(ItemsOut, "/Mobile/ItemsOut/Details/")
        info ={}
        #title, code
        shift_title = len('/Mobile/ItemsOut/Details/1499265">')
        for i in books:
            t = ItemsOut.find(':',i+shift_title)
            title = ItemsOut[i+shift_title:t-1]
            r = ItemsOut.find('&nbsp;renewals left', i)
            renewals_left = ItemsOut[r-1]
            d = ItemsOut.find('Due:&nbsp;', i) + len('Due:&nbsp;')
            df = ItemsOut.find('&', d)
            due_date = ItemsOut[d:df]
            code= ItemsOut[i+len('/Mobile/ItemsOut/Details/'): i+len('/Mobile/ItemsOut/Details/1499265')]
            info[title] = [renewals_left, due_date, code]
        return info

POST_LOGIN = 'https://librarycatalog.pwcgov.org/Mobile/MyAccount/Logon'

#login information, remberMe must be defined
payload = {'barcodeOrUsername': your_bardcode,
'password': your_password,
'rememberMe':'false'}

renew_url = 'https://librarycatalog.pwcgov.org/Mobile/MyAccount/ItemsOut'
#renew = {'chkItem1688949':'true', 'button':'Renew'}
s = requests.Session()
post = s.post(POST_LOGIN, data=payload)


r = s.get(renew_url)
ItemsOut = str(r.text)
information = book_info(ItemsOut)

#check if due date has passed
def check_date(due_date, today):
    #make due due_date in standard yyyymmdd in order to compare to today
    due_date = due_date.split('/')
    date = due_date[2]
    if len(due_date[0]) == 1:
        date = date + '0' + due_date[0]
    else:
        date = date + due_date[0]
    if len(due_date[1]) == 1:
        date = date + '0' + due_date[1]
    else:
        date = date + due_date[1]
    if today >= int(date):
        return True
    else:
        return False

print(information)
renew_data = {'button': 'Renew'}
for i in information:
    if int(information[i][0]) > 0:
        if check_date(information[i][1], today):
            renew_data['chkItem'+information[i][2]] = 'true'
        else:
            renew_data['chkItem'+information[i][2]] = 'false'

print(renew_data)
post_RENEW = s.post(renew_url, data=renew_data)
