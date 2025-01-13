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
    html.H1("NC Public School Education County Data Dashboard", style={'text-align': 'center'}),
    html.Div([
        html.Label("Select County:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='county-dropdown',
            options=[{'label': county, 'value': county} for county in counties],
            value=counties[0],
            style={'width': '50%'}
        ),
        html.Label("Select Year Range:"),
        dcc.RangeSlider(
            id='year-slider',
            min=1970,
            max=2024,
            step=1,
            marks={
                int(year): {'label': str(year), 'style': {'transform': 'rotate(45deg)', 'font-size': '12px'}}
                for year in range(1970, 2024, 2)  # Show marks every 2 years
            },
            value=[1970, 2024]  # Default range
        )
    ], style={'margin-bottom': '20px'}),
    dcc.Tabs([
        dcc.Tab(label='Pupils', children=[
            dcc.Graph(id='pupils-total-enrollment'),
            dcc.Graph(id='pupils-enrollment-by-race'),
            dcc.Graph(id='pupils-enrollment-white-percentage'),
            dcc.Graph(id='pupils-enrollment-public-percentage')
        ]),
        dcc.Tab(label='Finances', children=[
            dcc.Graph(id='finances-funding-percentage'),
            dcc.Graph(id='finances-expenditure-per-pupil'),
            dcc.Graph(id='finances-source-breakdown')
        ]),
        dcc.Tab(label='Current Expenses', children=[
            dcc.Graph(id='expenses-total'),
            dcc.Graph(id='expenses-salaries-by-source'),
            dcc.Graph(id='expenses-employee-benefit-by-source'),
            dcc.Graph(id='expenses-supplies-by-source'),
            dcc.Graph(id='expenses-services-by-source'),
            dcc.Graph(id='expenses-instructional-equipment-by-source')
        ]),
        dcc.Tab(label='Personnel Summary', children=[
            dcc.Graph(id='personnel-total'),
            dcc.Graph(id='personnel-teacher-by-source'),
            dcc.Graph(id='personnel-admin-by-source')
        ]),
        dcc.Tab(label='Graduate Intentions', children=[
            dcc.Graph(id='graduate-intentions')
        ])
    ])
])

# Callbacks for charts
@app.callback(
    [
        Output('pupils-total-enrollment', 'figure'),
        Output('pupils-enrollment-by-race', 'figure'),
        Output('pupils-enrollment-white-percentage', 'figure'),
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
    [Input('county-dropdown', 'value'), Input('year-slider', 'value')]
)
def update_charts(selected_county, selected_years):
    # Filter data
    filtered = df[(df['area_name'] == selected_county) &
                  (df['year'] >= selected_years[0]) &
                  (df['year'] <= selected_years[1])]
    

    avg_data = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
    avg_data = avg_data[avg_data['local_funding_as_perc'].notna()]  # Remove NaN
    avg_data = avg_data[avg_data['local_funding_as_perc'] >= 0]  # Remove negative values
    avg_data = avg_data[np.isfinite(avg_data['local_funding_as_perc'])]  # Remove infinite values
    yearly_avg = avg_data.groupby('year')[['local_expenditure_per_pupil', 'local_funding_as_perc']].mean().reset_index()


    # Pupils Tab Charts
    fig11 = go.Figure()
    fig11.add_trace(go.Scatter(x=filtered['year'], y=filtered['Public School Final Enrollment'],
                              mode='lines+markers', name='Total Enrollment'))
    fig11.update_layout(title="Total Public School Enrollment", xaxis_title="Year", yaxis_title="Enrollment")

    fig12 = go.Figure()
    fig12.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['pupils_by_race_and_sex_BLACKMale'] + filtered['pupils_by_race_and_sex_BLACKFemale'],
                              mode='lines', name='Black'))
    fig12.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['pupils_by_race_and_sex_WHITEMale'] + filtered['pupils_by_race_and_sex_WHITEFemale'],
                              mode='lines', name='White'))
    fig12.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['pupils_by_race_and_sex_HISPANICMale'] + filtered['pupils_by_race_and_sex_HISPANICFemale'],
                              mode='lines', name='Hispanic'))
    fig12.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['pupils_by_race_and_sex_INDIANMale'] + filtered['pupils_by_race_and_sex_INDIANFemale'] +
                              filtered['pupils_by_race_and_sex_ASIANMale'] + filtered['pupils_by_race_and_sex_ASIANFemale'] +
                              filtered['pupils_by_race_and_sex_TWO OR MORE RACESMale'] + filtered['pupils_by_race_and_sex_TWO OR MORE RACESFemale'] +
                              filtered['pupils_by_race_and_sex_PACIFICISLANDMale'] + filtered['pupils_by_race_and_sex_PACIFICISLANDFemale'],
                              mode='lines', name='Other'))
    fig12.update_layout(title="Public School Enrollment by Race", xaxis_title="Year", yaxis_title="Enrollment")

    fig13 = go.Figure()
    fig13.add_trace(go.Scatter(x=filtered['year'],
                              y=(filtered['pupils_by_race_and_sex_WHITEMale'] + filtered['pupils_by_race_and_sex_WHITEFemale']) /
                              filtered['pupils_by_race_and_sex_Total'], mode='lines+markers', name='% White'))
    fig13.update_layout(title="% of Public School Enrollment that is White", xaxis_title="Year", yaxis_title="Percentage")

    fig14 = go.Figure()
    fig14.add_trace(go.Scatter(x=filtered['year'],
                              y=(filtered['Public School Final Enrollment'] / (filtered['Public School Final Enrollment'] +
                              filtered['Nonpublic School Enrollment'])), mode='lines+markers', name='% Public School Enrollment'))
    fig14.update_layout(title="Public School Enrollment as % of Total Enrollment", xaxis_title="Year", yaxis_title="Percentage")

    # Finances Tab Charts
    fig21 = go.Figure()
    fig21.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['local_funding_as_perc'], mode='lines+markers', name='Funding %'))
    fig21.add_trace(go.Scatter(x=yearly_avg['year'],
                              y=yearly_avg['local_funding_as_perc'], mode='lines', name='Avg Funding %', line=dict(color='gray', dash='dot')))
    fig21.update_layout(title="Local Public School Funding as % of Total Expenditure", xaxis_title="Year", yaxis_title="%")

    fig22 = go.Figure()
    fig22.add_trace(go.Scatter(x=filtered['year'],
                              y=filtered['local_expenditure_per_pupil'], mode='lines+markers', name='Local'))
    fig22.add_trace(go.Scatter(x=yearly_avg['year'],
                              y=yearly_avg['local_expenditure_per_pupil'], mode='lines', name='Avg Local', line=dict(color='gray', dash='dot')))
    fig22.update_layout(title="Public School Expenditure Per Pupil by Source", xaxis_title="Year", yaxis_title="Expenditure")

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
        xaxis_title="Year",
        yaxis_title="Expenditure",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[{"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Expenditure"}}]  # Update axis title
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[{"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}]  # Update axis title
                    ),
                ],
                showactive=True,
                x=0,  # Align to the left
                xanchor="left",
                y=1,  # Align to the top
                yanchor="top",
                pad={"t": 10, "r": 10}  # Add some padding to avoid tight alignment
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, True, True, True] + [False] * len(percent_data)},
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False] * 6 + [True] * len(percent_data)},
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
        xaxis_title="Year",
        yaxis_title="Total",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Show Absolute",
                        method="update",
                        args=[
                            {"visible": [True, True, True, False, False, False]},  # Toggle traces
                            {"yaxis": {"title": "Total"}}
                        ]
                    ),
                    dict(
                        label="Show Percentage",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, True, True]},  # Toggle traces
                            {"yaxis": {"title": "Percentage"}}
                        ]
                    )
                ],
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
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
            y=filtered[columns].sum(axis=1),  # Sum the specified columns row-wise
            mode='lines+markers',
            name=category
        ))

    # Update layout
    fig41.update_layout(
        title="Personnel Summary by Category",
        xaxis_title="Year",
        yaxis_title="Total"
)

    fig42 = go.Figure()
    fig42.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_LocalFund_Teachers_ Elementary Teachers', 
                                          'personnel_summary_LocalFund_Teachers_ Other Teachers',
                                          'personnel_summary_LocalFund_Teachers_ Secondary Teachers']].sum(axis=1), 
                              mode='lines+markers', name='Local - Teachers'))
    fig42.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_StateFund_Teachers_ Elementary Teachers', 
                                          'personnel_summary_StateFund_Teachers_ Other Teachers',
                                          'personnel_summary_StateFund_Teachers_ Secondary Teachers']].sum(axis=1),
                              mode='lines+markers', name='State - Teachers'))
    fig42.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_FederalFund_Teachers_ Elementary Teachers', 
                                          'personnel_summary_FederalFund_Teachers_ Other Teachers',
                                          'personnel_summary_FederalFund_Teachers_ Secondary Teachers']].sum(axis=1),
                              mode='lines+markers', name='Federal - Teachers'))
    fig42.update_layout(title="Teachers Personnel Funding by Source", xaxis_title="Year", yaxis_title="Total")

    fig43 = go.Figure()
    fig43.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_LocalFund_Administrators_ Official Adm., Mgrs.', 
                                          'personnel_summary_LocalFund_Administrators_ Principals',
                                          'personnel_summary_LocalFund_Administrators_ Ast. Principals, Teaching',
                                          'personnel_summary_LocalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1), 
                              mode='lines+markers', name='Local - Administrators'))
    fig43.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_StateFund_Administrators_ Official Adm., Mgrs.', 
                                          'personnel_summary_StateFund_Administrators_ Principals',
                                          'personnel_summary_StateFund_Administrators_ Ast. Principals, Teaching',
                                          'personnel_summary_StateFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1),
                              mode='lines+markers', name='State - Administrators'))
    fig43.add_trace(go.Scatter(x=filtered['year'], 
                              y=filtered[['personnel_summary_FederalFund_Administrators_ Official Adm., Mgrs.', 
                                          'personnel_summary_FederalFund_Administrators_ Principals',
                                          'personnel_summary_FederalFund_Administrators_ Ast. Principals, Teaching',
                                          'personnel_summary_FederalFund_Administrators_Ast. Principals, Nonteaching']].sum(axis=1),
                              mode='lines+markers', name='Federal - Administrators'))
    fig43.update_layout(title="Administrator Personnel Funding by Source", xaxis_title="Year", yaxis_title="Total")

    # Graduate Intentions Tab Chart
    fig10 = go.Figure()
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_PublicSeniorInstitutions'], mode='lines+markers', name='Public Senior Institution'))
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_PrivateSeniorInstitutions'], mode='lines+markers', name='Private Senior Institution'))
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_CommunityTechnicalCollege'], mode='lines+markers', name='Community Technical College'))
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_PrivateJuniorInstitutions'], mode='lines+markers', name='Private Junior Institution'))
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_TradeBusinessNursing'], mode='lines+markers', name='Trade Business Nursing'))
    fig10.add_trace(go.Scatter(x=filtered['year'], 
                               y=filtered['hs_graduate_intentions_Other'], mode='lines+markers', name='Other'))
    fig10.update_layout(title="High School Graduates by Post-Graduate Intentions", xaxis_title="Year", yaxis_title="Total")

    return fig11, fig12, fig13, fig14, fig21, fig22, fig23, fig31, fig32, fig33, fig34, fig35, fig36, fig41, fig42, fig43, fig10


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
