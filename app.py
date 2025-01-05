import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

# Uncomment the following line to load data from a local file for testing
df = pd.read_csv('Data/nc-education-data.csv')

# Data preparation
counties = sorted([county for county in df['area_name'].unique() if 'Schools' not in county and 'County' in county])
years = sorted(df['year'].unique())

# Initialize the Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("NC Public School Education County Data Dashboard", style={'text-align': 'center'}),
    
    # Dropdown for county selection
    html.Div([
        html.Label("Select County:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='county-dropdown',
            options=[{'label': county, 'value': county} for county in counties],
            value=str(counties[0]),  # Default value converted to string
            style={'width': '50%'}
        )
    ], style={'margin-bottom': '20px'}),

    # Slider for year selection
    html.Div([
        html.Label("Select Year Range:"),
        dcc.RangeSlider(
            id='year-slider',
            min=1970,
            max=2025,  # Explicitly set 2025 as the maximum year
            step=1,
            marks={
                int(year): {'label': str(year), 'style': {'transform': 'rotate(45deg)', 'font-size': '12px'}}
                for year in range(1970, 2025, 2)  # Show marks every 2 years
            },
            value=[1970, 2025]  # Default range
        )
    ], style={'width': '80%', 'margin': 'auto'}),
    
    # Section for Financial Charts
    html.Div([
        html.H2("Financials", style={'text-align': 'center'}),
        dcc.Graph(id='financial-chart-1'),
        dcc.Graph(id='financial-chart-2'),
        dcc.Graph(id='financial-chart-3')
    ]),
    
    # Section for Education Charts
    html.Div([
        html.H2("Education", style={'text-align': 'center'}),
        dcc.Graph(id='education-chart-1'),
        dcc.Graph(id='education-chart-2')
    ]),
    
    # Section for Demographics Charts
    html.Div([
        html.H2("Demographics", style={'text-align': 'center'}),
        dcc.Graph(id='demographics-chart-1'),
        dcc.Graph(id='demographics-chart-2')
    ])
])

# Callbacks for updating charts based on filters
@app.callback(
    [
        Output('financial-chart-1', 'figure'),
        Output('financial-chart-2', 'figure'),
        Output('financial-chart-3', 'figure'),
        Output('education-chart-1', 'figure'),
        Output('education-chart-2', 'figure'),
        Output('demographics-chart-1', 'figure'),
        Output('demographics-chart-2', 'figure')
    ],
    [Input('county-dropdown', 'value'), Input('year-slider', 'value')]
)
def update_charts(selected_county, selected_years):
    # Filter data based on county and year range
    filtered_data = df[(df['area_name'] == selected_county) & 
                       (df['year'] >= selected_years[0]) & 
                       (df['year'] <= selected_years[1])]
    
    avg_data = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
    yearly_avg = avg_data.groupby('year')[['local_expenditure_per_pupil', 'local_funding_as_perc']].mean().reset_index()
    
    years = filtered_data['year']

    # Financials
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=years, y=filtered_data['local_expenditure_per_pupil'], mode='lines+markers', name='Local Expenditure Per Pupil'))
    fig1.add_trace(go.Scatter(x=yearly_avg['year'], y=yearly_avg['local_expenditure_per_pupil'], mode='lines', name='Yearly Average for All Counties', line=dict(color='gray', dash='dot')))
    fig1.update_layout(title="Local Public School Expenditure Per Pupil", xaxis_title="Year", yaxis_title="Expenditure (000s)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=years, y=filtered_data['local_funding_as_perc'], mode='lines+markers', name='Local Public School Funding %'))
    fig2.add_trace(go.Scatter(x=yearly_avg['year'], y=yearly_avg['local_funding_as_perc'], mode='lines', name='Yearly Average for All Counties', line=dict(color='gray', dash='dot')))
    fig2.update_layout(title="Local Public School Funding as % of Total Expenditure", xaxis_title="Year", yaxis_title="%", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=years, y=filtered_data['local_expenditure_per_pupil'], mode='lines', name='Local', line=dict(color='blue')))
    fig3.add_trace(go.Scatter(x=years, y=filtered_data['state_expenditure_per_pupil'], mode='lines', name='State', line=dict(color='orange')))
    fig3.add_trace(go.Scatter(x=years, y=filtered_data['federal_expenditure_per_pupil'], mode='lines', name='Federal', line=dict(color='red')))
    fig3.update_layout(title="Public School Expenditure Per Pupil by Source", xaxis_title="Year", yaxis_title="Expenditure (000s)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    # Education
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=years, y=filtered_data['Public School Final Enrollment'], mode='lines+markers', name='Total Enrollment'))
    fig4.update_layout(title="Total Public School Enrollment", xaxis_title="Year", yaxis_title="Enrollment", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=years, y=filtered_data['public_school_enrollment_perc'], mode='lines+markers', name='Public School Enrollment %'))
    fig5.update_layout(title="Public School Enrollment as % of Total Enrollment", xaxis_title="Year", yaxis_title="%", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    # Demographics
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=years, y=filtered_data['white_total'], mode='lines', name='White', line=dict(color='blue')))
    fig6.add_trace(go.Scatter(x=years, y=filtered_data['black_total'], mode='lines', name='Black', line=dict(color='red')))
    fig6.add_trace(go.Scatter(x=years, y=filtered_data['hispanic_total'], mode='lines', name='Hispanic', line=dict(color='green')))
    fig6.add_trace(go.Scatter(x=years, y=filtered_data['other_race_total'], mode='lines', name='Other', line=dict(color='purple')))
    fig6.update_layout(title="Public School Enrollment by Race", xaxis_title="Year", yaxis_title="Enrollment", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(x=years, y=filtered_data['perc_of_white_enrollment'], mode='lines+markers', name='% of White Enrollment'))
    fig7.update_layout(title="% of White Enrollment", xaxis_title="Year", yaxis_title="%", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7

# Run the app
if __name__ == '__main__':
    print("Starting server...") 
    app.run_server(debug=True, host='0.0.0.0', port=8080)