#!/usr/bin/env python3
"""
Unified CSV Viewer - Combines Flask interactive viewer and ydata-profiling reports.
"""
import sys
import os
import pandas as pd
from flask import Flask, render_template_string, request, jsonify
import webbrowser
import json
import threading
import time
import argparse

# Try to import ydata-profiling (optional)
try:
    from ydata_profiling import ProfileReport
    YDATA_AVAILABLE = True
except ImportError:
    YDATA_AVAILABLE = False
    print("Warning: ydata-profiling not available. Install with: pip install ydata-profiling")

app = Flask(__name__)

# Global variables
df = None
unique_names = []
csv_path = None

def load_data(csv_path):
    """Load CSV data and extract unique names."""
    global df, unique_names
    df = pd.read_csv(csv_path)
    # Get unique names for filtering, handling NaN values
    unique_names = sorted([name for name in df['name'].unique() if pd.notna(name)])
    return df, unique_names

def generate_profile_report(csv_path, output_name=None):
    """Generate ydata-profiling report."""
    if not YDATA_AVAILABLE:
        print("Error: ydata-profiling not available. Install with: pip install ydata-profiling")
        return None
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate output filename
    if output_name is None:
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        output_name = f"{base_name}_profile"
    
    output_html = f"data/{output_name}.html"
    
    print(f"Generating ydata-profiling report...")
    profile = ProfileReport(df, title=f"{output_name.replace('_', ' ').title()} Profile", explorative=True)
    profile.to_file(output_html)
    
    print(f"Profile report saved as {output_html}")
    return output_html

@app.route("/")
def show_table():
    """Main Flask route for interactive table view."""
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
        <title>Unified CSV Viewer - {{ csv_filename }}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            .filter-section { background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
            .stats-section { background-color: #e9ecef; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
            .table-container { max-height: 600px; overflow-y: auto; }
            .table th { position: sticky; top: 0; background-color: white; z-index: 1; }
            .action-buttons { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h1 class="mt-4 mb-4">Unified CSV Viewer</h1>
            <h4 class="text-muted">{{ csv_filename }}</h4>
            
            <!-- Action Buttons -->
            <div class="action-buttons">
                <a href="/generate_profile" class="btn btn-success" target="_blank">
                    📊 Generate ydata-Profiling Report
                </a>
                <a href="/download_csv" class="btn btn-info">
                    📥 Download Filtered CSV
                </a>
                <a href="/stats" class="btn btn-warning">
                    📈 View Statistics
                </a>
            </div>
            
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
    unique_count=len(unique_names),
    csv_filename=os.path.basename(csv_path) if csv_path else "CSV File"
    )

@app.route("/generate_profile")
def generate_profile():
    """Generate ydata-profiling report."""
    if not YDATA_AVAILABLE:
        return "ydata-profiling not available. Install with: pip install ydata-profiling"
    
    output_html = generate_profile_report(csv_path)
    if output_html:
        # Extract just the filename from the full path
        filename = os.path.basename(output_html)
        return f"""
        <html>
        <head><title>Profile Report Generated</title></head>
        <body>
            <h2>Profile Report Generated Successfully!</h2>
            <p>Report saved as: {output_html}</p>
            <a href="/view_profile/{filename}" target="_blank" class="btn btn-primary">Open Report</a>
            <a href="/" class="btn btn-secondary">Back to Viewer</a>
        </body>
        </html>
        """
    return "Error generating profile report"

@app.route("/view_profile/<filename>")
def view_profile(filename):
    """Serve the generated profile report HTML file."""
    profile_path = os.path.join('data', filename)
    if os.path.exists(profile_path):
        with open(profile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    else:
        return f"Profile report not found: {filename}"

@app.route("/stats")
def show_stats():
    """Show detailed statistics."""
    global df
    
    # Calculate statistics
    stats = {
        'total_records': len(df),
        'columns': list(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
    }
    
    # Exchange distribution
    if 'exchange' in df.columns:
        stats['exchange_distribution'] = df['exchange'].value_counts().to_dict()
    
    # Instrument type distribution
    if 'instrument_type' in df.columns:
        stats['instrument_type_distribution'] = df['instrument_type'].value_counts().to_dict()
    
    # Name distribution (top 20)
    if 'name' in df.columns:
        stats['name_distribution'] = df['name'].value_counts().head(20).to_dict()
    
    return render_template_string("""
    <html>
    <head>
        <title>CSV Statistics</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-4">
            <h1>CSV Statistics</h1>
            <a href="/" class="btn btn-primary mb-3">Back to Viewer</a>
            
            <div class="row">
                <div class="col-md-6">
                    <h3>Basic Info</h3>
                    <ul>
                        <li><strong>Total Records:</strong> {{ stats.total_records }}</li>
                        <li><strong>Memory Usage:</strong> {{ "%.2f"|format(stats.memory_usage) }} MB</li>
                        <li><strong>Columns:</strong> {{ stats.columns|length }}</li>
                    </ul>
                    
                    <h4>Columns:</h4>
                    <ul>
                    {% for col in stats.columns %}
                        <li>{{ col }}</li>
                    {% endfor %}
                    </ul>
                </div>
                
                <div class="col-md-6">
                    {% if stats.exchange_distribution %}
                    <h3>Exchange Distribution</h3>
                    <ul>
                    {% for exchange, count in stats.exchange_distribution.items() %}
                        <li>{{ exchange }}: {{ count }}</li>
                    {% endfor %}
                    </ul>
                    {% endif %}
                    
                    {% if stats.instrument_type_distribution %}
                    <h3>Instrument Type Distribution</h3>
                    <ul>
                    {% for type, count in stats.instrument_type_distribution.items() %}
                        <li>{{ type }}: {{ count }}</li>
                    {% endfor %}
                    </ul>
                    {% endif %}
                </div>
            </div>
            
            {% if stats.name_distribution %}
            <div class="row mt-4">
                <div class="col-12">
                    <h3>Top 20 Names</h3>
                    <ul>
                    {% for name, count in stats.name_distribution.items() %}
                        <li>{{ name }}: {{ count }}</li>
                    {% endfor %}
                    </ul>
                </div>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, stats=stats)

@app.route("/download_csv")
def download_csv():
    """Download filtered CSV data."""
    # This would need to be implemented with proper CSV download
    return "CSV download feature coming soon!"

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Unified CSV Viewer with Flask and ydata-profiling")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("--port", type=int, default=5000, help="Port for Flask server (default: 5000)")
    parser.add_argument("--profile-only", action="store_true", help="Generate profile report only, don't start Flask server")
    
    args = parser.parse_args()
    
    global csv_path
    csv_path = args.csv_file
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    print(f"Loading data from {csv_path}...")
    load_data(csv_path)
    print(f"Loaded {len(df)} records with {len(unique_names)} unique names")
    
    if args.profile_only:
        # Generate profile report only
        if YDATA_AVAILABLE:
            output_html = generate_profile_report(csv_path)
            if output_html:
                webbrowser.open('file://' + os.path.realpath(output_html))
        else:
            print("ydata-profiling not available. Install with: pip install ydata-profiling")
    else:
        # Start Flask server
        print("Starting unified web server...")
        print(f"Access the viewer at: http://127.0.0.1:{args.port}")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://127.0.0.1:{args.port}')
        
        threading.Thread(target=open_browser).start()
        
        # Start Flask app
        app.run(debug=False, host='127.0.0.1', port=args.port)

if __name__ == "__main__":
    main() 