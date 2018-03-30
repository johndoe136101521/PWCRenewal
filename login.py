import requests
import time



#this gives a list of all occurences of a substring in a string
# (probably a cleaner way of acheving this)
def find(text, string):
    books = []
    i = -1
    while True:
        i = text.find(string, i+1)
        if i == -1:
            return books
        books.append(i)

#renewals left, item number, code of the book,
#and due_date all given in dictionary with the title as a key
#these values are found with the text output of the itemsOut page.  It looks for key
#phrases to identify the books
def book_info(ItemsOut):
        books = find(ItemsOut, "/Mobile/ItemsOut/Details/")
        info ={}
        #title, code
        shift_title = len('/Mobile/ItemsOut/Details/*******">')
        for i in books:
            t = ItemsOut.find('</a>',i+shift_title)
            title = ItemsOut[i+shift_title:t-1]
            r = ItemsOut.find('&nbsp;renewals left', i)
            renewals_left = ItemsOut[r-1]
            d = ItemsOut.find('Due:&nbsp;', i) + len('Due:&nbsp;')
            df = ItemsOut.find('&', d)
            due_date = ItemsOut[d:df]
            code= ItemsOut[i+len('/Mobile/ItemsOut/Details/'): i+len('/Mobile/ItemsOut/Details/*******')]
            info[title] = [renewals_left, due_date, code]
        return info

POST_LOGIN = 'https://librarycatalog.pwcgov.org/Mobile/MyAccount/Logon'

#login information, remberMe must be defined
#username and password given both as strings
payload = {'barcodeOrUsername': your_username,
'password': your_password,
'rememberMe':'false'}

#itemsOut page
renew_url = 'https://librarycatalog.pwcgov.org/Mobile/MyAccount/ItemsOut'
s = requests.Session()
#logging in
post = s.post(POST_LOGIN, data=payload)

#retrieving itemsOut page and parsing it
r = s.get(renew_url)
ItemsOut = str(r.text)
information = book_info(ItemsOut)

today = int(time.strftime("%Y%m%d"))

#used to check if due date has passed
#(could use today as global variable rather than as an argument)
def check_date(due_date, today):
    #make due_date in standard yyyymmdd in order to compare to today
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

renew_data = {'button': 'Renew'}
for i in information:
    if int(information[i][0]) > 0:
        if check_date(information[i][1], today):
            renew_data['chkItem'+information[i][2]] = 'true'
        else:
            renew_data['chkItem'+information[i][2]] = 'false'

#renew the books that need to be
post_RENEW = s.post(renew_url, data=renew_data)

#CAUTION: there may be an error when the renew all button is present, it could be
# a hidden input in the renew form causing it to be incomplete
