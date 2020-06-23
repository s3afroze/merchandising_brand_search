from flask import Flask, url_for
from flask import render_template,request,redirect,url_for,Flask
from flask import send_from_directory
from algorithim.merchant_team import Merchandise_Optimization
from flask_sslify import SSLify
import os

app = Flask(__name__)
merchandise_optimization = Merchandise_Optimization()

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/search_ingredient', methods=['GET'])
def search_ingredient():	
	return render_template('form2.html')

@app.route('/search_ingredient_submitted', methods=['POST'])
def search_ingredient_submitted():
	upc = request.form['upc']
	propotion = int(request.form['propotion'])
	number_of_leads = int(request.form['number_of_leads'])

	merchandise_optimization.execute_open_food(upc=upc, propotion=propotion, number_of_leads=number_of_leads)

	return send_from_directory(directory='data', filename='df.csv', as_attachment=True)

@app.route('/search_database', methods=['GET'])
def search_database():
	return render_template('form1.html')

@app.route('/search_database_submitted', methods=['POST'])
def search_database_submitted():
	search_query = request.form['search_query']
	number_of_leads = int(request.form['number_of_leads'])
	merchandise_optimization.execute_fdc(search_query, number_of_leads)


	return send_from_directory(directory='data', filename='df.csv', as_attachment=True)


if __name__ == '__main__':
	
	port = int(os.environ.get("PORT", 5000))

	# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	# sslify = SSLify(app)
	app.run(host='0.0.0.0', port=port, debug=False)
    # app.run(debug=True)

