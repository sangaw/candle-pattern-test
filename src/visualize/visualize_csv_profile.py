import sys
import pandas as pd
from flask import Flask, render_template_string, request, jsonify
import webbrowser
import os
import json

app = Flask(__name__)

# Global variable to store the dataframe
df = None
unique_names = []

def load_data(csv_path):
    global df, unique_names
    df = pd.read_csv(csv_path)
    # Get unique names for filtering, handling NaN values
    unique_names = sorted([name for name in df['name'].unique() if pd.notna(name)])
    return df, unique_names

@app.route("/")
def show_table():
    global df, unique_names
    
    # Get filter parameters
    selected_name = request.args.get('name', '')
    search_term = request.args.get('search', '')
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_name:
        filtered_df = filtered_df[filtered_df['name'] == selected_name]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['tradingsymbol'].str.contains(search_term, case=False, na=False) |
            filtered_df['name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Limit to first 1000 rows for performance
    display_df = filtered_df.head(1000)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instrument List CSV Viewer</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            .filter-section { background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
            .stats-section { background-color: #e9ecef; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
            .table-container { max-height: 600px; overflow-y: auto; }
            .table th { position: sticky; top: 0; background-color: white; z-index: 1; }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h1 class="mt-4 mb-4">Instrument List Viewer</h1>
            
            <!-- Filter Section -->
            <div class="filter-section">
                <h4>Filters</h4>
                <form method="GET" class="row">
                    <div class="col-md-4">
                        <label for="name">Filter by Name:</label>
                        <select name="name" id="name" class="form-control" onchange="this.form.submit()">
                            <option value="">All Names</option>
                            {% for name in unique_names %}
                            <option value="{{ name }}" {% if name == selected_name %}selected{% endif %}>{{ name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label for="search">Search (Trading Symbol or Name):</label>
                        <input type="text" name="search" id="search" class="form-control" 
                               value="{{ search_term }}" placeholder="Enter search term...">
                    </div>
                    <div class="col-md-4">
                        <label>&nbsp;</label><br>
                        <button type="submit" class="btn btn-primary">Apply Filters</button>
                        <a href="/" class="btn btn-secondary">Clear Filters</a>
                    </div>
                </form>
            </div>
            
            <!-- Stats Section -->
            <div class="stats-section">
                <h4>Statistics</h4>
                <div class="row">
                    <div class="col-md-3">
                        <strong>Total Records:</strong> {{ total_records }}
                    </div>
                    <div class="col-md-3">
                        <strong>Filtered Records:</strong> {{ filtered_records }}
                    </div>
                    <div class="col-md-3">
                        <strong>Displayed Records:</strong> {{ displayed_records }}
                    </div>
                    <div class="col-md-3">
                        <strong>Unique Names:</strong> {{ unique_count }}
                    </div>
                </div>
                {% if selected_name %}
                <div class="mt-2">
                    <strong>Selected Name:</strong> {{ selected_name }}
                </div>
                {% endif %}
            </div>
            
            <!-- Table Section -->
            <div class="table-container">
                <h4>Data (showing first 1000 filtered records)</h4>
                {{ table|safe }}
            </div>
        </div>
        
        <script>
            // Auto-submit form when search input changes (with delay)
            let searchTimeout;
            $('#search').on('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    $('#search').closest('form').submit();
                }, 500);
            });
        </script>
    </body>
    </html>
    """, 
    table=display_df.to_html(classes="table table-striped table-sm", index=False),
    unique_names=unique_names,
    selected_name=selected_name,
    search_term=search_term,
    total_records=len(df),
    filtered_records=len(filtered_df),
    displayed_records=len(display_df),
    unique_count=len(unique_names)
    )

@app.route("/api/names")
def get_names():
    """API endpoint to get unique names"""
    return jsonify(unique_names)

@app.route("/api/data")
def get_data():
    """API endpoint to get filtered data"""
    selected_name = request.args.get('name', '')
    search_term = request.args.get('search', '')
    
    filtered_df = df.copy()
    
    if selected_name:
        filtered_df = filtered_df[filtered_df['name'] == selected_name]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['tradingsymbol'].str.contains(search_term, case=False, na=False) |
            filtered_df['name'].str.contains(search_term, case=False, na=False)
        ]
    
    return jsonify(filtered_df.head(100).to_dict('records'))

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/instruments_list_20250705_093603.csv"
    
    print(f"Loading data from {csv_path}...")
    load_data(csv_path)
    print(f"Loaded {len(df)} records with {len(unique_names)} unique names")
    print("Starting web server...")
    
    # Open browser after a short delay
    import threading
    import time
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:5000/')
    
    threading.Thread(target=open_browser).start()
    
    # Start Flask app
    app.run(debug=False, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    main() 