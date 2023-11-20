import sqlite3

conn = sqlite3.connect('instance/test.db') 
c = conn.cursor()
c.execute('SELECT * FROM user')
for row in c:
    print(row)