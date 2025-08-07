"""
Funciones auxiliares para el análisis de datos del Superstore

Este módulo contiene funciones que utilizamos para:
- Cargar y limpiar datos
- Procesar fechas
- Crear visualizaciones personalizadas
- Generar reportes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Configuramos el estilo de matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def cargar_datos(ruta_archivo):
    """
    Cargamos el dataset y realizamos limpieza básica
    
    Parámetros:
    ruta_archivo (str): Ruta al archivo CSV
    
    Retorna:
    pandas.DataFrame: DataFrame limpio con columnas en español
    """
    # Cargamos los datos
    df = pd.read_csv(ruta_archivo, encoding='utf-8')
    
    # Traducimos los nombres de las columnas al español
    columnas_traducidas = {
        'Row ID': 'id_fila',
        'Order ID': 'id_pedido',
        'Order Date': 'fecha_pedido',
        'Ship Date': 'fecha_envio',
        'Ship Mode': 'modo_envio',
        'Customer ID': 'id_cliente',
        'Customer Name': 'nombre_cliente',
        'Segment': 'segmento',
        'Country': 'pais',
        'City': 'ciudad',
        'State': 'estado',
        'Postal Code': 'codigo_postal',
        'Region': 'region',
        'Product ID': 'id_producto',
        'Category': 'categoria',
        'Sub-Category': 'subcategoria',
        'Product Name': 'nombre_producto',
        'Sales': 'ventas',
        'Quantity': 'cantidad',
        'Discount': 'descuento',
        'Profit': 'ganancia'
    }
    
    df = df.rename(columns=columnas_traducidas)
    
    return df

def procesar_fechas(df):
    """
    Procesamos las columnas de fechas y creamos nuevas variables temporales
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    
    Retorna:
    pandas.DataFrame: DataFrame con fechas procesadas
    """
    # Convertimos las fechas a formato datetime
    df['fecha_pedido'] = pd.to_datetime(df['fecha_pedido'])
    df['fecha_envio'] = pd.to_datetime(df['fecha_envio'])
    
    # Creamos nuevas variables temporales
    df['año'] = df['fecha_pedido'].dt.year
    df['mes'] = df['fecha_pedido'].dt.month
    df['dia_semana'] = df['fecha_pedido'].dt.day_name()
    df['trimestre'] = df['fecha_pedido'].dt.quarter
    df['dias_envio'] = (df['fecha_envio'] - df['fecha_pedido']).dt.days
    
    return df

def crear_resumen_basico(df):
    """
    Creamos un resumen básico de las características del dataset
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    
    Retorna:
    dict: Diccionario con estadísticas básicas
    """
    resumen = {
        'total_filas': len(df),
        'total_columnas': len(df.columns),
        'periodo_datos': f"{df['fecha_pedido'].min().strftime('%Y-%m-%d')} a {df['fecha_pedido'].max().strftime('%Y-%m-%d')}",
        'total_ventas': df['ventas'].sum(),
        'total_ganancia': df['ganancia'].sum(),
        'margen_promedio': (df['ganancia'].sum() / df['ventas'].sum()) * 100,
        'pedidos_unicos': df['id_pedido'].nunique(),
        'clientes_unicos': df['id_cliente'].nunique(),
        'productos_unicos': df['id_producto'].nunique()
    }
    
    return resumen

def analizar_valores_faltantes(df):
    """
    Analizamos los valores faltantes en el dataset
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    
    Retorna:
    pandas.DataFrame: DataFrame con información de valores faltantes
    """
    valores_faltantes = df.isnull().sum()
    porcentaje_faltantes = (valores_faltantes / len(df)) * 100
    
    resultado = pd.DataFrame({
        'columna': valores_faltantes.index,
        'valores_faltantes': valores_faltantes.values,
        'porcentaje': porcentaje_faltantes.values
    })
    
    return resultado[resultado['valores_faltantes'] > 0].sort_values('valores_faltantes', ascending=False)

def crear_grafico_ventas_temporales(df, guardar=False, ruta_salida=None):
    """
    Creamos un gráfico de evolución temporal de las ventas
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    guardar (bool): Si guardamos el gráfico
    ruta_salida (str): Ruta donde guardar el gráfico
    """
    # Agrupamos ventas por mes
    ventas_mensuales = df.groupby(['año', 'mes'])['ventas'].sum().reset_index()
    ventas_mensuales['fecha'] = pd.to_datetime(ventas_mensuales[['año', 'mes']].assign(day=1))
    
    # Creamos el gráfico
    fig = px.line(ventas_mensuales, x='fecha', y='ventas', 
                  title='Evolución Temporal de las Ventas',
                  labels={'ventas': 'Ventas ($)', 'fecha': 'Fecha'})
    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        font=dict(size=12)
    )
    
    if guardar and ruta_salida:
        fig.write_html(ruta_salida)
    
    return fig

def crear_grafico_top_productos(df, top_n=10, guardar=False, ruta_salida=None):
    """
    Creamos un gráfico de los productos más vendidos
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    top_n (int): Número de productos a mostrar
    guardar (bool): Si guardamos el gráfico
    ruta_salida (str): Ruta donde guardar el gráfico
    """
    # Calculamos ventas por producto
    top_productos = df.groupby('subcategoria')['ventas'].sum().sort_values(ascending=False).head(top_n)
    
    # Creamos el gráfico
    fig = px.bar(x=top_productos.values, y=top_productos.index, 
                 orientation='h',
                 title=f'Top {top_n} Subcategorías por Ventas',
                 labels={'x': 'Ventas ($)', 'y': 'Subcategoría'})
    
    fig.update_layout(
        xaxis_title="Ventas ($)",
        yaxis_title="Subcategoría",
        font=dict(size=12)
    )
    
    if guardar and ruta_salida:
        fig.write_html(ruta_salida)
    
    return fig

def analizar_rentabilidad_por_categoria(df):
    """
    Analizamos la rentabilidad por categoría de productos
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    
    Retorna:
    pandas.DataFrame: DataFrame con análisis de rentabilidad
    """
    rentabilidad = df.groupby('categoria').agg({
        'ventas': 'sum',
        'ganancia': 'sum',
        'cantidad': 'sum',
        'id_pedido': 'nunique'
    }).round(2)
    
    rentabilidad['margen_porcentaje'] = ((rentabilidad['ganancia'] / rentabilidad['ventas']) * 100).round(2)
    rentabilidad['venta_promedio'] = (rentabilidad['ventas'] / rentabilidad['id_pedido']).round(2)
    
    return rentabilidad.sort_values('ventas', ascending=False)

def exportar_reporte_excel(df, ruta_salida):
    """
    Exportamos un reporte completo a Excel con múltiples hojas
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    ruta_salida (str): Ruta donde guardar el archivo Excel
    """
    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        # Hoja 1: Resumen general
        resumen = crear_resumen_basico(df)
        pd.DataFrame(list(resumen.items()), columns=['Métrica', 'Valor']).to_excel(
            writer, sheet_name='Resumen_General', index=False
        )
        
        # Hoja 2: Análisis por categoría
        rentabilidad = analizar_rentabilidad_por_categoria(df)
        rentabilidad.to_excel(writer, sheet_name='Rentabilidad_Categoria')
        
        # Hoja 3: Top productos
        top_productos = df.groupby('subcategoria')['ventas'].sum().sort_values(ascending=False).head(20)
        top_productos.to_excel(writer, sheet_name='Top_Productos')
        
        # Hoja 4: Análisis temporal
        ventas_mensuales = df.groupby(['año', 'mes']).agg({
            'ventas': 'sum',
            'ganancia': 'sum',
            'cantidad': 'sum'
        })
        ventas_mensuales.to_excel(writer, sheet_name='Ventas_Mensuales')

def calcular_metricas_cliente(df):
    """
    Calculamos métricas importantes por cliente
    
    Parámetros:
    df (pandas.DataFrame): DataFrame con datos de superstore
    
    Retorna:
    pandas.DataFrame: DataFrame con métricas por cliente
    """
    metricas_cliente = df.groupby(['id_cliente', 'nombre_cliente']).agg({
        'ventas': ['sum', 'mean', 'count'],
        'ganancia': 'sum',
        'cantidad': 'sum',
        'fecha_pedido': ['min', 'max']
    }).round(2)
    
    # Aplanamos las columnas multinivel
    metricas_cliente.columns = ['_'.join(col).strip() for col in metricas_cliente.columns]
    
    # Calculamos días como cliente
    metricas_cliente['dias_como_cliente'] = (
        metricas_cliente['fecha_pedido_max'] - metricas_cliente['fecha_pedido_min']
    ).dt.days
    
    return metricas_cliente.sort_values('ventas_sum', ascending=False)

# Función para configurar el estilo de gráficos
def configurar_estilo_graficos():
    """
    Configuramos el estilo general para todos nuestros gráficos
    """
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10

# Fin de funciones auxiliares para el análisis de Superstore
