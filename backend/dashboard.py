import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import Flask, render_template, request

app = Flask(__name__)

# Function to load data from output directory and filter by date range
def load_and_filter_data(start_date, end_date, output_dir):
    # Convert string dates to datetime objects for comparison
    start_date = datetime.strptime(start_date, '%Y-%m-%d')  # Start date in '%Y-%m-%d'
    end_date = datetime.strptime(end_date, '%Y-%m-%d')  # End date in '%Y-%m-%d'

    data = []
    
    # Read each file in the output directory
    for filename in os.listdir(output_dir):
        # Only process files with the correct date format (YYYYMMDD.txt)
        if filename.endswith('.txt'):
            # Extract the date from the filename (expecting the format YYYYMMDD)
            file_date_str = filename[:8]  # YYYYMMDD (ignore the hour part)
            print(file_date_str)  # Debugging: Print the date part of the filename
            
            # Parse the file date from the filename string (format: YYYYMMDD)
            try:
                file_date = datetime.strptime(file_date_str, '%Y%m%d')  # Correct date format (YYYYMMDD)
            except ValueError as e:
                print(f"Error parsing file date from filename {filename}: {e}")
                continue  # Skip this file if date parsing fails
            
            # Only load data if the file's date is within the start and end range
            if start_date <= file_date <= end_date:
                with open(os.path.join(output_dir, filename), 'r') as f:
                    for line in f:
                        # Parse each line and append to data list
                        fields = line.strip().split('|')
                        if len(fields) == 4:
                            data.append({
                                'hour': fields[0],
                                'product': fields[1],
                                'category': fields[2],
                                'total_price': float(fields[3])
                            })
    
    # Convert list to DataFrame for easier manipulation and visualization
    df = pd.DataFrame(data)
    
    # If no data is found for the given date range
    if df.empty:
        print(f"No data found for the date range: {start_date} to {end_date}")
        return None
    
    return df

# Function to generate a dashboard (basic visualization)
def generate_dashboard(df, start_date, end_date):
    if df is None:
        return None
    
    # Group data by product and category and sum the total_price
    aggregated_data = df.groupby(['product', 'category']).agg({'total_price': 'sum'}).reset_index()
    
    # Generate bar plot for total price by product/category
    plt.figure(figsize=(10, 6))
    for category in aggregated_data['category'].unique():
        category_data = aggregated_data[aggregated_data['category'] == category]
        plt.bar(category_data['product'], category_data['total_price'], label=category)
    
    plt.title(f"Total Sales by Product and Category ({start_date} to {end_date})")
    plt.xlabel("Product")
    plt.ylabel("Total Sales (Price)")
    plt.xticks(rotation=90)
    
    # Annotate bars with the total price
    for idx, row in aggregated_data.iterrows():
        plt.text(
            row['product'], 
            row['total_price'], 
            f"{row['total_price']:.2f}", 
            ha='center', 
            va='bottom', 
            fontsize=10
        )
    
    plt.legend()
    plt.tight_layout()

    # Save the plot to a BytesIO object to send it to the HTML page
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')  # Convert image to base64
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Define the output directory
        output_dir = "output"
        
        # Load and filter the data
        df = load_and_filter_data(start_date, end_date, output_dir)
        
        # Generate the dashboard and get the plot as a base64-encoded string
        plot_url = generate_dashboard(df, start_date, end_date)
    
    return render_template('index.html', plot_url=plot_url)

if __name__ == "__main__":
    app.run(debug=True)
