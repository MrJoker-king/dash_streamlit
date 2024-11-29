from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Hello Dash!"),
    html.Button("Click me", className="button")
])

if __name__ == '__main__':
    app.run_server(debug=True)
