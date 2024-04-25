from flask import Flask, request, jsonify, render_template
import pandas as pd
from scipy.stats import zscore

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('sales_data_sample.csv' , encoding='ISO-8859-1').ffill()

@app.route('/')
def home():
    return render_template('task5.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    month = request.args.get('month')
    
    # Filter data for the given month
    df_month = df[df['MONTH_ID'] == int(month)]
    
    # Calculate Z-scores for the given month
    df_month['SALES_ZSCORE'] = zscore(df_month['SALES'])
    
    # Find the product with the highest sales in that month
    recommendation = df_month[df_month['SALES'] == df_month['SALES'].max()]['PRODUCTLINE'].iloc[0]
    
    # Find anomalies in the sales data for the given month
    anomalies = df_month[df_month['SALES_ZSCORE'].abs() > 3]
    
    if anomalies.empty:
        anomalies_message = "No anomalies"
    else:
        anomalies_message = "Anomalies detected"
    
    return jsonify({'recommendation': recommendation, 'anomalies': anomalies_message})

if __name__ == '__main__':
    app.run(debug=True)
