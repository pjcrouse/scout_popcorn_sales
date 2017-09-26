import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Span, Label, Range1d, HoverTool
from bokeh.models.widgets import Select
from bokeh.layouts import layout, widgetbox, row, column

df = pd.read_csv('data.csv')
#df['Sales'] = np.random.randint(0,400,len(df))
#df['Pack'] = 'Pack 12'
total_sales = df['Sales'].sum()
#df.to_csv('/Users/pat/Desktop/Pop_BS/bokeh_server_flask2/data.csv', index=False)

def create_figure(total_sales):
    selection=select.value
    df_sum = df.groupby(selection).agg(sum).reset_index()
    source = ColumnDataSource(df_sum)
    #need x_factors to pass to make x_axis categorical
    x_factors=list(source.data[selection])

    p = figure(y_axis_label='Total Sales', x_range=x_factors, plot_width=500, plot_height=400)
    p.vbar(x=selection, width = 0.5, top='Sales', source=source)
    p.yaxis.formatter=NumeralTickFormatter(format="$ 0,0[.]00")

    hover = HoverTool(tooltips=[
    ("Sales", "@Sales{($ 0.00 a)}"),])

    p.add_tools(hover)

    if select.value == 'Pack':
        p.y_range = Range1d(0, max(14000, int(total_sales*1.2)))
        goal = Span(location=12500, dimension='width', line_color='red', line_dash='solid', line_width=3)
        span_label = Label(x=150, y=12500, x_units='screen', y_units='data', text='Goal=$12.5K')
        p.add_layout(goal)
        p.add_layout(span_label)

    return p

#create updated func:
def update(attr, old, new):
    layout.children[1] = create_figure(total_sales)

select_options=[('Pack', 'Pack'), ('Den', 'Den'), ('Rank', 'Scout Rank')]
select=Select(title="Aggregate By:", value='Pack', options=select_options)
select.on_change('value', update)

controls = widgetbox([select], width=200)
layout = column(controls, create_figure(total_sales))

curdoc().add_root(layout)
curdoc().title = "Popcorn Sales"
