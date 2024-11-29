import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import base64
import io

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("BMS Data Dashboard", style={'text-align': 'center'}),
    
    # File upload
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload BMS Data', style={'font-size': '18px'}),
        multiple=False,
        style={
            'width': '50%',
            'margin': '10px auto',
            'text-align': 'center'
        }
    ),
    
    # Filters
    html.Div([
        html.Label("Filter by Battery ID:"),
        dcc.Input(id='battery-id', type='text', placeholder="Enter Battery ID"),
        
        html.Label("Filter by Date Range:"),
        dcc.DatePickerRange(
            id='date-picker',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date"
        )
    ], style={'margin': '20px', 'padding': '10px', 'border': '1px solid #ccc'}),
    
    # Display data
    html.Div(id='output-table', style={'margin': '20px'}),
    
    # Graphs
    dcc.Graph(id='soc-vs-time', style={'margin': '20px'}),
    dcc.Graph(id='voltage-vs-current', style={'margin': '20px'}),
])

# Function to parse uploaded file
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded))
    return df

# Callback to process uploaded file and display data
@app.callback(
    [
        Output('output-table', 'children'),
        Output('soc-vs-time', 'figure'),
        Output('voltage-vs-current', 'figure'),
    ],
    [
        Input('upload-data', 'contents'),
        Input('battery-id', 'value'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date')
    ]
)
def update_dashboard(contents, battery_id, start_date, end_date):
    if not contents:
        return "Upload a file to view data.", {}, {}

    # Parse uploaded data
    df = parse_contents(contents)
    
    # Filter by Battery ID
    if battery_id:
        df = df[df['Battery ID'] == battery_id]
    
    # Filter by Date Range
    if start_date and end_date:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Create DataTable
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
    
    # Create SoC vs Time plot
    if 'Time' in df.columns and 'SoC' in df.columns:
        soc_fig = px.line(df, x='Time', y='SoC', title='State of Charge (SoC) vs Time')
    else:
        soc_fig = {}

    # Create Voltage vs Current plot
    if 'Voltage' in df.columns and 'Current' in df.columns:
        voltage_current_fig = px.scatter(df, x='Voltage', y='Current', title='Voltage vs Current')
    else:
        voltage_current_fig = {}

    return table, soc_fig, voltage_current_fig

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
