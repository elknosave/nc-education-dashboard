import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

# Load data
df = pd.read_parquet('Data/nc-education-data.parquet')

df = df.replace(',', '', regex=True)
columns_to_exclude = ['area_name']  # List of columns to exclude
numeric_columns = [col for col in df.columns if col not in columns_to_exclude]
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
df['local_expenditure_per_pupil'] = df['Public School Expenditures - Local (000s)'] / df['Public School Final Enrollment']
df['local_funding_as_perc'] = (df['Public School Expenditures - Local (000s)'] * 100) / df['Total Expenditures (000s)']
df['local_funding_as_perc'] = pd.to_numeric(df['local_funding_as_perc'], errors='coerce')

# Data preparation
counties = sorted([county for county in df['area_name'].unique() if 'Schools' not in county and 'County' in county])
years = sorted(df['year'].dropna().unique())

# Initialize the Dash app
app = Dash(__name__)
app.title = "NC Public School Education Dashboard"

# Layout with Tabs
app.layout = html.Div([
    # Title
    html.H1("NC Public School Education County Data Dashboard", style={'text-align': 'center'}),
    
    # Select County Section
    html.Div([
        html.Label("Select County:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='county-dropdown',
            options=[{'label': county, 'value': county} for county in counties],
            value=counties[0],
            style={'width': '70%'}
        )
    ], style={'margin-bottom': '30px'}),  # Add space below this section
    
    
    # Tabs Section
    dcc.Tabs([
        dcc.Tab(label='Pupils', children=[
            dcc.Graph(id='pupils-total-enrollment',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='pupils-enrollment-by-race',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='pupils-enrollment-public-percentage',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'})
        ]),
        dcc.Tab(label='Finances', children=[
            dcc.Graph(id='finances-funding-percentage',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='finances-expenditure-per-pupil',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='finances-source-breakdown',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'})
        ]),
        dcc.Tab(label='Current Expenses', children=[
            dcc.Graph(id='expenses-total',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='expenses-salaries-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='expenses-employee-benefit-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='expenses-supplies-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='expenses-services-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='expenses-instructional-equipment-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'})
        ]),
        dcc.Tab(label='Personnel Summary', children=[
            dcc.Graph(id='personnel-total',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='personnel-teacher-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'}),
            dcc.Graph(id='personnel-admin-by-source',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'})
        ]),
        dcc.Tab(label='Graduate Intentions', children=[
            dcc.Graph(id='graduate-intentions',
                      style={'width': '100%', 'overflowX': 'scroll', 'height': '400px'})
        ])
    ])
])

# Callbacks for charts
@app.callback(
    [
        Output('pupils-total-enrollment', 'figure'),
        Output('pupils-enrollment-by-race', 'figure'),
        Output('pupils-enrollment-public-percentage', 'figure'),
        Output('finances-funding-percentage', 'figure'),
        Output('finances-expenditure-per-pupil', 'figure'),
        Output('finances-source-breakdown', 'figure'),
        Output('expenses-total', 'figure'),
        Output('expenses-salaries-by-source', 'figure'),
        Output('expenses-employee-benefit-by-source', 'figure'),
        Output('expenses-supplies-by-source', 'figure'),
        Output('expenses-services-by-source', 'figure'),
        Output('expenses-instructional-equipment-by-source', 'figure'),
        Output('personnel-total', 'figure'),
        Output('personnel-teacher-by-source', 'figure'),
        Output('personnel-admin-by-source', 'figure'),
        Output('graduate-intentions', 'figure')
    ],
    [Input('county-dropdown', 'value')]
)
def update_charts(selected_county):
    # Filter data
    filtered = df[(df['area_name'] == selected_county) & (df['year'] >= 1970) & (df['year'] <= 2024)]
    
    avg_data = df[df['local_funding_as_perc'].notna()]  # Remove NaN
    avg_data = avg_data[avg_data['local_funding_as_perc'] >= 0]  # Remove negative values
    avg_data = avg_data[np.isfinite(avg_data['local_funding_as_perc'])]  # Remove infinite values
    yearly_avg = avg_data.groupby('year')[['local_expenditure_per_pupil', 'local_funding_as_perc']].mean().reset_index()


    # Pupils Tab Charts
    fig11 = go.Figure()
    fig11.add_trace(go.Scatter(x=filtered['year'], y=filtered['Public School Final Enrollment'],
                              mode='lines+markers', name='Total Enrollment'))
    fig11.update_layout(title="Total Public School Enrollment", xaxis_title="Year", yaxis_title="Enrollment",
                        autosize=True)

    # Calculate absolute values
    black_enrollment = filtered['pupils_by_race_and_sex_BLACKMale'] + filtered['pupils_by_race_and_sex_BLACKFemale']
    white_enrollment = filtered['pupils_by_race_and_sex_WHITEMale'] + filtered['pupils_by_race_and_sex_WHITEFemale']
    hispanic_enrollment = filtered['pupils_by_race_and_sex_HISPANICMale'] + filtered['pupils_by_race_and_sex_HISPANICFemale']
    other_enrollment = (filtered['pupils_by_race_and_sex_INDIANMale'] + filtered['pupils_by_race_and_sex_INDIANFemale'] +
                        filtered['pupils_by_race_and_sex_ASIANMale'] + filtered['pupils_by_race_and_sex_ASIANFemale'] +
                        filtered['pupils_by_race_and_sex_TWO OR MORE RACESMale'] + filtered['pupils_by_race_and_sex_TWO OR MORE RACESFemale'] +
                        filtered['pupils_by_race_and_sex_PACIFICISLANDMale'] + filtered['pupils_by_race_and_sex_PACIFICISLANDFemale'])

    # Calculate total enrollment
    total_enrollment = black_enrollment + white_enrollment + hispanic_enrollment + other_enrollment

    # Calculate percentage values
    black_percentage = (black_enrollment / total_enrollment) * 100
    white_percentage = (white_enrollment / total_enrollment) * 100
    hispanic_percentage = (hispanic_enrollment / total_enrollment) * 100
    other_percentage = (other_enrollment / total_enrollment) * 100

    # Create the figure
    fig12 = go.Figure()

    # Add absolute traces
    fig12.add_trace(go.Scatter(x=filtered['year'], y=black_enrollment, mode='lines+markers', name='Black (Absolute)', visible=True))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=white_enrollment, mode='lines+markers', name='White (Absolute)', visible=True))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=hispanic_enrollment, mode='lines+markers', name='Hispanic (Absolute)', visible=True))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=other_enrollment, mode='lines+markers', name='Other (Absolute)', visible=True))

    # Add percentage traces
    fig12.add_trace(go.Scatter(x=filtered['year'], y=black_percentage, mode='lines+markers', name='Black (%)', visible=False))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=white_percentage, mode='lines+markers', name='White (%)', visible=False))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=hispanic_percentage, mode='lines+markers', name='Hispanic (%)', visible=False))
    fig12.add_trace(go.Scatter(x=filtered['year'], y=other_percentage, mode='lines+markers', name='Other (%)', visible=False))

    # Add toggle button
    fig12.update_layout(
        title="Public School Enrollment by Race",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Enrollment",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, True, False, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, False, True, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    fig14 = go.Figure()
    fig14.add_trace(go.Scatter(x=filtered['year'],
                              y=(filtered['Public School Final Enrollment'] / (filtered['Public School Final Enrollment'] +
                              filtered['Nonpublic School Enrollment'])), mode='lines+markers', name='% Public School Enrollment'))
    fig14.update_layout(title="Public School Enrollment as % of Total Enrollment", xaxis_title="Year", yaxis_title="Percentage",
                        autosize=True)

    # Finances Tab Charts
    fig21 = go.Figure()
    fig21.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['local_funding_as_perc'], mode='lines+markers', name='Funding %'))
    fig21.add_trace(go.Scatter(x=yearly_avg['year'],
                              y=yearly_avg['local_funding_as_perc'], mode='lines', name='Avg Funding % For All Counties', line=dict(color='gray', dash='dot')))
    fig21.update_layout(title="Local Public School Funding as % of Total Expenditure",
                        xaxis=dict(range=[1978, max(filtered['year']) + 1],title="Year"), yaxis_title="%",
                        autosize=True, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top", title=None, traceorder="normal"))

    fig22 = go.Figure()
    fig22.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['local_expenditure_per_pupil'], mode='lines+markers', name='Local'))
    fig22.add_trace(go.Scatter(x=yearly_avg['year'],
                              y=yearly_avg['local_expenditure_per_pupil'], mode='lines', name='Avg Local For All Counties', line=dict(color='gray', dash='dot')))
    fig22.update_layout(title="Public School Local Expenditure Per Pupil",
                        xaxis=dict(range=[1978, max(filtered['year']) + 1],
            title="Year"), yaxis_title="Expenditure (000s)",
                        autosize=True, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top", title=None, traceorder="normal"))

    fig23 = go.Figure()
    # Absolute Values Traces
    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['Public School Expenditures - Local (000s)'] / filtered['Public School Final Enrollment'],
        mode='lines+markers',
        name='Local (Absolute)',
        visible=True  # Initially visible
    ))

    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['Public School Expenditures - State (000s)'] / filtered['Public School Final Enrollment'],
        mode='lines+markers',
        name='State (Absolute)',
        visible=True  # Initially visible
    ))

    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['Public School Expenditures - Federal (000s)'] / filtered['Public School Final Enrollment'],
        mode='lines+markers',
        name='Federal (Absolute)',
        visible=True  # Initially visible
    ))

    # Percentage Traces
    total_expenditure_per_pupil = (
        (filtered['Public School Expenditures - Local (000s)'] +
        filtered['Public School Expenditures - State (000s)'] +
        filtered['Public School Expenditures - Federal (000s)'])
        / filtered['Public School Final Enrollment']
    )

    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=(filtered['Public School Expenditures - Local (000s)'] / filtered['Public School Final Enrollment']) /
        total_expenditure_per_pupil * 100,
        mode='lines+markers',
        name='Local (%)',
        visible=False  # Initially hidden
    ))

    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=(filtered['Public School Expenditures - State (000s)'] / filtered['Public School Final Enrollment']) /
        total_expenditure_per_pupil * 100,
        mode='lines+markers',
        name='State (%)',
        visible=False  # Initially hidden
    ))

    fig23.add_trace(go.Scatter(
        x=filtered['year'],
        y=(filtered['Public School Expenditures - Federal (000s)'] / filtered['Public School Final Enrollment']) /
        total_expenditure_per_pupil * 100,
        mode='lines+markers',
        name='Federal (%)',
        visible=False  # Initially hidden
    ))

    # Layout with Dropdown Toggle
    fig23.update_layout(
        title="Public School Expenditure Per Pupil by Source",
        xaxis=dict(
            range=[1978, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Expenditure (000s)",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Current Expenses Tab Charts
    # Compute total expenses for percentage calculations
    total_expenses = (
        filtered['current_expense_SourceTotal_EMPLOYEE BENEFITS'].fillna(0) +
        filtered['current_expense_SourceTotal_INSTRUCTIONAL EQUIP.'].fillna(0) +
        filtered['current_expense_SourceTotal_OTHER OBJECTS'].fillna(0) +
        filtered['current_expense_SourceTotal_PURCHASED SERVICES'].fillna(0) +
        filtered['current_expense_SourceTotal_SALARIES'].fillna(0) +
        filtered['current_expense_SourceTotal_SUPPLIES & MATERIALS'].fillna(0)
    )

    # Replace NaN with 0 for percentage calculations only
    percent_data = {
        'Employee Benefits': filtered['current_expense_SourceTotal_EMPLOYEE BENEFITS'].fillna(0) / total_expenses,
        'Instructional Equipment': filtered['current_expense_SourceTotal_INSTRUCTIONAL EQUIP.'].fillna(0) / total_expenses,
        'Other Objects': filtered['current_expense_SourceTotal_OTHER OBJECTS'].fillna(0) / total_expenses,
        'Purchased Services': filtered['current_expense_SourceTotal_PURCHASED SERVICES'].fillna(0) / total_expenses,
        'Salaries': filtered['current_expense_SourceTotal_SALARIES'].fillna(0) / total_expenses,
        'Supplies & Materials': filtered['current_expense_SourceTotal_SUPPLIES & MATERIALS'].fillna(0) / total_expenses,
    }

    # Absolute values
    fig31 = go.Figure()
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_EMPLOYEE BENEFITS'],
        mode='lines+markers',
        name='Employee Benefits (Absolute)',
        visible=True
    ))
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_INSTRUCTIONAL EQUIP.'],
        mode='lines+markers',
        name='Instructional Equipment (Absolute)',
        visible=True
    ))
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_OTHER OBJECTS'],
        mode='lines+markers',
        name='Other Objects (Absolute)',
        visible=True
    ))
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_PURCHASED SERVICES'],
        mode='lines+markers',
        name='Purchased Services (Absolute)',
        visible=True
    ))
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_SALARIES'],
        mode='lines+markers',
        name='Salaries (Absolute)',
        visible=True
    ))
    fig31.add_trace(go.Scatter(
        x=filtered['year'],
        y=filtered['current_expense_SourceTotal_SUPPLIES & MATERIALS'],
        mode='lines+markers',
        name='Supplies & Materials (Absolute)',
        visible=True
    ))

    # Percentage values
    for name, values in percent_data.items():
        fig31.add_trace(go.Scatter(
            x=filtered['year'],
            y=values * 100,  # Convert to percentage
            mode='lines+markers',
            name=f'{name} (%)',
            visible=False
        ))

    # Layout with Toggle
    fig31.update_layout(
        title="Current Expenses by Category",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, True, True, True,
                                            False, False, False, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, False, False, False,
                                           True, True, True, True, True, True,]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Calculate total salaries for percentage calculation
    total_salaries = (
        filtered['current_expense_SourceLocal_SALARIES'] +
        filtered['current_expense_SourceState_SALARIES'] +
        filtered['current_expense_SourceFederal_SALARIES']
    ).fillna(0)

    # Replace 0 in total_salaries with NaN to avoid division errors
    safe_total_salaries = total_salaries.replace(0, np.nan)

    # Create the figure
    fig32 = go.Figure()

    # Absolute values
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceLocal_SALARIES'], 
        mode='lines+markers', 
        name='Local - Salaries (Absolute)', 
        visible=True
    ))
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceState_SALARIES'], 
        mode='lines+markers', 
        name='State - Salaries (Absolute)', 
        visible=True
    ))
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceFederal_SALARIES'], 
        mode='lines+markers', 
        name='Federal - Salaries (Absolute)', 
        visible=True
    ))

    # Percentage values
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceLocal_SALARIES'] / safe_total_salaries) * 100, 
        mode='lines+markers', 
        name='Local - Salaries (%)', 
        visible=False
    ))
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceState_SALARIES'] / safe_total_salaries) * 100, 
        mode='lines+markers', 
        name='State - Salaries (%)', 
        visible=False
    ))
    fig32.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceFederal_SALARIES'] / safe_total_salaries) * 100, 
        mode='lines+markers', 
        name='Federal - Salaries (%)', 
        visible=False
    ))

    # Layout with Toggle
    fig32.update_layout(
        title="Salaries Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )


    # Calculate total employee benefits for percentage calculation
    total_employee_benefits = (
        filtered['current_expense_SourceLocal_EMPLOYEE BENEFITS'] +
        filtered['current_expense_SourceState_EMPLOYEE BENEFITS'] +
        filtered['current_expense_SourceFederal_EMPLOYEE BENEFITS']
    ).fillna(0)

    # Replace 0 in total_employee_benefits with NaN to avoid division errors
    safe_total_employee_benefits = total_employee_benefits.replace(0, np.nan)

    # Create the figure
    fig33 = go.Figure()

    # Absolute values
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceLocal_EMPLOYEE BENEFITS'], 
        mode='lines+markers', 
        name='Local - Employee Benefits (Absolute)', 
        visible=True
    ))
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceState_EMPLOYEE BENEFITS'], 
        mode='lines+markers', 
        name='State - Employee Benefits (Absolute)', 
        visible=True
    ))
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceFederal_EMPLOYEE BENEFITS'], 
        mode='lines+markers', 
        name='Federal - Employee Benefits (Absolute)', 
        visible=True
    ))

    # Percentage values
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceLocal_EMPLOYEE BENEFITS'] / safe_total_employee_benefits) * 100, 
        mode='lines+markers', 
        name='Local - Employee Benefits (%)', 
        visible=False
    ))
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceState_EMPLOYEE BENEFITS'] / safe_total_employee_benefits) * 100, 
        mode='lines+markers', 
        name='State - Employee Benefits (%)', 
        visible=False
    ))
    fig33.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceFederal_EMPLOYEE BENEFITS'] / safe_total_employee_benefits) * 100, 
        mode='lines+markers', 
        name='Federal - Employee Benefits (%)', 
        visible=False
    ))

    # Layout with Toggle
    fig33.update_layout(
        title="Employee Benefits Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Calculate total supplies and materials for percentage calculation
    total_supplies = (
        filtered['current_expense_SourceLocal_SUPPLIES & MATERIALS'] +
        filtered['current_expense_SourceState_SUPPLIES & MATERIALS'] +
        filtered['current_expense_SourceFederal_SUPPLIES & MATERIALS']
    ).fillna(0)

    # Replace 0 in total_supplies with NaN to avoid division errors
    safe_total_supplies = total_supplies.replace(0, np.nan)

    # Create the figure
    fig34 = go.Figure()

    # Absolute values
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceLocal_SUPPLIES & MATERIALS'], 
        mode='lines+markers', 
        name='Local - Supplies & Materials (Absolute)', 
        visible=True
    ))
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceState_SUPPLIES & MATERIALS'], 
        mode='lines+markers', 
        name='State - Supplies & Materials (Absolute)', 
        visible=True
    ))
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceFederal_SUPPLIES & MATERIALS'], 
        mode='lines+markers', 
        name='Federal - Supplies & Materials (Absolute)', 
        visible=True
    ))

    # Percentage values
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceLocal_SUPPLIES & MATERIALS'] / safe_total_supplies) * 100, 
        mode='lines+markers', 
        name='Local - Supplies & Materials (%)', 
        visible=False
    ))
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceState_SUPPLIES & MATERIALS'] / safe_total_supplies) * 100, 
        mode='lines+markers', 
        name='State - Supplies & Materials (%)', 
        visible=False
    ))
    fig34.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceFederal_SUPPLIES & MATERIALS'] / safe_total_supplies) * 100, 
        mode='lines+markers', 
        name='Federal - Supplies & Materials (%)', 
        visible=False
    ))

    # Layout with Toggle
    fig34.update_layout(
        title="Supplies & Materials Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Calculate total purchased services for percentage calculation
    total_services = (
        filtered['current_expense_SourceLocal_PURCHASED SERVICES'] +
        filtered['current_expense_SourceState_PURCHASED SERVICES'] +
        filtered['current_expense_SourceFederal_PURCHASED SERVICES']
    ).fillna(0)

    # Replace 0 in total_services with NaN to avoid division errors
    safe_total_services = total_services.replace(0, np.nan)

    # Create the figure
    fig35 = go.Figure()

    # Absolute values
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceLocal_PURCHASED SERVICES'], 
        mode='lines+markers', 
        name='Local - Purchased Services (Absolute)', 
        visible=True
    ))
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceState_PURCHASED SERVICES'], 
        mode='lines+markers', 
        name='State - Purchased Services (Absolute)', 
        visible=True
    ))
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceFederal_PURCHASED SERVICES'], 
        mode='lines+markers', 
        name='Federal - Purchased Services (Absolute)', 
        visible=True
    ))

    # Percentage values
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceLocal_PURCHASED SERVICES'] / safe_total_services) * 100, 
        mode='lines+markers', 
        name='Local - Purchased Services (%)', 
        visible=False
    ))
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceState_PURCHASED SERVICES'] / safe_total_services) * 100, 
        mode='lines+markers', 
        name='State - Purchased Services (%)', 
        visible=False
    ))
    fig35.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceFederal_PURCHASED SERVICES'] / safe_total_services) * 100, 
        mode='lines+markers', 
        name='Federal - Purchased Services (%)', 
        visible=False
    ))

    # Layout with Toggle
    fig35.update_layout(
        title="Purchased Services Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Calculate total instructional equipment for percentage calculation
    total_instructional_equipment = (
        filtered['current_expense_SourceLocal_EMPLOYEE BENEFITS'] +
        filtered['current_expense_SourceState_INSTRUCTIONAL EQUIP.'] +
        filtered['current_expense_SourceFederal_INSTRUCTIONAL EQUIP.']
    ).fillna(0)

    # Replace 0 in total_instructional_equipment with NaN to avoid division errors
    safe_total_instructional_equipment = total_instructional_equipment.replace(0, np.nan)

    # Create the figure
    fig36 = go.Figure()

    # Absolute values
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceLocal_INSTRUCTIONAL EQUIP.'], 
        mode='lines+markers', 
        name='Local - Instructional Equipment (Absolute)', 
        visible=True
    ))
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceState_INSTRUCTIONAL EQUIP.'], 
        mode='lines+markers', 
        name='State - Instructional Equipment (Absolute)', 
        visible=True
    ))
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=filtered['current_expense_SourceFederal_INSTRUCTIONAL EQUIP.'], 
        mode='lines+markers', 
        name='Federal - Instructional Equipment (Absolute)', 
        visible=True
    ))

    # Percentage values
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceLocal_INSTRUCTIONAL EQUIP.'] / safe_total_instructional_equipment) * 100, 
        mode='lines+markers', 
        name='Local - Instructional Equipment (%)', 
        visible=False
    ))
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceState_INSTRUCTIONAL EQUIP.'] / safe_total_instructional_equipment) * 100, 
        mode='lines+markers', 
        name='State - Instructional Equipment (%)', 
        visible=False
    ))
    fig36.add_trace(go.Scatter(
        x=filtered['year'], 
        y=(filtered['current_expense_SourceFederal_INSTRUCTIONAL EQUIP.'] / safe_total_instructional_equipment) * 100, 
        mode='lines+markers', 
        name='Federal - Instructional Equipment (%)', 
        visible=False
    ))

    # Layout with Toggle
    fig36.update_layout(
        title="Instructional Equipment Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )


    # Personnel Summary Tab Charts
    # Define a dictionary mapping categories to the columns to be summed
    categories = {
        'Administrators': [
            'personnel_summary_TotalFund_Administrators_ Official Adm., Mgrs.',
            'personnel_summary_TotalFund_Administrators_ Principals',
            'personnel_summary_TotalFund_Administrators_ Ast. Principals, Teaching',
            'personnel_summary_TotalFund_Administrators_Ast. Principals, Nonteaching'
        ],
        'Teachers': [
            'personnel_summary_TotalFund_Teachers_ Elementary Teachers',
            'personnel_summary_TotalFund_Teachers_ Secondary Teachers',
            'personnel_summary_TotalFund_Teachers_ Other Teachers'
        ],
        'Professionals': [
            'personnel_summary_TotalFund_Professionals_ Guidance',
            'personnel_summary_TotalFund_Professionals_ Psychological',
            'personnel_summary_TotalFund_Professionals_Librarian, Audiovisual',
            'personnel_summary_TotalFund_Professionals_Consultant, Supervisor'
        ]
    }

    # Create the figure
    fig41 = go.Figure()

    # Loop through the categories and add traces
    for category, columns in categories.items():
        fig41.add_trace(go.Scatter(
            x=filtered['year'],
            y=filtered[columns].sum(axis=1).replace(0, np.nan),  # Sum the specified columns row-wise
            mode='lines+markers',
            name=category
        ))

    # Update layout
    fig41.update_layout(
        title="Personnel Summary by Category",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        autosize=True
)

    # Calculate total funding for teachers
    teachers_local = filtered[['personnel_summary_LocalFund_Teachers_ Elementary Teachers', 
                            'personnel_summary_LocalFund_Teachers_ Other Teachers',
                            'personnel_summary_LocalFund_Teachers_ Secondary Teachers']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_LocalFund_Teachers_ Elementary Teachers', 
                                                     'personnel_summary_LocalFund_Teachers_ Other Teachers',
                                                     'personnel_summary_LocalFund_Teachers_ Secondary Teachers']].sum(axis=1) == 0)), np.nan)
    teachers_state = filtered[['personnel_summary_StateFund_Teachers_ Elementary Teachers', 
                            'personnel_summary_StateFund_Teachers_ Other Teachers',
                            'personnel_summary_StateFund_Teachers_ Secondary Teachers']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_StateFund_Teachers_ Elementary Teachers', 
                                                     'personnel_summary_StateFund_Teachers_ Other Teachers',
                                                     'personnel_summary_StateFund_Teachers_ Secondary Teachers']].sum(axis=1) == 0)), np.nan)
    teachers_federal = filtered[['personnel_summary_FederalFund_Teachers_ Elementary Teachers', 
                                'personnel_summary_FederalFund_Teachers_ Other Teachers',
                                'personnel_summary_FederalFund_Teachers_ Secondary Teachers']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_FederalFund_Teachers_ Elementary Teachers', 
                                                     'personnel_summary_FederalFund_Teachers_ Other Teachers',
                                                     'personnel_summary_FederalFund_Teachers_ Secondary Teachers']].sum(axis=1) == 0)), np.nan)
    teachers_total = teachers_local + teachers_state + teachers_federal

    # Create percentage values
    teachers_local_percent = (teachers_local / teachers_total) * 100
    teachers_state_percent = (teachers_state / teachers_total) * 100
    teachers_federal_percent = (teachers_federal / teachers_total) * 100

    # Create the figure for teachers
    fig42 = go.Figure()

    # Add absolute traces
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_local, mode='lines+markers', name='Local - Teachers (Absolute)', visible=True))
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_state, mode='lines+markers', name='State - Teachers (Absolute)', visible=True))
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_federal, mode='lines+markers', name='Federal - Teachers (Absolute)', visible=True))

    # Add percentage traces
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_local_percent, mode='lines+markers', name='Local - Teachers (%)', visible=False))
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_state_percent, mode='lines+markers', name='State - Teachers (%)', visible=False))
    fig42.add_trace(go.Scatter(x=filtered['year'], y=teachers_federal_percent, mode='lines+markers', name='Federal - Teachers (%)', visible=False))

    # Add toggle button
    fig42.update_layout(
        title="Teachers Personnel Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Repeat similar logic for administrators
    admins_local = filtered[['personnel_summary_LocalFund_Administrators_ Official Adm., Mgrs.', 
                            'personnel_summary_LocalFund_Administrators_ Principals',
                            'personnel_summary_LocalFund_Administrators_ Ast. Principals, Teaching',
                            'personnel_summary_LocalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_LocalFund_Administrators_ Official Adm., Mgrs.', 
                                                     'personnel_summary_LocalFund_Administrators_ Principals',
                                                     'personnel_summary_LocalFund_Administrators_ Ast. Principals, Teaching',
                                                     'personnel_summary_LocalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1) == 0)), np.nan)
    admins_state = filtered[['personnel_summary_StateFund_Administrators_ Official Adm., Mgrs.', 
                            'personnel_summary_StateFund_Administrators_ Principals',
                            'personnel_summary_StateFund_Administrators_ Ast. Principals, Teaching',
                            'personnel_summary_StateFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_StateFund_Administrators_ Official Adm., Mgrs.', 
                                                     'personnel_summary_StateFund_Administrators_ Principals',
                                                     'personnel_summary_StateFund_Administrators_ Ast. Principals, Teaching',
                                                     'personnel_summary_StateFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1) == 0)), np.nan)
    admins_federal = filtered[['personnel_summary_FederalFund_Administrators_ Official Adm., Mgrs.', 
                            'personnel_summary_FederalFund_Administrators_ Principals',
                            'personnel_summary_FederalFund_Administrators_ Ast. Principals, Teaching',
                            'personnel_summary_FederalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1).where(~((filtered['year'] < 2005) & (filtered[['personnel_summary_FederalFund_Administrators_ Official Adm., Mgrs.', 
                                                     'personnel_summary_FederalFund_Administrators_ Principals',
                                                     'personnel_summary_FederalFund_Administrators_ Ast. Principals, Teaching',
                                                     'personnel_summary_FederalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1) == 0)), np.nan)
    admins_total = admins_local + admins_state + admins_federal

    # Create percentage values
    admins_local_percent = (admins_local / admins_total) * 100
    admins_state_percent = (admins_state / admins_total) * 100
    admins_federal_percent = (admins_federal / admins_total) * 100

    # Create the figure for teachers
    fig43 = go.Figure()

    # Add absolute traces
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_local, mode='lines+markers', name='Local - Admins (Absolute)', visible=True))
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_state, mode='lines+markers', name='State - Admins (Absolute)', visible=True))
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_federal, mode='lines+markers', name='Federal - Admins (Absolute)', visible=True))

    # Add percentage traces
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_local_percent, mode='lines+markers', name='Local - Admins (%)', visible=False))
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_state_percent, mode='lines+markers', name='State - Admins (%)', visible=False))
    fig43.add_trace(go.Scatter(x=filtered['year'], y=admins_federal_percent, mode='lines+markers', name='Federal - Admins (%)', visible=False))

    # Add toggle button
    fig43.update_layout(
        title="Administrator Personnel Funding by Source",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )

    # Graduate Intentions Tab Chart
    # Replace nan with 0 for years between 2005 and 2023
    filtered = filtered.copy()  # Ensure the original DataFrame is not modified
    filtered.loc[(filtered['year'] > 2004) & (filtered['year'] < 2024)] = filtered.loc[
        (filtered['year'] > 2004) & (filtered['year'] < 2024)
    ].fillna(0)

    # Calculate absolute values
    public_senior = filtered['hs_graduate_intentions_PublicSeniorInstitutions']
    private_senior = filtered['hs_graduate_intentions_PrivateSeniorInstitutions']
    community_college = filtered['hs_graduate_intentions_CommunityTechnicalCollege']
    private_junior = filtered['hs_graduate_intentions_PrivateJuniorInstitutions']
    trade_nursing = filtered['hs_graduate_intentions_TradeBusinessNursing']
    other = filtered['hs_graduate_intentions_Other']

    # Calculate total graduates
    total_graduates = public_senior + private_senior + community_college + private_junior + trade_nursing + other

    # Calculate percentage values
    public_senior_perc = (public_senior / total_graduates) * 100
    private_senior_perc = (private_senior / total_graduates) * 100
    community_college_perc = (community_college / total_graduates) * 100
    private_junior_perc = (private_junior / total_graduates) * 100
    trade_nursing_perc = (trade_nursing / total_graduates) * 100
    other_perc = (other / total_graduates) * 100

    # Create the figure
    fig51 = go.Figure()

    # Add absolute traces
    fig51.add_trace(go.Scatter(x=filtered['year'], y=public_senior, mode='lines+markers', name='Public Senior Institution (Absolute)', visible=True))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=private_senior, mode='lines+markers', name='Private Senior Institution (Absolute)', visible=True))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=community_college, mode='lines+markers', name='Community Technical College (Absolute)', visible=True))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=private_junior, mode='lines+markers', name='Private Junior Institution (Absolute)', visible=True))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=trade_nursing, mode='lines+markers', name='Trade Business Nursing (Absolute)', visible=True))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=other, mode='lines+markers', name='Other (Absolute)', visible=True))

    # Add percentage traces
    fig51.add_trace(go.Scatter(x=filtered['year'], y=public_senior_perc, mode='lines+markers', name='Public Senior Institution (%)', visible=False))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=private_senior_perc, mode='lines+markers', name='Private Senior Institution (%)', visible=False))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=community_college_perc, mode='lines+markers', name='Community Technical College (%)', visible=False))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=private_junior_perc, mode='lines+markers', name='Private Junior Institution (%)', visible=False))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=trade_nursing_perc, mode='lines+markers', name='Trade Business Nursing (%)', visible=False))
    fig51.add_trace(go.Scatter(x=filtered['year'], y=other_perc, mode='lines+markers', name='Other (%)', visible=False))

    # Add toggle button
    fig51.update_layout(
        title="High School Graduates by Post-Graduate Intentions",
        xaxis=dict(
            range=[2003, max(filtered['year']) + 1],
            title="Year"
        ),
        yaxis_title="Total",
        autosize=True,
        legend=dict(
            orientation="h",  # Horizontal layout for legend
            y=-0.2,  # Place legend below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
            title=None,  # Remove "Legend" title
            traceorder="normal"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, True, True, True,
                                            False, False, False, False, False, False]},
                            {"yaxis": {"title": "Total"}}]),
                    dict(label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, False, False, False,
                                           True, True, True, True, True, True,]},
                            {"yaxis": {"title": "Percentage"}}])
                ],
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2,
                yanchor="top"
            )
        ]
    )
    return fig11, fig12, fig14, fig21, fig22, fig23, fig31, fig32, fig33, fig34, fig35, fig36, fig41, fig42, fig43, fig51


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
