from flask import Flask, render_template, url_for, redirect, request
from bokeh.embed import server_document
#from bokeh.client import pull_session
import datetime
import pandas as pd
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    n=10
    goal=12500
    days_left = (datetime.date(2017, 10, 22)-datetime.date.today()).days
    df, names = get_top_sellers()
    df['Family'].fillna(df['Name'], inplace=True)
    df['Family Sum'] = df['Sales'].groupby(df['Family']).transform('sum')
    df['Family Members'] = df['Sales'].groupby(df['Family']).transform('count')
    df['Family Max'] = df['Sales'].groupby(df['Family']).transform('max')
    df['Family Rank'] = df.groupby("Family")["Sales"].rank(method='dense', ascending=False)
    df['Chunky'] = df.apply(determine_chunky, axis=1)
    total = df['Sales'].sum()
    total_str = '{:,.0f}'.format(total)
    left_to_sell = '{:,.2f}'.format((goal-total)/days_left/len(df)*7)
    left_to_sell_num = float(left_to_sell)
    records = df[df['Sales']>0]
    scouts_with_sales = len(records)
    n=min(len(records), n)
    if n == 0:
        table_title = "No Sales Data Yet:"
    elif n == 1:
        table_title = "Top Seller:"
    else:
        table_title = "Top {} Sellers:".format(n)
    #session=pull_session(url='http://localhost:5006/bokeh_bar')
    #bokeh_script=autoload_server(None,url='http://localhost:5006/bokeh_bar', session_id=session.id)
    bokeh_script=server_document("http://159.203.96.247:5006/bokeh_bar")
    if request.method == 'POST':
        scout = request.form['scout']
        amount = float(request.form['sales'])
        df.loc[df.Name == scout, 'Sales'] = amount
        df=df[['Name', 'Rank', 'Den', 'Sales', 'Pack', 'Family']]
        df.to_csv('/opt/webapps/bokehflask/data.csv', index=False)
        return redirect('/')
    return render_template('index.html', bokeh_script=bokeh_script, days_left=days_left,
                            table_title=table_title, n=n, records=records[:n], scout_names=names,
                            goal=goal, total_str=total_str, left_to_sell=left_to_sell,
                            left_to_sell_num=left_to_sell_num, scouts_with_sales=scouts_with_sales)

app.wsgi_app = ProxyFix(app.wsgi_app)

def get_top_sellers():
    df = pd.read_csv('/opt/webapps/bokehflask/data.csv', na_values='None')
    names = sorted(list(set(df['Name'].tolist())))
    df = df.sort_values(by='Sales', axis=0, ascending=False).reset_index(drop=True)
    return df, names

def determine_chunky(x):
    if x['Sales'] >= 350.0:
        return 1
    if (x['Family Members'] == 2.0) & (x['Family Sum'] >= 525.0):
        return 1
    if x['Family Members'] == 3.0:
        if x['Family Sum'] >= 700.0:
            return 1
        elif (x['Family Rank'] == 1) & (x['Family Sum'] >= 350):
            return 1
        elif (x['Family Rank'] == 2) & (x['Sales'] + x['Family Max'] >= 525.0):
            return 1
    else:
        return 0

if __name__ == "__main__":
    app.run()
