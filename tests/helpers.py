import grblogtools as glt

def read_single(filename):
    summary = glt.get_dataframe([f'data/{filename}'])
    rows = summary.to_dict(orient='records')
    return rows[0]
