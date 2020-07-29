import flask
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import plotly.plotly
import plotly.graph_objs as go
import plotly
import json

app = flask.Flask(__name__)

conVal=[]
numVal=[]
intVal=[]
df=np.array([])
col=[]

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8585, debug=True, use_reloader=False)

@app.route('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global df, conVal, numVal
    if request.method == 'POST':
        # get file name
        name = request.files['file'].filename
        if(name.endswith('.csv')):
            df = pd.read_csv(request.files.get('file'), encoding='CP949')
        elif(name.endswith('.xlsx')):
            df = pd.read_excel(request.files.get('file'), encoding='CP949')
        else:
            print('wrong file')

        df.columns=[column.replace(" ", "_") for column in df.columns]
        # determine numeric or continous
        conVal.clear()
        numVal.clear()
        intVal.clear()
        col.clear()
        for i in range(0, df.shape[1]):
            checknum = df[df.keys()[i]].nunique()
            #print(df[df.keys()[i]].dtypes)
            if(checknum >10 or df[df.keys()[i]].dtypes=='float64'):
                conVal.append(str(df.keys()[i]))
                col.append(str(df.keys()[i]))
            elif(checknum >10 or df[df.keys()[i]].dtypes=='int64')  :
                intVal.append(str(df.keys()[i]))
                col.append(str(df.keys()[i]))
            else:
                numVal.append(str(df.keys()[i]))
                col.append(str(df.keys()[i]))

        return render_template('upload.html', tablename=name, colNames = col, rowData=list(df.values.tolist()), zip=zip, conVal=conVal, numVal=numVal)
    return render_template('upload.html')


@app.route('/graphbuilder')
def graphbuilder():
    page = request.args.get('graph')
    return render_template('graphbuilder.html', page=page)


def plotscatter(xCol, yCol, label):
    if label=='None':
        data = [
            go.Scatter(
                x=df[xCol],
                y=df[yCol],
                mode='markers',
            )
        ]
        layout = go.Layout(
                yaxis=dict(title=yCol),
                xaxis=dict(title=xCol)
            )
        figure = go.Figure(data=data, layout=layout)
    else:
        figure = go.Figure()
        for name, group in df.groupby(label):
            figure.add_trace(
                go.Scatter(
                    name=name,
                    x=group[xCol],
                    mode='markers',
                )
            )
        figure.layout.update(yaxis=dict(title=yCol),
                xaxis=dict(title=xCol))

    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/scatter', methods=['POST', 'GET'])
def scatter():
    global df, conVal, scatter, numVal
    if request.method=='POST':
        xCol = request.form.get("xcol")
        yCol = request.form.get("ycol")
        label = request.form.get("label")
        print(xCol, yCol, label)
        if str(xCol) != "None" and str(yCol) != "None":
            scatter=plotscatter(xCol, yCol, label)
            return render_template('scatter.html',columns=conVal, plot=scatter, label=numVal)
        return redirect(request.url)
    return render_template('scatter.html', columns=conVal, label=numVal)

def plotbox(xCol, yCol):
    data = [
        go.Box(
            x=df[xCol],
            y=df[yCol],
        )
    ]
    layout = go.Layout(
            yaxis=dict(title=yCol),
            xaxis=dict(title=xCol)
        )
    figure = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/boxplot', methods=['GET', 'POST'])
def boxplot():
    global df, conVal, numVal
    if request.method=='POST':
        xCol = request.form.get('xcol')
        yCol = request.form.get('ycol')
        print(xCol, yCol)
        if str(xCol) != "None" and str(yCol) != "None":
            boxplot=plotbox(xCol, yCol)
            return render_template('boxplot.html',xcolumns=numVal, ycolumns=conVal, plot=boxplot)
        return redirect(request.url)
    return render_template('boxplot.html', xcolumns=numVal, ycolumns=conVal)

def bar(xCol, yCol):
    data = [
        go.Bar(
            x=df[xCol],
            y=df[yCol],
            #textposition='auto'
        )
    ]
    layout = go.Layout(
        yaxis=dict(title=yCol),
        xaxis=dict(title=xCol)
    )
    figure = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/barchart', methods=['GET', 'POST'])
def barchart():
    global df, conVal
    if request.method=='POST':
        xCol = request.form.get("xcol")
        yCol = request.form.get("ycol")
        print(xCol, yCol)
        if str(xCol) != "None" and str(yCol) != "None":
            plot=bar(xCol, yCol)
            return render_template('barchart.html',columns=conVal, plot=plot)
        return redirect(request.url)
    return render_template('barchart.html', columns=conVal)

def histo(col):
    data = [
        go.Histogram(
            x=df[col]
        )
    ]
    layout = go.Layout(
        xaxis=dict(title=col),
    )
    figure = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/histogram', methods=['GET', 'POST'])
def histogram():
    global df, intVal
    if request.method=='POST':
        col = request.form.get('col')
        print(col)
        if str(col) != "None":
            plot=histo(col)
            return render_template('histogram.html',columns=intVal, plot=plot)
        return redirect(request.url)
    return render_template('histogram.html', columns=intVal)

def pie(col):
    data = [
        go.Pie(
            values=df[col].value_counts().values,
            labels=df[col].value_counts().index
        )
    ]
    figure = go.Figure(data=data)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/piechart',methods=['GET', 'POST'])
def piechart():
    global df, numVal
    if request.method=='POST':
        col = request.form.get('col')
        print(col)
        if str(col) != "None":
            plot=pie(col)
            return render_template('piechart.html',columns=numVal, plot=plot)
        return redirect(request.url)
    return render_template('piechart.html', columns=numVal)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


