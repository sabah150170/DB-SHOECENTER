from flask import Flask, render_template, request
import urllib.parse as urlparse
import os
import psycopg2
from psycopg2 import Error



app = Flask(__name__)


def create_tables():
	commands=(
		""" CREATE TABLE IF NOT EXISTS CUSTOMER_INFO(
			CUSTOMER_ID SERIAL PRIMARY KEY, 
			NAME VARCHAR, 
			SURNAME VARCHAR, 
			E_MAIL VARCHAR UNIQUE NOT NULL, 
			PASSWORD VARCHAR NOT NULL, 
			BIRTH_DATE DATE, 
			PHONE_NUMBER VARCHAR NOT NULL      
		) """,

		""" CREATE TABLE IF NOT EXISTS CREDIT_CARD (
			CARD_ID SERIAL PRIMARY KEY,
			NAME VARCHAR NOT NULL,
			SURNAME VARCHAR NOT NULL,
			CARD_NO VARCHAR UNIQUE NOT NULL,
			CVV_CVC VARCHAR NOT NULL,
			EXPIRES VARCHAR NOT NULL
		) """,

		""" CREATE TABLE IF NOT EXISTS ADDRESS (
			ADDRESS_ID SERIAL PRIMARY KEY,
			CITY VARCHAR NOT NULL,
			DISTRICT VARCHAR NOT NULL,
			NEIGHBORHOOD VARCHAR NOT NULL,
			STREET VARCHAR NOT NULL,
			GATE_NO VARCHAR NOT NULL,
			ADDRESS_TYPE VARCHAR(1) NOT NULL
		) """,

		""" CREATE TABLE IF NOT EXISTS SHOE_INFO(
			SHOE_ID SERIAL PRIMARY KEY,
			PHOTO VARCHAR UNIQUE NOT NULL,
			RATE_SHOE INTEGER DEFAULT 0.0,
			BRAND VARCHAR NOT NULL,
			COLOR VARCHAR NOT NULL,
			FEATURE VARCHAR NOT NULL,
			GENDER VARCHAR NOT NULL
		) """,

		""" CREATE TABLE IF NOT EXISTS STORE_INFO(
			STORE_ID SERIAL PRIMARY KEY,
			ADDRESS_ID INTEGER UNIQUE NOT NULL,
			E_MAIL VARCHAR UNIQUE NOT NULL,
			RATE_STORE INTEGER DEFAULT 0.0,
			PASSWORD VARCHAR NOT NULL,
			PHONE_NUMBER VARCHAR NOT NULL, 
			FOREIGN KEY (ADDRESS_ID) REFERENCES ADDRESS(ADDRESS_ID)
		) """,

		""" CREATE TABLE IF NOT EXISTS STOCK_INFO(
			STOCK_ID SERIAL PRIMARY KEY,
			SHOE_ID INTEGER,
			STORE_ID INTEGER,
			DELIVER_TIME INTEGER NOT NULL,
			PRICE FLOAT NOT NULL,
			SIZE FLOAT NOT NULL,
			QUANTITY INTEGER NOT NULL,
			FOREIGN KEY (SHOE_ID) REFERENCES SHOE_INFO(SHOE_ID),
			FOREIGN KEY (STORE_ID) REFERENCES STORE_INFO(STORE_ID)
			) """,

		""" CREATE TABLE IF NOT EXISTS BASKET(
			BASKET_ID SERIAL PRIMARY KEY,
			STOCK_ID INTEGER NOT NULL,
			CUSTOMER_ID INTEGER NOT NULL,
			QUANTITY INTEGER NOT NULL,
			FOREIGN KEY (STOCK_ID) REFERENCES STOCK_INFO(STOCK_ID),
			FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER_INFO(CUSTOMER_ID)
		) """,

		""" CREATE TABLE IF NOT EXISTS SHOPPING_HISTORY(
			SHOPPING_ID SERIAL PRIMARY KEY,
			SHOE_ID INTEGER NOT NULL,
			STORE_ID INTEGER NOT NULL,
			CARD_ID INTEGER NOT NULL,
			CUSTOMER_ID INTEGER NOT NULL,
			ADDRESS_ID INTEGER NOT NULL,
			PRICE FLOAT NOT NULL,
			QUANTITY INTEGER NOT NULL,
			SIZE FLOAT NOT NULL,
			ORDER_DATE DATE NOT NULL,
			FOREIGN KEY (SHOE_ID) REFERENCES SHOE_INFO(SHOE_ID),
			FOREIGN KEY (STORE_ID) REFERENCES STORE_INFO(STORE_ID),
			FOREIGN KEY (CARD_ID) REFERENCES CREDIT_CARD(CARD_ID),
			FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER_INFO(CUSTOMER_ID),
			FOREIGN KEY (ADDRESS_ID) REFERENCES ADDRESS(ADDRESS_ID)
		) """
	)
	return commands


try:
	url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
	db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
	schema = "schema.sql"
	DB = psycopg2.connect(db)
 
	cursor=DB.cursor()

	print("PostgreSQL server information:")
	print(DB.get_dsn_parameters(), "\n")
	# Executing a SQL query
	cursor.execute("SELECT version();")
	# Fetch result
	record = cursor.fetchone()
	print("You are connected to - ", record, "\n")

	for command in create_tables():
		cursor.execute(command)

	DB.commit()

except (Exception, Error) as error:
	print("Error while connecting to PostgreSQL", error)
   

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/si_customer")
def sign_in_customer():
	return render_template("sign_in_customer.html")

@app.route("/si_company")
def sign_in_company():
	return render_template("sign_in_company.html")

@app.route("/su_customer")
def sign_up_customer():  
	return render_template("sign_up_customer.html")

@app.route("/su_company")
def sign_up_company():
	return render_template("sign_up_company.html")

@app.route("/success_cus", methods=['POST'])
def success_cus():
	if request.method=='POST':   
		name=request.form['inputName']
		surname=request.form['inputSurname']
		email=request.form['inputEmail']
		password=request.form['inputPassword']
		birthdate=request.form['inputBirthDate']
		phoneno=request.form['inputPhone']

		cursor.execute("SELECT COUNT(CUSTOMER_ID) FROM CUSTOMER_INFO WHERE (E_MAIL = %s)", (email,))
		quantity_email=cursor.fetchall()
		
		if quantity_email[0] == (1,) :
			return render_template("sign_up_customer.html", notice="Our database already has this e-mail!" )

		if name=='':
			name=None
		if surname=='':
			surname=None
		if birthdate=='':
			birthdate=None  

		cursor.execute("INSERT INTO CUSTOMER_INFO (NAME, SURNAME, E_MAIL, PASSWORD, BIRTH_DATE, PHONE_NUMBER) VALUES (%s, %s, %s, %s, %s, %s)", (name, surname, email, password, birthdate, phoneno))
		DB.commit()
		return render_template("sign_in_customer.html", notice="Registiration is success")

	else: return render_template("sign_up_customer.html")

@app.route("/success_com", methods=['POST'])
def success_com():
		if request.method=='POST':  
			city=request.form['inputCity'] 
			district=request.form['inputDistrict']
			neighborhood=request.form['inputNeighborhood']
			street=request.form['inputStreet']
			gate=request.form['inputNumber']
			email=request.form['inputEmail']
			password=request.form['inputPassword']
			phoneno=request.form['inputPhone']
			address_type='S'

			cursor.execute("SELECT COUNT(STORE_ID) FROM STORE_INFO WHERE (E_MAIL = %s)", (email,))
			quantity_email=cursor.fetchall()
			if quantity_email[0] == (1,) :
				return render_template("sign_up_company.html", notice="Our database already has this e-mail!" )

			cursor.execute("SELECT COUNT(ADDRESS_ID) FROM ADDRESS WHERE (CITY=%s and DISTRICT=%s and NEIGHBORHOOD=%s and STREET=%s and GATE_NO=%s and ADDRESS_TYPE='S')", (city, district, neighborhood, street, gate))
			quantity_address=cursor.fetchall()
			if quantity_address[0] ==(1,) :
				return render_template("sign_up_company.html", notice="A company resides at this address. If this address belongs to you, please contect us immediately!" )

			cursor.execute("INSERT INTO ADDRESS (CITY, DISTRICT, NEIGHBORHOOD, STREET, GATE_NO, ADDRESS_TYPE) VALUES (%s, %s, %s, %s, %s, %s)", (city, district, neighborhood, street, gate, address_type))
			DB.commit()

			cursor.execute("SELECT ADDRESS_ID FROM ADDRESS WHERE (CITY=%s and DISTRICT=%s and NEIGHBORHOOD=%s and STREET=%s and GATE_NO=%s and ADDRESS_TYPE='S')", (city, district, neighborhood, street, gate)) 
			address_id=cursor.fetchall()

			cursor.execute("INSERT INTO STORE_INFO (ADDRESS_ID, E_MAIL, PASSWORD,PHONE_NUMBER) VALUES (%s, %s, %s, %s)", (address_id[0][0], email, password, phoneno))
			DB.commit()

			return render_template("sign_in_company.html", notice="Registiration is success")

		else: return render_template("sign_up_company.html")

@app.route("/cus_wel", methods=['POST'])
def customer_welcome():
	if request.method=='POST':   
		email=request.form['inputEmail']
		password=request.form['inputPassword']

		cursor.execute("SELECT PASSWORD FROM CUSTOMER_INFO WHERE (E_MAIL = %s)", (email,))
		valid_password=cursor.fetchall()

		if len(valid_password)==0:          
			return render_template("sign_in_customer.html", notice="invalid email")

		else: 
			if(password==valid_password[0][0]):
				cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER_INFO WHERE (E_MAIL = %s)", (email,))
				c_id=cursor.fetchall()
				cursor.execute("SELECT NAME FROM CUSTOMER_INFO WHERE (E_MAIL = %s)", (email,))
				c_name=cursor.fetchall()

				return render_template("customer_welcome.html", customer_id=c_id[0][0], customer_name=c_name[0][0], welcome="Welcome,")
			else:
				return render_template("sign_in_customer.html", notice="invalid password")

	else: 
		return render_template("sign_in_customer.html")

@app.route("/com_wel", methods=['POST'])
def company_welcome():
	if request.method=='POST':   
		email=request.form['inputEmail']
		password=request.form['inputPassword']

		cursor.execute("SELECT PASSWORD FROM STORE_INFO WHERE (E_MAIL = %s)", (email,))
		valid_password=cursor.fetchall()

		if len(valid_password)==0:
			return render_template("sign_in_company.html", notice="invalid email")

		else: 
			if(password==valid_password[0][0]):
				cursor.execute("SELECT STORE_ID FROM STORE_INFO WHERE (E_MAIL = %s)", (email,))
				s_id=cursor.fetchall()

				return render_template("company_welcome.html", company_id=s_id[0][0])
				
			else:
				return render_template("sign_in_company.html", notice="invalid password")

	else: return render_template("sign_in_company.html")

@app.route("/cng_pro_cus", methods=['POST'])
def change_profile_customer():
	if request.method=='POST':
		cid=request.form['customer_id']
		cursor.execute("SELECT COUNT(E_MAIL) FROM CUSTOMER_INFO WHERE (CUSTOMER_ID = %s)", (cid,))
		test=cursor.fetchall()

		if test[0][0]==1:
			name=request.form['inputName']
			surname=request.form['inputSurname']
			password=request.form['inputPassword']
			birthdate=request.form['inputBirthDate']
			phoneno=request.form['inputPhone']

			if name != '':
				cursor.execute("UPDATE CUSTOMER_INFO SET NAME = %s WHERE (CUSTOMER_ID=%s)", (name,cid))
				DB.commit()
			if surname != '':
				cursor.execute("UPDATE CUSTOMER_INFO SET SURNAME = %s WHERE (CUSTOMER_ID=%s)", (surname,cid))
				DB.commit()
			if password != '':
				cursor.execute("UPDATE CUSTOMER_INFO SET PASSWORD = %s WHERE (CUSTOMER_ID=%s)", (password,cid))
				DB.commit()
			if birthdate != '':
				cursor.execute("UPDATE CUSTOMER_INFO SET BIRTH_DATE = %s WHERE (CUSTOMER_ID=%s)", (birthdate,cid))
				DB.commit()
			if phoneno != '':
				cursor.execute("UPDATE CUSTOMER_INFO SET PHONE_NUMBER = %s WHERE (CUSTOMER_ID=%s)", (phoneno,cid))
				DB.commit()
			return render_template("customer_welcome.html", notice="Succesful changed", customer_id=cid)

		else:
			return render_template("customer_welcome.html", notice="Something is going wrong, please contact us!", customer_id=cid)

@app.route("/my_bskt_cus", methods=['POST'])
def my_basket():
	if request.method=='POST':
		cid=request.form['customer_id']

		cursor.execute("SELECT COUNT(BASKET_ID) FROM BASKET WHERE (CUSTOMER_ID = %s)", (cid,))
		quantity_basket=cursor.fetchall()

		if quantity_basket[0][0] == 0:
			return render_template("customer_welcome.html", notice="No shoes in your basket!", customer_id=cid)

		else:
			cursor.execute("SELECT STOCK_ID,QUANTITY FROM BASKET WHERE (CUSTOMER_ID = %s)", (cid,))
			stock_and_quantity=cursor.fetchall()

@app.route("/logout")
def log_out():
	return render_template("index.html")

@app.route("/cng_pro_com", methods=['POST'])
def change_profile_company():
	if request.method=='POST':
		sid=request.form['company_id']
		cursor.execute("SELECT COUNT(E_MAIL) FROM STORE_INFO WHERE (STORE_ID = %s)", (sid,))
		test=cursor.fetchall()

		if test[0][0]==1:
			city=request.form['inputCity'] 
			district=request.form['inputDistrict']
			neighborhood=request.form['inputNeighborhood']
			street=request.form['inputStreet']
			gate=request.form['inputNumber']
			password=request.form['inputPassword']
			phoneno=request.form['inputPhone']
			
			if password != '':
				cursor.execute("UPDATE STORE_INFO SET PASSWORD = %s WHERE (STORE_ID=%s)", (password, sid))
				DB.commit()
			if phoneno != '':
				cursor.execute("UPDATE STORE_INFO SET PHONE_NUMBER = %s WHERE (STORE_ID=%s)", (phoneno,sid))
				DB.commit()

			cursor.execute("SELECT ADDRESS_ID FROM STORE_INFO WHERE (STORE_ID = %s)", (sid,))
			address=cursor.fetchall()
			address=address[0][0]

			if city != '':
				cursor.execute("UPDATE ADDRESS SET CITY = %s WHERE (ADDRESS_ID=%s)", (city,address))
				DB.commit()
			if district != '':
				cursor.execute("UPDATE ADDRESS SET DISTRICT = %s WHERE (ADDRESS_ID=%s)", (district,address))
				DB.commit()
			if neighborhood != '':
				cursor.execute("UPDATE ADDRESS SET NEIGHBORHOOD = %s WHERE (ADDRESS_ID=%s)", (neighborhood,address))
				DB.commit()
			if street != '':
				cursor.execute("UPDATE ADDRESS SET STREET = %s WHERE (ADDRESS_ID=%s)", (street,address))
				DB.commit()
			if gate != '':
				cursor.execute("UPDATE ADDRESS SET GATE_NO = %s WHERE (ADDRESS_ID=%s)", (gate,address))
				DB.commit()

			return render_template("company_welcome.html", notice="Succesful changed", company_id=sid)

		else:
			return render_template("company_welcome.html", notice="Something is going wrong, please contact us!", company_id=sid)

@app.route("/add_new_shoe", methods=['POST'])
def add_new_shoe():
	if request.method=='POST':
		photo=request.form['photo'] 
		gender=request.form['gender'] 
		feature=request.form['feature'] 
		brand=request.form['brand']
		color=request.form['color'] 
		sid=request.form['company_id']

		cursor.execute("SELECT SHOE_ID FROM SHOE_INFO WHERE (PHOTO = %s)", (photo,))
		quantity_photo=cursor.fetchall()

		if len(quantity_photo)==0:
			cursor.execute("INSERT INTO SHOE_INFO (PHOTO, BRAND, COLOR, FEATURE, GENDER) VALUES (%s, %s, %s, %s, %s)", (photo, brand, color, feature, gender))
			DB.commit()
			return render_template("/company_welcome.html", photo=photo, company_id=sid, notice="You can create your stock with shoes which are added by you")	
		
		else:
			return render_template("/company_welcome.html", photo=photo, company_id=sid, notice="Our database already has this shoe, you can continue to create your stock with this shoes" )

@app.route("/filter_shoes", methods=['POST'])
def filter_shoes():
	if request.method=='POST':
		sid=request.form['company_id']
		rate_shoe=request.form['rate_shoe']
		number_brand=int(request.form['n_brand'])
		number_feature=int(request.form['n_feature'])
		number_color=int(request.form['n_color'])
		number_gender=int(request.form['n_gender']) 

		check_b=0
		check_c=0
		check_g=0
		check_f=0

		brands=[0]
		brands=brands*number_brand
		current_number_brand=0

		features=[0]
		features=features*number_feature
		current_number_feature=0

		colors=[0]
		colors=colors*number_color
		current_number_color=0

		genders=[0]
		genders=genders*number_gender
		current_number_gender=0

		for i in range (0,number_brand):
			if "brand"+str(i) in request.form:
				check_b=1
				brands[current_number_brand]=request.form['brand'+str(i)]
				current_number_brand=(current_number_brand+1)
		for i in range (0,number_color):
			if "color"+str(i) in request.form:
				check_c=1
				colors[current_number_color]=request.form['color'+str(i)]
				current_number_color=(current_number_color+1)			
		for i in range (0,number_feature):
			if "feature"+str(i) in request.form:
				check_f=1
				features[current_number_feature]=request.form['feature'+str(i)]
				current_number_feature=(current_number_feature+1)
		for i in range (0,number_gender):
			if "gender"+str(i) in request.form:
				check_g=1
				genders[current_number_gender]=request.form['gender'+str(i)]
				current_number_gender=(current_number_gender+1)


		if brands[0]=="All" and colors[0]=="All" and features[0]=="All" and genders[0]=="All":
			cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
			all_rows=cursor.fetchall()
			if len(all_rows)==0:
				notice="No shoe is find according to your filters, please change your filter or do not select anything."
				return render_template("company_welcome.html", company_id=sid, notice=notice)
			else:
				notice:"Select shoes which will be included your stock"
				return render_template("company_welcome.html", company_id=sid, result=all_rows, notice=notice) 

		else:
			if brands[0]=="All" or check_b==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_brand=cursor.fetchall()
			elif brands[0]!="All":
				command_brand="BRAND = %s"
				for i in range(0,current_number_brand-1):
					command_brand+=" or BRAND = %s"
				for i in range(0,(number_brand-current_number_brand)):
					brands.pop()
				brands.reverse()
				brands.append(rate_shoe)
				brands.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_brand + "ORDER BY RATE_SHOE DESC", (brands))
				result_brand=cursor.fetchall()

			if colors[0]=="All" or check_c==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_color=cursor.fetchall()
			elif colors[0]!="All":
				command_color="COLOR = %s"
				for i in range(0,current_number_color-1):
					command_color+=" or COLOR = %s"
				for i in range(0,(number_color-current_number_color)):
					colors.pop()
				colors.reverse()
				colors.append(rate_shoe)
				colors.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_color + "ORDER BY RATE_SHOE DESC", (colors))
				result_color=cursor.fetchall()

			if features[0]=="All" or check_f==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_feature=cursor.fetchall()
			elif features[0]!="All":
				command_feature="FEATURE = %s"
				for i in range(0,current_number_feature-1):
					command_feature+=" or FEATURE = %s"
				for i in range(0,(number_feature-current_number_feature)):
					features.pop()
				features.reverse()
				features.append(rate_shoe)
				features.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_feature + "ORDER BY RATE_SHOE DESC", (features))
				result_feature=cursor.fetchall()

			if genders[0]=="All" or check_g==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_gender=cursor.fetchall()
			elif genders[0]!="All":
				command_gender="GENDER = %s"
				for i in range(0,current_number_gender-1):
					command_gender+=" or GENDER = %s"
				for i in range(0,(number_gender-current_number_gender)):
					genders.pop()
				genders.reverse()
				genders.append(rate_shoe)
				genders.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_gender + "ORDER BY RATE_SHOE DESC", (genders))
				result_gender=cursor.fetchall()

			size=len(result_color)
			base=result_color
			if size>len(result_gender):
				size=len(result_gender)
				base=result_gender
			if size>len(result_brand):
				size=len(result_brand)
				base=result_brand
			if size>len(result_feature):
				size=len(result_feature)
				base=result_feature

			result=[]
			index_size=0
			for i in range(0,size):
				for k in range(0,len(result_gender)):
					if(base[i][0]==result_gender[k][0]):
						for j in range(0, len(result_brand)):
							if(base[i][0]==result_brand[j][0]):
								for m in range(0,len(result_color)):
									if(base[i][0]==result_color[m][0]):
										for n in range(0, len(result_feature)):
											if(base[i][0]==result_feature[n][0]):
												print(base[i])
												result.append(base[i])
												index_size=(index_size+1)

			if index_size>0:
				notice="Select shoes which will be included your stock"
				return render_template("company_welcome.html", company_id=sid, result=result, size=index_size, notice=notice)
			else:
				notice="No shoe is found according to your filters, please change your filter or do not select anything."
				return render_template("company_welcome.html", company_id=sid, notice=notice)

@app.route("/add_stock", methods=['POST'])
def add_stock():
	if request.method=='POST':
		photo=request.form['photo'] 
		price=request.form['price'] 
		number=request.form['number'] 
		quantity=request.form['quantity']
		deliver=request.form['deliver']
		store_id=request.form['company_id'] 

		cursor.execute("SELECT SHOE_ID FROM SHOE_INFO WHERE (PHOTO = %s)", (photo,))
		shoe_id=cursor.fetchall()

		if len(shoe_id)==1:
			cursor.execute("SELECT COUNT(STOCK_ID) FROM STOCK_INFO WHERE (SHOE_ID= %s and STORE_ID=%s)", (shoe_id[0][0], store_id,))
			quantity_stock=cursor.fetchall()		

			if quantity_stock[0][0]==0:
				cursor.execute("INSERT INTO STOCK_INFO (SHOE_ID, STORE_ID, DELIVER_TIME, PRICE, SIZE, QUANTITY) VALUES (%s, %s, %s, %s, %s, %s)", (shoe_id[0][0], store_id, deliver, price, number, quantity))
				DB.commit()
				return render_template("/company_welcome.html", company_id=store_id, notice="Creation Successful")	
			else:
				return render_template("/company_welcome.html", company_id=store_id, notice="This shoes already in your stock, if you change your stock please click 'update menu' ")	
		
		else:
			return render_template("/company_welcome.html", company_id=store_id, notice="Something is going wrong, please contact us" )

@app.route("/select_shoes", methods=['POST'])
def select_shoes():
	if request.method=='POST':
		shoe=request.form['shoe_id'] 
		sid=request.form['company_id']

		cursor.execute("SELECT SHOE_ID FROM SHOE_INFO WHERE (SHOE_ID = %s)", (shoe,))
		quantity_shoe=cursor.fetchall()

		if len(quantity_shoe)!=1:
			return render_template("/company_welcome.html", company_id=sid, notice="Something is going wrong, please contact us")	
		
		else:
			cursor.execute("SELECT PHOTO FROM SHOE_INFO WHERE (SHOE_ID = %s)", (shoe,))
			photo=cursor.fetchall()
			return render_template("/company_welcome.html", photo=photo[0][0], company_id=sid, notice="You can create your stock with shoes which are selected by you" )

@app.route("/filter_stock", methods=['POST'])
def filter_stock():
	if request.method=='POST':
		sid=request.form['company_id']
		rate_shoe=int(request.form['rate_shoe'])
		number_brand=int(request.form['n_brand'])
		number_feature=int(request.form['n_feature'])
		number_color=int(request.form['n_color'])
		number_gender=int(request.form['n_gender']) 

		check_b=0
		check_c=0
		check_g=0
		check_f=0

		brands=[0]
		brands=brands*number_brand
		current_number_brand=0

		features=[0]
		features=features*number_feature
		current_number_feature=0

		colors=[0]
		colors=colors*number_color
		current_number_color=0

		genders=[0]
		genders=genders*number_gender
		current_number_gender=0

		for i in range (0,number_brand):
			if "brand"+str(i) in request.form:
				check_b=1
				brands[current_number_brand]=request.form['brand'+str(i)]
				current_number_brand=(current_number_brand+1)
		for i in range (0,number_color):
			if "color"+str(i) in request.form:
				check_c=1
				colors[current_number_color]=request.form['color'+str(i)]
				current_number_color=(current_number_color+1)			
		for i in range (0,number_feature):
			if "feature"+str(i) in request.form:
				check_f=1
				features[current_number_feature]=request.form['feature'+str(i)]
				current_number_feature=(current_number_feature+1)
		for i in range (0,number_gender):
			if "gender"+str(i) in request.form:
				check_g=1
				genders[current_number_gender]=request.form['gender'+str(i)]
				current_number_gender=(current_number_gender+1)


		if brands[0]=="All" and colors[0]=="All" and features[0]=="All" and genders[0]=="All":
			cursor.execute("SELECT * FROM SHOE_INFO  WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
			all_rows=cursor.fetchall()
			if len(all_rows)==0:
				notice="No shoe is find according to your filters, please change your filter or do not select anything."
				return render_template("company_welcome.html", company_id=sid, notice=notice)
			else:
				notice:"Select shoes which will be included your stock"
				return render_template("company_welcome.html", company_id=sid, result=all_rows, notice=notice) 

		else:
			if brands[0]=="All" or check_b==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_brand=cursor.fetchall()
			elif brands[0]!="All":
				command_brand="BRAND = %s"
				for i in range(0,current_number_brand-1):
					command_brand+=" or BRAND = %s"
				for i in range(0,(number_brand-current_number_brand)):
					brands.pop()
				brands.reverse()
				brands.append(rate_shoe)
				brands.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_brand + "ORDER BY RATE_SHOE DESC", (brands))
				result_brand=cursor.fetchall()

			if colors[0]=="All" or check_c==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_color=cursor.fetchall()
			elif colors[0]!="All":
				command_color="COLOR = %s"
				for i in range(0,current_number_color-1):
					command_color+=" or COLOR = %s"
				for i in range(0,(number_color-current_number_color)):
					colors.pop()
				colors.reverse()
				colors.append(rate_shoe)
				colors.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_color + "ORDER BY RATE_SHOE DESC", (colors))
				result_color=cursor.fetchall()

			if features[0]=="All" or check_f==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_feature=cursor.fetchall()
			elif features[0]!="All":
				command_feature="FEATURE = %s"
				for i in range(0,current_number_feature-1):
					command_feature+=" or FEATURE = %s"
				for i in range(0,(number_feature-current_number_feature)):
					features.pop()
				features.reverse()
				features.append(rate_shoe)
				features.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_feature + "ORDER BY RATE_SHOE DESC", (features))
				result_feature=cursor.fetchall()

			if genders[0]=="All" or check_g==0:
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) ORDER BY RATE_SHOE DESC",(rate_shoe,))
				result_gender=cursor.fetchall()
			elif genders[0]!="All":
				command_gender="GENDER = %s"
				for i in range(0,current_number_gender-1):
					command_gender+=" or GENDER = %s"
				for i in range(0,(number_gender-current_number_gender)):
					genders.pop()
				genders.reverse()
				genders.append(rate_shoe)
				genders.reverse()
				cursor.execute("SELECT * FROM SHOE_INFO WHERE(RATE_SHOE >= %s) and " + command_gender + "ORDER BY RATE_SHOE DESC", (genders))
				result_gender=cursor.fetchall()

			size=len(result_color)
			base=result_color
			if size>len(result_gender):
				size=len(result_gender)
				base=result_gender
			if size>len(result_brand):
				size=len(result_brand)
				base=result_brand
			if size>len(result_feature):
				size=len(result_feature)
				base=result_feature

			result=[]
			index_size=0
			for i in range(0,size):
				for k in range(0,len(result_gender)):
					if(base[i][0]==result_gender[k][0]):
						for j in range(0, len(result_brand)):
							if(base[i][0]==result_brand[j][0]):
								for m in range(0,len(result_color)):
									if(base[i][0]==result_color[m][0]):
										for n in range(0, len(result_feature)):
											if(base[i][0]==result_feature[n][0]):
												print(base[i])
												result.append(base[i][0])
												index_size=(index_size+1)

			if index_size>0:
				print("SHOE EXIST")
				deliver=(request.form['deliver'])
				rate_store=(request.form['rate_store'])
				price_lower=(request.form['price_lower'])
				price_upper=(request.form['price_upper'])
				size=(request.form['size'])
				quantity=(request.form['quantity'])

				command="SHOE_ID = %s"
				for i in range(0,index_size-1):
					command+=" or SHOE_ID = %s"

				result.append(price_upper)
				result.append(price_lower)
				result.append(deliver)
				result.append(quantity)
				result.append(rate_store)

				if int(size)==0:
					cursor.execute("SELECT * FROM (SELECT * FROM (SELECT * FROM SHOE_INFO WHERE " + command + ") AS NW1 INNER JOIN (SELECT * FROM STOCK_INFO WHERE(PRICE <=%s AND PRICE>=%s AND DELIVER_TIME<=%s AND QUANTITY>=%s)) AS NT2 USING(SHOE_ID)) AS NW2 INNER JOIN (SELECT * FROM STORE_INFO WHERE (RATE_STORE>=%s)) AS NW3 USING(STORE_ID)", (result))
					result=cursor.fetchall()

				else:
					result.remove(rate_store)
					result.append(size)
					result.append(rate_store)
					cursor.execute("SELECT * FROM (SELECT * FROM (SELECT * FROM SHOE_INFO WHERE " + command + ") AS NW1 INNER JOIN (SELECT * FROM STOCK_INFO WHERE(PRICE <=%s AND PRICE>=%s AND DELIVER_TIME<=%s AND QUANTITY>=%s AND SIZE=%s)) AS NT2 USING(SHOE_ID)) AS NW2 INNER JOIN (SELECT * FROM STORE_INFO WHERE (RATE_STORE>=%s)) AS NW3 USING(STORE_ID)", (result))

					#cursor.execute("SELECT * FROM (SELECT * FROM STOCK_INFO WHERE " + command +"INTERSECT SELECT * FROM STOCK_INFO WHERE(PRICE <=%s AND PRICE>=%s AND DELIVER_TIME<=%s AND QUANTITY>=%s AND SIZE=%s)) AS NT1 INNER JOIN (SELECT * FROM STORE_INFO WHERE (RATE_STORE>=%s)) AS NW2 USING(STORE_ID)", (result))
					result=cursor.fetchall()
					
				if(len(result))==0:
					return render_template("company_welcome.html", company_id=sid, notice="No stock is found according to your filters, please change your filter or do not select anything.")
				else:
					return render_template("company_welcome.html", company_id=sid, result2=result, size2=len(result))

			else:
				notice="No stock is found according to your filters, please change your filter or do not select anything."
				return render_template("company_welcome.html", company_id=sid, notice=notice)


@app.route("/update_stock", methods=['POST'])
def update_stock():
	if request.method=='POST':
		sid=request.form['company_id']
		stock_id=request.form['stock_id']
		price=request.form['price']
		number=request.form['number']
		quantity=int(request.form['quantity'])
		deliver=request.form['deliver']

		if quantity==0:
			cursor.execute("DELETE FROM BASKET WHERE(STOCK_ID=%s)", (stock_id,))
			DB.commit()
			cursor.execute("DELETE FROM STOCK_INFO WHERE(STOCK_ID=%s)", (stock_id,))
			DB.commit()
			return render_template("company_welcome.html", company_id=sid, notice="Delete Success")
		else:
			cursor.execute("UPDATE STOCK_INFO SET PRICE =%s, SIZE=%s, QUANTITY=%s, DELIVER_TIME=%s WHERE STOCK_ID=%s",(price, number, quantity, deliver, stock_id))
			DB.commit()
			return render_template("company_welcome.html", company_id=sid, notice="Update Success")


@app.route("/my_stock", methods=['POST'])
def my_stock():
	if request.method=='POST':
		sid=request.form['company_id']
		
		cursor.execute("SELECT * FROM (SELECT * FROM STOCK_INFO WHERE(STORE_ID=%s) GROUP BY DELIVER_TIME,STOCK_INFO.STOCK_ID ORDER BY QUANTITY DESC) AS NW1 INNER JOIN (SELECT * FROM SHOE_INFO) AS NW2 USING(SHOE_ID)",(sid,))
		result=cursor.fetchall()

		cursor.execute("SELECT RATE_STORE FROM STORE_INFO WHERE(STORE_ID=%s)",(sid,))
		rate=cursor.fetchall()

		notice="Your rate is " + str(rate[0][0])
		if len(result)==0:		
			notice+="  \n No stock "		
			return render_template("company_welcome.html", company_id=sid, notice=notice)

		else:			
			return render_template("company_welcome.html", company_id=sid, notice=notice, result3=result, size=len(result))
			

   
app.config["DEBUG"]=True



if __name__=="__main__":
	app.run()




