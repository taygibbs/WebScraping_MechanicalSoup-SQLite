# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 11:39:50 2024

@author: tayta
"""

import mechanicalsoup #import used for scraping information from website
import pandas as pd #used to hold the data
import sqlite3 #used to connect/grab database

from urllib.request import pathname2url #this is used to check to see if a database exists already. NOT part of the tutorial

url = 'https://en.wikipedia.org/wiki/Comparison_of_Linux_distributions' #url to look at


browser = mechanicalsoup.StatefulBrowser() #creates a browser object to connect to a url

browser.open(url)

"""
To get the data from SPECIFIC parts of the website, go to the website and press CTRL + SHIFT + C to get to dev. details.

Hover over an element. We are looking for anything that has table-rh or class similar to that name. 
"""

# extracting table headers (th)
th = browser.page.find_all('th', attrs= {'class': 'table-rh'}) #grabs all the heading tags from the webpage. DOES NOT GRAB INFO OF HEADER FROM TABLE
# ^This will pull anything on the page that has a th description and anything with the class 'table-rh'. This will give us a LOT of data, so we can reduce it by disposing unnecessary text below.

distribution = [value.text.replace('\n','') for value in th] #focuses on the texts of the tags in th. The .replace will find all of the new line commands (\n) and replace them with empty string
#print(distribution) #prints the list of all the distribution (headers of the wikitable)

"""
Notice that when this is ran, the list that is printed shows a bunch of headers, but looking at the entries, it has all of the headers for ALL of the tables in the site. 
To change this, we can change the list itself to only include the headers from the table we care about.
"""
#print(distribution.index('Zorin OS')) #prints the first index of the last distro found on the table we are looking for
distribution = distribution[:distribution.index('Zorin OS') + 1]
#print(distribution) #prints the new list

# extracting table data (td)
# to get the data, it will follow a similar pattern to the browser.page.find_all() command, but instead, we will look at the dev details on the site and see that the info on the table is labeled td
td = browser.page.find_all('td')
columns = [value.text.replace('\n','') for value in td]

#print(columns)

#this will find too much information, much like the headers. This time, we have to find where the tables are put next to each other and find a descriptive data element to use to tell where to end/begin our list.
# in this case, we are using the word 'AlmaLinux OS Foundation' as the start, and 'Binary blobs' because it is the start of the next table and is desriptive enough that it wont get confused finding the right spot through the list.

#print(columns.index('AlmaLinux OS  Foundation'))
#print(columns.index('Binary blobs'))

columns = columns[columns.index('AlmaLinux OS  Foundation'):columns.index('Binary blobs')] #NOTE: The first data entry in the looked at table has a double space between 'OS' and 'Foundation'
#print(columns)

"""
Next step is to organize the columns list into other lists based on their columns. To do this, we can count the number of columns on the table through the site, and organize based on the number of columns. 
This is done one column at a time. Each column is repeated after 11 entries. So, we will have to go through the list, add every 11th item to a list and repeat for the other columns.
"""

#columns[::11] #gets every 11th element of columns list. This would be the 'Founders' column
#columns[1:][::11] #gets every 11th element of columns list starting at index 1. This would be the 'Maintainer' column
#columns[2:][::11] #gets every 11th element of columns list starting at index 2. This would be the 'Initial_release_year' column

#ultimately a pattern is found and can be seen that the first index changes for each of the columns of the table. 

# to organize this the best, we will make a list of column names and sort by that.

column_names = ['Founder',
                'Maintainer',
                'Initial_Release_Year',
                'Current_Stable_Version',
                'Security_Updates',
                'Release_Date',
                'System_Distribution_Commitment',
                'Forked_From',
                'Target_Audience',
                'Cost',
                'Status']

# we are going to make a dictionary
data_dict = {'Distribution': distribution}
for idx, key in enumerate(column_names): #idx is the index of the list
    data_dict[key] = columns[idx:][::11]
    
# =============================================================================
#This section was made to test and see where there was an issue with the dictionary being entered into a dataframe. 
#The problem was solved when I would that the starting entry for the table has a double space.
#
# for i in data_dict:
#     print(f'data_dict[{i}] has: {len(data_dict[i])}')
# =============================================================================

#Now to add the dictionary to a dataframe so we can see it much easier.
df = pd.DataFrame(data = data_dict)

print(df.head())
print(df.tail())
# putting info into a SQLite database


try: #This will check to see if a file has been found or if it needs to be made
    dburi = 'file:{}?mode=rw'.format(pathname2url('linux_distro.db'))
    connection = sqlite3.connect(dburi, uri= True)
except sqlite3.OperationalError: #This is the case in which the file does not exist
    cursor = connection.cursor() #passes sql commands to the database. REQUIRED

    # creating database table
    cursor.execute('create table linux (Distribution, '+ ','.join(column_names) +')') #SQL command: create table NAME (column_headers names). the ''.join(column_names) is juse a fast way to not have to type a lot
    
    for i in range(len(df)):
        cursor.execute('insert into linux values (?,?,?,?,?,?,?,?,?,?,?,?)', df.iloc[i]) # ? is a placeholder with the column headers for the table, then the ',df.iloc[i]' is the info being added.
        
    connection.commit() #saves the table data into the database
    

connection.close() #closing connection


