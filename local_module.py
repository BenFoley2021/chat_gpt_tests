def func(df):
    import plotly.express as px
    fig = px.scatter(df, x='Views', y='Viewing Affinity', size='Views Growth', color='Creator')
    return fig