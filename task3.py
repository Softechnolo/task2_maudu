from flask import Flask, request, jsonify, render_template
import pandas as pd
import nltk

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Create the Flask app
app = Flask(__name__)

# Import the CSV data into a pandas DataFrame
# Handle missing values using forward fill method
df = pd.read_csv('sales_data_sample.csv', encoding='ISO-8859-1').ffill()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    # Get the query from the request
    query = request.form['query'].lower()  # Convert to lowercase for case-insensitive processing

    # Tokenize the query using NLTK
    tokens = nltk.word_tokenize(query)

    # Use POS tagging (optional) to identify word types (e.g., noun, verb)
    pos_tags = nltk.pos_tag(tokens)

    # keywords based on the logic
    keywords = set(tokens)
    product_keywords = {'product', 'item', 'sell'}
    city_keywords = {'city', 'location'}
    sales_analysis_keywords = {'performance', 'analysis', 'sales'}
    customer_keywords = {'customer', 'client'}
    order_keywords = {'order', 'purchase'}
    demand_keywords = {'demand', 'trend', 'popular'}
    region_keywords = {'region', 'state', 'area'}
    sales_trend_keywords = {'trend', 'increase', 'change'}

    # Analysing the query based on identified keywords

    if product_keywords.intersection(keywords):
        response = df.groupby('PRODUCTCODE')['SALES'].sum().idxmax()
    elif city_keywords.intersection(keywords):
        response = df.groupby('CITY')['SALES'].sum().idxmax()
    elif sales_analysis_keywords.issubset(keywords):
        # Implement filtering  (assuming 'QTR_ID', 'YEAR_ID', etc. exist)
        filtered = df[(df['QTR_ID'] == 4) & (df['YEAR_ID'] == 2003) & (df['STATUS'] == 'Shipped') & (df['QUANTITYORDERED'] >= 40)]
        response = filtered.groupby('PRODUCTCODE')['SALES'].sum().nlargest(5).to_dict()
    elif customer_keywords.intersection(keywords) and order_keywords.intersection(keywords):
        # Implement filtering similar (assuming 'YEAR_ID', 'SALES', 'COUNTRY' exist)
        filtered = df[(df['YEAR_ID'] == 2003) & (df['SALES'] > 5000) & (df['COUNTRY'].isin(['USA', 'France']))]
        top_customers = filtered['CUSTOMERNAME'].value_counts()
        top_customers = top_customers[top_customers > 3]
        response = top_customers.to_dict()
    elif demand_keywords.intersection(keywords):
        # Implement filtering similar to spaCy version (assuming 'YEAR_ID', 'SALES', 'PRICEEACH', 'MONTH_ID' exist)
        filtered = df[(df['YEAR_ID'] == 2003) & (df['SALES'] > 100000) & (df['PRICEEACH'] > 80)]
        average_quantity = filtered.groupby(df['MONTH_ID'])['QUANTITYORDERED'].mean()
        top_month = average_quantity.idxmax()
        response = top_month
    elif region_keywords.intersection(keywords) and sales_keywords.intersection(keywords):
        # Filter data based on year, sales status, minimum order quantity, and specific states
        filtered_data = df[
            (df['YEAR_ID'] == 2003) &  # Filter for specific year (adjust as needed)
            (df['STATUS'] == 'Shipped') &  # Filter for shipped orders
            (df['QUANTITYORDERED'] >= 20) &  # Filter for orders with minimum quantity
            (df['STATE'].isin(['CA', 'NY']))  # Filter for specific states (adjust as needed)
        ]
        # Analyze sales performance by region (assuming 'STATE' and 'SALES' columns exist)
        average_sales_by_region = filtered_data.groupby('STATE')['SALES'].mean().to_dict()

        response = average_sales_by_region  # Update response with the result
    elif sales_trend_keywords.intersection(keywords):
        # Implement filtering similar to spaCy version (assuming 'YEAR_ID', 'PRICEEACH', 'MONTH_ID', 'PRODUCTLINE' exist)
        filtered = df[(df['YEAR_ID'] == 2003) & (df['PRICEEACH'] < 100)]
        monthly_sales = filtered.groupby([df['MONTH_ID'], 'PRODUCTLINE'])['SALES'].sum()
        monthly_sales_pct_change = monthly_sales.groupby(level=1).pct_change()
        result = monthly_sales_pct_change[monthly_sales_pct_change > 0.25]
        response = result.to_dict()

    else:
        response = "Sorry, I didn't understand your question."

    # Return the response
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
