#import python packages
import random
import sqlite3

# create connection
conn = sqlite3.connect('card.s3db')
#create a table for storing data
create_table = """CREATE TABLE IF NOT EXISTS card(id INTEGER NOT NULL PRIMARY KEY, number TEXT NOT NULL, pin TEXT, balance INTEGER);"""
c = conn.cursor()
c.execute(create_table)
conn.commit()

# function to define a client i.e card PIN and ID etc
class Client:
    def __init__(self, card_id, card_pin, balance, log_flag=False):
        self.card_id = card_id
        self.card_pin = card_pin
        self.balance = balance
        self.log_flag = log_flag


class Bank:
    IIN = '400000'
    checksum = '8'

    def __init__(self):
        self._database = dict()

    def create_account(self):
        flag = True
        while flag:
            # generate new card
            gen_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            print(gen_id)
            card_number = self.IIN + gen_id
            gen_list = [int(d) for d in str(card_number)]
            gen_even = gen_list[1::2]
            gen_odd = gen_list[0::2]
            gen_odd_new = []
            sum_of_digits = 0
            # luhn card checks and generate last digit (checksum)
            for digits in gen_odd:
                if (int(digits) * 2) > 9:
                    gen_odd_new.append((int(digits) * 2) - 9)
                else:
                    gen_odd_new.append((int(digits) * 2))
            sum_all = gen_odd_new + gen_even
            for ele in range(0, len(sum_all)):
                sum_of_digits = sum_of_digits + sum_all[ele]
            if sum_of_digits % 10 == 0:
                checksum = 0
            else:
                checksum = (10 - (sum_of_digits % 10))
            card_number = card_number + str(checksum)
            card_pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            # update database with generated card number and card pin
            if card_number not in c.execute("SELECT * FROM card"):
                flag = False
                params = [card_number, card_pin, 0]
                c.execute("INSERT INTO card VALUES(NULL, ?, ?, ?)", params)
                conn.commit()
                print(f'\nYour card has been created\nYour card number:\n{card_number}\nYour card PIN:\n{card_pin}\n')
                self.run_session()
            else:
                self.run_session()
# determine if login is successful or not
    def login(self):
        card_id = input('Enter your card number:\n')
        card_pin = input('Enter your PIN:\n')
        c.execute("SELECT * FROM card")
        card_details = c.fetchall()
        if [cus_num for cus_num in card_details if card_id in cus_num]:
            if [cus_pin for cus_pin in card_details if card_pin in cus_pin]:
                if card_pin == (c.execute("SELECT pin FROM card WHERE number =?", (card_id,)).fetchall())[0][0]:
                    print('You have successfully logged in!\n')
                    self.transactions(ids=card_id)
                else:
                    print("Wrong card number or PIN!")
                    self.transactions(ids=card_id)
            else:
                print('Wrong card number or PIN!\n')
                self.run_session()
        else:
            print('Wrong card number or PIN!\n')
            self.run_session()
# defines transaction to be made and effect changes
    def transactions(self, ids):
        para = int(ids)
        self_input = int(
            input('1. Balance \n2. Add income \n3. Do transfer \n4. close account \n5. Log out\n0. Exit\n'))
        if self_input == 1:
            my_balance = c.execute("SELECT balance FROM card WHERE number =?", (para,)).fetchall()
            print(my_balance)
            print('Balance {} \n'.format(str(my_balance[0][0])))
            self.transactions(ids)
        elif self_input == 2:
            income = input('Enter income!\n')
            c.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, para,)).fetchall()
            conn.commit()
            print('Income was added! \n')
            self.transactions(ids)
        elif self_input == 3:
            print('Transfer')
            all_card = c.execute("SELECT number FROM card").fetchall()
            cur_card = input("Enter card number: \n")
            to_list = [int(d) for d in str(cur_card)]
            last_digit = to_list[-1]
            first_digit = to_list[0]
            second_to_list = to_list[0:15]
            the_even = second_to_list[1::2]
            the_odd = second_to_list[0::2]
            to_odd_new = []
            sum_digits = 0
            for digits in the_odd:
                if (int(digits) * 2) > 9:
                    to_odd_new.append((int(digits) * 2) - 9)
                else:
                    to_odd_new.append((int(digits) * 2))
            sum_all = to_odd_new + the_even
            for ele in range(0, len(sum_all)):
                sum_digits = sum_digits + sum_all[ele]
            checksums = sum_digits % 10
            if cur_card == para:
                print("You can't transfer money to the same account!")
                self.transactions(ids)
            elif [n_num for n_num in all_card if cur_card in n_num]:
                transfer = int(input("Enter how much money you want to transfer: \n"))
                avail_balance = c.execute("SELECT balance FROM card WHERE number =?", (para,)).fetchall()
                ava_balance = int(avail_balance[0][0])
                if ava_balance > transfer:
                    c.execute("UPDATE card SET balance = (balance - ?) WHERE number = ?", (transfer, para,)).fetchall()
                    conn.commit()
                    c.execute("UPDATE card SET balance = (balance + ?) WHERE number = ?",
                              (transfer, cur_card)).fetchall()
                    conn.commit()
                    print('Success! \n')
                    self.transactions(ids)
                else:
                    print("Not enough money!")
                    self.transactions(ids)
            elif (first_digit == 4 or first_digit == 3 or first_digit == 5) and checksums == 0 and last_digit == 0:
                print("Such a card does not exist. \n")
                self.transactions(ids)
            elif (first_digit == 4 or first_digit == 3 or first_digit == 5) and checksums != 0 and (10 - checksums) == last_digit:
                print("Such a card does not exist. \n")
                self.transactions(ids)
            else:
                print("Probably you made a mistake in the number. Please try again! \n")
                self.transactions(ids)
        elif self_input == 4:
            c.execute("DELETE FROM card WHERE number = ?", (para,))
            conn.commit()
            print("The account has been closed!\n")
            self.run_session()
        elif self_input == 5:
            print("You have successfully log out! \n")
            self.run_session()
        elif self_input == 0:
            print('Bye!\n')
            exit()
        else:
            print("Check your input! \n")
            self.transactions(ids)

    def menu(self, client=False):
        if client:
            cl_input = input('1. Balance \n2. Add income \n3. Do transfer \n4. close account \n5. Log out\n0. Exit\n')
        else:
            cl_input = input('1. Create an account\n2. Log into account\n0. Exit\n')
        return cl_input

    def run_session(self, client=False):
        cl_input = self.menu(client)
        if cl_input == '1' and not client:
            self.create_account()
        elif cl_input == '2' and not client:
            self.login()
        else:
            print('Bye')
            conn.close()
            exit()


bank = Bank()
bank.run_session()
