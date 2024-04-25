from flask import Flask, request, jsonify, render_template
import pandas as pd
import gender_guesser.detector as gender

app = Flask(__name__)

# Load your CSV data
data = pd.read_csv('sales_data_sample.csv', encoding='ISO-8859-1').ffill()

# Initialize gender detector
d = gender.Detector()

@app.route('/')
def home():
    return render_template('task2.html')

@app.route('/order', methods=['GET'])
def get_gender():
    order_id = request.args.get('order_id', type=int)
    if order_id is not None:
        order = data[data['ORDERNUMBER'] == order_id]
        if not order.empty:
            first_name = order['CONTACTFIRSTNAME'].values[0]
            # Use the gender_guesser package to predict gender
            gender = d.get_gender(first_name)
            return jsonify({"gender": gender})
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
