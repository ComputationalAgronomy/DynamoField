

import base64
import datetime
import io

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate
from dynamofield import app_db, app_style
from dynamofield.field import field_table, importer


def generate_upload_box_message(parsed_name):
    return html.Div([
            html.Br(),
            'Drag and Drop or ', html.A('Select Files    '),
            html.Br(),
            parsed_name
        ])




@dash.callback(
    Output("upload-data", "children"),
    Output("import_markdown", "children"),
    Input("upload-data", "filename"),
    Input("importing_type", "value"),
)
def update_uploader_info(filename, data_type):
    parsed_name = ""
    parsed_data_type = "Import data type:"
    if filename is not None:
        parsed_name = f"\nCurrent files: {filename}"
    if data_type is not None:
        parsed_data_type = f"{parsed_data_type} {data_type}"
    markdown_text = f"{parsed_data_type}  {parsed_name}"
    html_code = generate_upload_box_message(parsed_name)
    return html_code, markdown_text



@dash.callback(
    Output("btn_import", "disabled"),
    Input("importing_type", "value"),
    Input('upload-data', 'filename'),
    Input("importing_type", "required"),
    Input("importing_type", "style"),
)
def is_btn_import_disabled(data_type, filenames, r, s):
    is_disabled = True
    if data_type is not None and filenames is not None:
        is_disabled = False
    print(f"data_type:{data_type}=={filenames}=={data_type is not None}=={is_disabled}")
    return is_disabled


def parse_contents(contents, filename, date=None):

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            # data_importer = importer.DataImporter(filename, data_type)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception("Invalid file type.")
    except Exception as e:
        print(e)
        df = pd.DataFrame({
            'There was an error processing this file':
                f"Error message: {str(e)}"
        }, index=[0])
        # return html.Div([
        #     f'There was an error processing this file.\n{e}'
        # ])

    return df


def preview_content(contents, filename, date):
    df = parse_contents(contents, filename, date)
    col_name_dict = [{'name': i, 'id': i} for i in df.columns]
    return html.Div([
        html.H6([filename, "  Timestamp:", datetime.datetime.fromtimestamp(date)]),
        dash_table.DataTable(df.to_dict('records'), col_name_dict),
        html.Hr(style={"height": "2px", "margin": "5px"}),
        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre([contents[0:200] + '   ...  '], style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


def import_dataframe(contents, filename, data_type, is_append,
                     db_table: field_table.FieldTable):
    #     content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string)

    try:
        df = parse_contents(contents, filename)
        data_importer = importer.DataImporter(df, data_type)
        data_importer.parse_df_to_dynamo_json(
            append=is_append, db_table=db_table)
        import_len = db_table.import_batch_field_data_res(
            data_importer)  # How to test this effectively?
    except Exception as e:
        print(e)
        return html.Div([
            f'There was an error processing this file.<br>{e}'
        ])

    return html.Div([
        html.H5(filename),
        # html.H6(datetime.datetime.fromtimestamp(date)),
        dcc.Markdown(
            f"Imported **{import_len}** rows and store in info={data_type}."),
        # dash_table.DataTable(df.to_dict('records'),
        #     [{'name': i, 'id': i} for i in df.columns]
        # ),
    ])


@dash.callback(
    Output('output-data-upload', 'children'),
    Input('btn_import', 'n_clicks'),
    Input('btn_preview', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('importing_type', 'value'),
    State("import_is_append", "value"),
    State('store_db_info', 'data'),
    prevent_initial_call=True,
)
def update_output(btn_1, btn_2,
                  list_of_contents, list_of_names, list_of_dates,
                  data_type, is_append, db_info):
    children = []
    is_append = eval(is_append)
    print(f"{data_type}, {is_append}, {list_of_names}")
    if list_of_contents is not None:
        if "btn_preview" == ctx.triggered_id:
            children = [preview_content(c, n, d) for c, n, d in
                        zip(list_of_contents, list_of_names, list_of_dates)]
        elif "btn_import" == ctx.triggered_id:
            # if not db_info["db_status"] or not db_info["table_status"]:
            #     children = ([html.H5("Database not available")])
            print(f"data_type_{data_type}")
            db_table = app_db.connect_db_table(db_info)
            children = [
                import_dataframe(
                    c, n, data_type, is_append, db_table) for c, n, in zip(
                    list_of_contents, list_of_names)]
            # else:
            # children = html.Div([html.H5("Please enter data type")])

    return children



@dash.callback(
    Output("btn_delete_data_type", "disabled"),
    Input("text_delete_data_type", "value"),
    Input("text_delete_data_type", "required"),
)
def is_btn_delete_disabled(data_type, is_required):
    is_disabled = True
    if data_type is not None:
        is_disabled = False
    print(f"DELETE: data_type:{data_type}={data_type is not None}=={is_disabled}=={is_required}")
    return is_disabled



@dash.callback(
    Output('md_delete_output', 'children'),
    Input('btn_delete_data_type', 'n_clicks'),
    State('text_delete_data_type', 'value'),
    State('store_db_info', 'data'),
    prevent_initial_call=True,
)
def delete_data_type(btn_delete, data_type, db_info):
    if data_type is None:
        raise PreventUpdate
    try:
        md = app_db.delete_all_items_data_type(db_info, data_type)
    except Exception as e:
        md = f"Please enter a data_type to delete all items. {e}"
    return md
