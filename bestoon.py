#!/usr/bin/python
import ConfigParser
import hashlib
from sys import exit
from requests import post , get
from getpass import getpass
from simplecrypt import encrypt , decrypt
from os.path import exists

class Config():
	'Class For Working With Config Files'
	def __init__(self):
		self.config = ConfigParser.RawConfigParser()
	def write_config(self,**kwargs):
		self.config.add_section('Section1')
		for var in kwargs:
			self.config.set('Section1',var,kwargs[var])
		with open('config.cfg','wb') as configfile:
			self.config.write(configfile)
		return True
	#---------------------------------------------------
	def read_config(self,*args):
		context = {}
		if exists('config.cfg'):
			self.config.read('config.cfg')
			for arg in args:
				if arg == 'token':
					context['token'] = self.config.get('Section1',arg)
				elif arg == 'initialized':
					context['initialized'] = self.config.get('Section1',arg)
				elif arg == 'password':
					context['password'] = self.config.get('Section1',arg)
				return context	

def initialize():
	if exists('config.cfg'):
		c = Config()
		is_init = c.read_config('initialized')['initialized']
		if is_init == 'true':
			return False # It means that Initialiaztion has been done before!
	else:
		c = Config()
		print('Hello And Welcome To Pytoon!')
		print('Follow Steps Below To Get Started With Pytoon!')
		print('==============================================')
		print('Please Provide A Password , You Will Need It When You Want To Submit Anything!')
		print('We Use This Password To Encrypt Your Token , So Choose Wisely!')
		Password1 = getpass('Enter Your Password: ')
		Password2 = getpass('Enter Your Password Again: ')
		while Password1 != Password2:
			print('Your Passwords Do Not Match , Try Again!')
			Password1 = getpass('Enter Your Password: ')
			Password2 = getpass('Enter Your Password Again: ')
		print('Your Password Saved Successfully!')
		print('============================')
		print('OK , Last Step.....Token!')
		print("If You Don't Have One,Please Register At http://bestoon.ir/accounts/register")
		token = raw_input('Please Provide Your Token: ')
		while token == '' or len(token) < 48:
			print('Invalid Token! Try Again!')
			token = raw_input('Please Provide Your Token: ')
		print('Encrypting Your Token....')
		Token = encrypt(Password2,token)
		Initialized = 'true' # Initialiaztion won't happen again if it's set to True
		Password = hashlib.sha256(Password2).hexdigest()
		s = c.write_config(token=Token,initialized=Initialized,password=Password) # Writing Info
		if s is True:
			print('Initialiaztion Completed Successfully!')
		return True	
		
def prompt():
	command = raw_input('Pytoon>> ')
	if command.lower() == 'set income':
		income()
	elif command.lower() == 'set expense':
		expense()
	elif command.lower() == 'show status':
		generalstat()	
	elif command.lower() == 'help':
		show_help()	
	elif command.lower() == 'exit':
		exit(0)				

def show_help():
	print('You Can Interact With Pytoon Using Following Commands:')
	print('set income ==> Submits An Income')
	print('set expense ==> Submits An Expense')
	print('show status ==> Shows A Generalstat')
	print('exit ==> Bye Bye!')

def income():
	c = Config()
	password = getpass('Enter Your Password To Submit An Income: ')
	p = c.read_config('password')['password']
	while hashlib.sha256(password).hexdigest() != p:
		print('Invalid Password! , Try Again!')
		password = getpass('Enter Your Password To Submit An Income: ')
	token = c.read_config('token')['token']
	token = decrypt(password,token).strip().rstrip()
	amount = raw_input('Enter The Amount Of The Income: ')
	text = raw_input('Enter The Text Of The Income: ')
	response = post('http://bestoon.ir/submit/income/',data={'amount':amount,'text':text,'token':token})
	response = response.json()
	if response['status'] == 'ok':
		print('Income Has Submited Successfully!')
	else:
		print('Error While Submitting The Income')

def expense():
	c = Config()
	password = getpass('Enter Your Password To Submit An Expense: ')
	p = c.read_config('password')['password']
	while hashlib.sha256(password).hexdigest() != p:
		print('Invalid Password! , Try Again!')
		password = getpass('Enter Your Password To Submit An Income: ')
	token = c.read_config('token')['token']
	token = decrypt(password,token).strip().rstrip()
	amount = raw_input('Enter The Amount Of The Expense: ')
	text = raw_input('Enter The Text Of The Expense: ')
	response = post('http://bestoon.ir/submit/expense/',data={'amount':amount,'text':text,'token':token})
	response = response.json()
	if response['status'] == 'ok':
		print('Expense Has Submited Successfully!')
	else:
		print('Error While Submitting The Expense')


def generalstat():
	c = Config()
	password = getpass('Enter Your Password To View Status: ')
	p = c.read_config('password')['password']
	while hashlib.sha256(password).hexdigest() != p:
		print('Invalid Password! , Try Again!')
		password = getpass('Enter Your Password To Submit An Income: ')
	token = c.read_config('token')['token']
	token = decrypt(password,token).strip().rstrip()
	response = post('http://bestoon.ir/q/generalstat/',data={'token':token})
	response = response.json()
	expense_amount = response['expense']['amount__sum']
	expense_count = response['expense']['amount__count']
	income_amount = response['income']['amount__sum']
	income_count = response['income']['amount__count']
	if expense_amount is None:
		print("You Haven't Submitted Any Expense Yet...")
	elif expense_amount is not None:
		print('The Sum Of Your Expenses: %d' % expense_amount)
		print('The Count Of Your Expenses: %d' % expense_count)	
	if income_amount is None:
		print("You Haven't Submitted Any Income Yet...")
	elif income_amount is not None:
		print('The Sum Of Your Incomes: %d' % income_amount)
		print('The Count Of Your Incomes: %d' % income_count)	

i = initialize()		
if i == False:
	prompt()		
	while True:
		prompt()
elif i == True:		
	prompt()		
	while True:
		prompt()		