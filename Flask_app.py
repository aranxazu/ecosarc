from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime
import calendar

app = Flask(__name__)

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fondos-mutuos')
def fondos_mutuos():
    return render_template('index.html')

@app.route('/rentabilidades', methods=['GET', 'POST'])
def rentabilidades():
    fecha_datepicker = request.form.get('datepicker')
    df = pd.read_csv('uploads/rentabilidades_acumuladas.csv', sep=";", index_col=None)

    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
    fechas = df['fecha'].unique()

    if fecha_datepicker is None:
        fecha_datepicker = fechas.max()
        fecha_str = fecha_datepicker.date().strftime('%m/%d/%Y')
        df_fecha = df[df['fecha'] == fecha_datepicker]
    else:
        fecha_typo_date = datetime.strptime(fecha_datepicker, '%m/%d/%Y')
        df_fecha = df[df['fecha'] == fecha_typo_date]
        fecha_str = fecha_datepicker

    if df_fecha.empty:
        html = "<p>No hay información para este periodo</p>"
    else:
        html = get_rentabilidades(df_fecha)
    print(html)
    return render_template('rentabilidades.html', html=html, fecha_actual=fecha_str)

@app.route('/portafolios', methods=['GET', 'POST'])
def portafolios():
    tipo_cartera = request.form.get('tipos')
    df = pd.read_csv('uploads/portafolio_nacional.csv', sep=";", index_col=None)
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')

    fondos = df['Run Fondo'].unique()

    run = str(request.form.get('fondos'))
    fecha = request.form.get("datepicker")

    date_picker = fecha

    if fecha != None and fecha != '':
        fecha = datetime.strptime(fecha, '%m/%d/%Y')
        fecha = ultimo_dia_del_mes(fecha)


    if run is None or tipo_cartera is None:
        html = ""
    else:
        html = get_portafolio(run, tipo_cartera, fecha)

    return render_template('portafolios.html', fondos=fondos, tipos=['Nacional', 'Internacional'], html=html)

@app.route('/detalle-fondo/<run>', methods=['POST','GET'])
def detalle_fondo(run):
    print(run)
    return render_template('detalle-fondo.html', table_data=get_detalle_fondo(run), table_series=get_series(run))

# Funciones
def get_rentabilidades(df):
    df['Run Fondo'] = df["Run Fondo"].apply(crear_enlace)
    html_table = df.to_html(classes='table', index=False, escape=False)
    return html_table

def get_detalle_fondo(run):
    df = pd.read_csv('uploads/detalle_fondo.csv', sep=";", index_col=None)
    df['Run Fondo'] = df['Run Fondo'].astype(str)
    df = df[df['Run Fondo'] == run]
    html_table = df.to_html(classes='table', index=False, escape=False)
    return html_table

def get_series(run):
    df = pd.read_csv('uploads/series.csv', sep=";", index_col=None)
    df['Run Fondo'] = df['Run Fondo'].astype(str)
    df = df[df['Run Fondo'] == run]
    html_table = df.to_html(classes='table', index=False, escape=False)
    return html_table

def get_portafolio(run, tipo_cartera, fecha):
    df = pd.read_csv(f'uploads/portafolio_{tipo_cartera}.csv', sep=";", index_col=None)
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
    df['Run Fondo'] = df['Run Fondo'].astype(str)
    df = df[df['Run Fondo'] == run]
    df = df[df['fecha'] == fecha]
    df['Run Fondo'] = df["Run Fondo"].apply(crear_enlace)

    if df.empty:
        html_table = '<p>No hay información para el periodo seleccionado</p>'
    else:
        html_table = df.to_html(classes='form-table', index=False, escape=False)
    return html_table

def crear_enlace(run):
    html = f'<a id="aunder" onclick="submitForm(\'{run}\')" name="{run}" value="{run}">{run}</a>'
    html += f'<input type="hidden" name="run" value="{run}">'
    return html

def ultimo_dia_del_mes(fecha):
    # Obtener el último día del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]

    # Crear una nueva fecha con el último día del mes
    fecha_cierre_mes = datetime(fecha.year, fecha.month, ultimo_dia)

    return fecha_cierre_mes

if __name__ == '__main__':
    app.run(debug=True)
