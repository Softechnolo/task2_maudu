from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('sales_data_sample.csv', encoding='ISO-8859-1').ffill()

@app.route('/')
def home():
    return render_template('task5.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    month = request.args.get('month')
    
    # Filter data for the given month
    df_month = df[df['MONTH_ID'] == int(month)]
    
    # Calculate IQR for the given month
    Q1 = df_month['SALES'].quantile(0.25)
    Q3 = df_month['SALES'].quantile(0.75)
    IQR = Q3 - Q1
    
    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Find anomalies in the sales data for the given month
    anomalies = df_month[(df_month['SALES'] < lower_bound) | (df_month['SALES'] > upper_bound)]
    
    # Find the product with the highest sales in that month (excluding anomalies)
    df_month_no_anomalies = df_month[(df_month['SALES'] >= lower_bound) & (df_month['SALES'] <= upper_bound)]
    recommendation = df_month_no_anomalies[df_month_no_anomalies['SALES'] == df_month_no_anomalies['SALES'].max()]['PRODUCTLINE'].iloc[0]
    
    if anomalies.empty:
        anomalies_message = "No anomalies"
    else:
        anomalies_message = "Anomalies detected"
    
    return jsonify({'recommendation': recommendation, 'anomalies': anomalies_message})

if __name__ == '__main__':
    app.run(debug=True)
