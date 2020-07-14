import flask
from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = flask.Flask(__name__)

conVal=[]
numVal=[]
df=np.array([])
col=[]

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
        col.clear()
        for i in range(0, df.shape[1]):
            checknum = df[df.keys()[i]].nunique()
            if(checknum >10 or df[df.keys()[i]].dtypes=='float64'):
                conVal.append(str(df.keys()[i]))
                col.append(str(df.keys()[i]).replace(" ","_"))
            else:
                numVal.append(str(df.keys()[i]))
                col.append(str(df.keys()[i]).replace(" ", "_"))

        return render_template('upload.html', tablename=name, colNames = col, rowData=list(df.values.tolist()), zip=zip, conVal=conVal, numVal=numVal)
    return render_template('upload.html')


@app.route('/graphbuilder')
def graphbuilder():
    return render_template('graphbuilder.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8585, debug=True)

