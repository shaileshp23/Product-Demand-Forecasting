from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_mail import Mail, Message
from random import randrange
import pickle

# Load the original CSV file
df = pd.read_csv("product.csv")

app = Flask(__name__)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.secret_key = "abcdef"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shailesh@12'
app.config['MYSQL_DB'] = 'shopping'
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] =  587
app.config["MAIL_USERNAME"] = "shopspot.1603@gmail.com"
app.config["MAIL_PASSWORD"] = "icir oiix pfqw qybd"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

model = pickle.load(open('product.pkl', 'rb'))

mail = Mail(app)
mysql = MySQL(app)
@app.route('/')

@app.route('/signin')
def home():
    return render_template('signin.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/signin',methods=['GET', 'POST'])
def signin():
    mesage = ''
    if request.method == 'POST' and 'emailid' in request.form and 'passwd' in request.form:
        emailid = request.form['emailid']
        passwd = request.form['passwd']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * from register where emailid = %s and password = %s',(emailid, passwd))
        user = cursor.fetchone()
        
        if user:
            session['loggedin'] = True
            session['rid'] = user['rid']
            session['fname'] = user['fname']
            session['lname'] = user['lname']
            session['phone'] = user['phone']
            session['emailid'] = user['emailid']
            session['password'] = user['password']
            mesage = 'Logged in successfully !'

            #return render_template('index.html', mesage = mesage)
            if passwd.isdigit():
                mesage = 'You need to update your password!'
                return render_template('changepassword.html',mesage = mesage)
            else:
                return render_template('index.html', mesage = mesage)
        else:
            mesage = 'Please enter correct emailid or password !'

    return render_template('signin.html', mesage = mesage)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('cid', None)
    session.pop('emailid', None)
    return redirect(url_for('signin'))
 

@app.route('/signup',methods=['GET','POST'])
def signup():
    mesage=''
 
    if request.method == 'POST' and 'fname' in request.form and 'lname' in request.form and 'phone' in request.form and 'emailid' in request.form:
  
        n = request.form['fname']
        m = request.form['lname']
        t = request.form['phone']
        d = request.form['emailid']
        g = ""
        text = "0123456789"
        for i in range(8):
            g = g + text[randrange(len(text))]
        print(g)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM register WHERE emailid = % s', (d,))
        
        result = cursor.fetchone()
        if result:
            mesage = 'Email id already exists !'
        else:
            mesage = Message("Welcome to ShopSpot!", sender = "shopspot.1603@gmail.com", recipients = [d])
            mesage.body = "Greetings from ShopSpot! Your password is " + str(g)
            mail.send(mesage)
            cursor.execute('INSERT INTO register VALUES (NULL, % s, % s, % s, % s, %s)', (n, m, t, d, g,))
            mysql.connection.commit()
            mesage = 'Password has been mailed to you'
            return render_template('signin.html', mesage = mesage)
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'

    return render_template('signup.html', mesage = mesage)

@app.route('/changepassword',methods=['GET','POST'])
def changepassword():
    mesage = ''
    if request.method == 'POST' and 'emailid' in request.form and 'passwd' in request.form and 'repasswd' in request.form:
        emailid = request.form['emailid']
        passwd = request.form['passwd']
        repasswd = request.form['repasswd']
        if passwd == repasswd:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM register WHERE emailid = %s', (emailid,))
            res = cursor.fetchone()

            if res:
                cursor.execute('UPDATE register SET password=%s WHERE emailid=%s', (passwd, emailid))
                mysql.connection.commit()  
                mesage = 'Password updated successfully!'
                return render_template('index.html', mesage=mesage)
            else:
                mesage = 'Error updating! Please try again!'
        else:
            mesage = 'Passwords do not match!'
    return render_template('changepassword.html', mesage=mesage)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/analysis')
def analysis():
    return render_template("churn.html")

@app.route('/predict', methods=['POST'])
def predictform():
    if request.method == 'POST':
        try:
            product_stats = df.groupby('Product')['Quantity'].agg(['mean', 'median', 'std']).reset_index()

            new_product_id = int(request.form['product_id'])

            product_data = product_stats[product_stats['Product'] == new_product_id]

            if not product_data.empty:
                product_stats = product_data[['mean', 'median', 'std']].iloc[0]

                predicted_percentage = model.predict([product_stats])
            else:
                predicted_percentage = 0

            return render_template('result.html', prediction=predicted_percentage[0])

        except Exception as e:
            return render_template('result.html', error_message=str(e))

    return render_template('result.html', error_message="Invalid request")

@app.route('/products')
def products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select * from product')
    pr = cursor.fetchall()
    return render_template('productupdate.html', pr=pr)


@app.route('/productupdate', methods=['GET','POST'])
def productupdate():
    if request.method == 'POST' and 'productid' in request.form and 'productname' in request.form and 'quantity' in request.form:
        productid = request.form['productid']    
        productname = request.form['productname']
        quantity = request.form['quantity']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('UPDATE product SET productname=%s , quantity=%s WHERE productid=%s',(productname, quantity, productid))
            mysql.connection.commit()
            msg = 'Updated Successfully !'
            return render_template('productupdate.html', msg = msg)
        except Exception as e:
            msg='Error updating error'
        render_template('productupdate.html', msg = msg)
    else:
        msg = 'Error'
        return render_template('productupdate.html', msg = msg)

@app.route('/productdelete/<string:id>', methods=['Get','POST'])
def productdelete(id):
    flash('Record has been Deleted')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('delete from product where productid=%s',(id,))
    mysql.connection.commit()
    return render_template('productupdate.html')

@app.route('/contactus', methods=['GET','POST'])
def contactus():
    return render_template('contactus.html')

if __name__ == '__main__':
    app.run(debug=True)
