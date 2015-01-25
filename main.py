import pandas as pd
from flask import Flask, request, url_for, render_template, redirect, flash, jsonify, abort
from datetime import datetime
from random import randint

app = Flask(__name__)
df = pd.read_csv('./data/merged_data.csv')

@app.route('/')
def show_index():
    return render_template('index.html')

@app.route('/map')
def show_map():
    return render_template('colored_slow_map.html')

@app.route('/calls')
def calls():
    return render_template('calls.html')

@app.route('/add_from_map')
def add_from_map():
	address = df.Street.ix[randint(0,len(df)), :]
	r = df[df.Street == address]
	r['Event Date/Time'] = r['Event Date/Time'].map(lambda x: datetime.strptime(x, r'%m/%d/%y %H:%M'))
	r.sort('Event Date/Time', ascending=False, inplace=True)
	print r
	s = zip(r['Event Date/Time'].tolist(), r.Event.tolist(), r['Event Nature'].tolist())
	return render_template('AddressExists.html', p='{:.0f}'.format(r.P.max() * 100), name='Al Pacino', dates_records_details=s)

@app.route('/add', methods=['POST'])
def add_entry():
	address = request.form['Address'].upper()
	r = df[df.Street == address]
	r['Event Date/Time'] = r['Event Date/Time'].map(lambda x: datetime.strptime(x, r'%m/%d/%y %H:%M'))
	r.sort('Event Date/Time', ascending=False, inplace=True)
	print r
	s = zip(r['Event Date/Time'].tolist(), r.Event.tolist(), r['Event Nature'].tolist())
	return render_template('AddressExists.html', p='{:.0f}'.format(r.P.max() * 100), name='Al Pacino', dates_records_details=s)

@app.route('/api/get_all', methods=['GET'])
def get_all():
	to_display = df[['Street','Event','Event Date/Time', 'Event Nature', 'P','yp']].to_json(orient='records')
	return jsonify({'get_all': to_display})

@app.route('/api/get_profile/<string:address>', methods=['GET'])
def get_profile(address):
	"""Input address, get all the events as JSON. One event consists of arrest/call, date, and p. P pertains to the address, which is the unique ID here."""
	address = address.upper()

	if address not in df.Street.values:
		abort(404)
	else:
		temp_dict = {}
		temp_table = df[df.Street == address].ix[:,1:]

		temp_dict['probability'] = temp_table.P.max()
		temp_dict['incidents'] = temp_table.ix[:,:-1].to_dict('records')

		return jsonify({'get_profile': temp_dict})

# For running Flask locally
if __name__ == '__main__':
    app.run(debug=True)