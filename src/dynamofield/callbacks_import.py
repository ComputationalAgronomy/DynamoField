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
    return html.Div(
        [
            # html.Br(),
            "Drag and Drop or ",
            html.A("Select Files    "),
            # html.Br(),
            parsed_name,
        ]
    )


@dash.callback(
    Output("upload-data", "children"),
    Output("import_markdown", "children"),
    Input("upload-data", "filename"),
    Input("importing_type", "value"),
)
def update_uploader_info(filename, record_type):
    parsed_name = ""
    parsed_record_type = "Import data type:"
    if filename is not None:
        parsed_name = f"\nCurrent files: {filename}"
    if record_type is not None:
        parsed_record_type = f"{parsed_record_type} {record_type}"
    markdown_text = f"{parsed_record_type}  {parsed_name}"
    html_code = generate_upload_box_message(parsed_name)
    return html_code, markdown_text


@dash.callback(
    Output("btn_import", "disabled"),
    Input("importing_type", "value"),
    Input("upload-data", "filename"),
    Input("importing_type", "required"),
    Input("importing_type", "style"),
)
def is_btn_import_disabled(record_type, filenames, r, s):
    is_disabled = True
    if record_type is not None and filenames is not None:
        is_disabled = False
    # print(f"record_type:{record_type}=={filenames}=={record_type is not None}=={is_disabled}")
    return is_disabled


def parse_contents(contents, filename, date=None):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            # data_importer = importer.DataImporter(filename, record_type)
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception("Invalid file type.")
    except Exception as e:
        print(e)
        df = pd.DataFrame(
            {"There was an error processing this file": f"Error message: {str(e)}"},
            index=[0],
        )
        # return html.Div([
        #     f'There was an error processing this file.\n{e}'
        # ])

    return df


def preview_content(contents, filename, date):
    df = parse_contents(contents, filename, date)
    col_name_dict = [{"name": i, "id": i} for i in df.columns]
    return html.Div(
        [
            html.H6([filename, "  Timestamp:", datetime.datetime.fromtimestamp(date)]),
            dash_table.DataTable(df.to_dict("records"), col_name_dict),
            html.Hr(style={"height": "2px", "margin": "5px"}),
            # For debugging, display the raw contents provided by the web browser
            html.Div("Raw Content"),
            html.Pre([contents[0:300] + "   ...  "],
                style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            ),
        ]
    )


def import_dataframe(
    contents, filename, record_type, is_append, db_table: field_table.FieldTable
):
    #     content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string)

    try:
        df = parse_contents(contents, filename)
        data_importer = importer.DataImporter(df, record_type)
        data_importer.parse_df_to_dynamo_json(append=is_append, db_table=db_table)
        import_len = db_table.import_batch_field_data_res(
            data_importer
        )  # How to test this effectively?
    except Exception as e:
        print(e)
        return html.Div([f"There was an error processing this file.  {e}"])

    return html.Div(
        [
            html.H5(filename),
            # html.H6(datetime.datetime.fromtimestamp(date)),
            dcc.Markdown(
                f"Imported **{import_len}** rows and store in info={record_type}."
            ),
            # dash_table.DataTable(df.to_dict('records'),
            #     [{'name': i, 'id': i} for i in df.columns]
            # ),
        ]
    )


@dash.callback(
    Output("output-data-upload", "children"),
    Input("btn_import", "n_clicks"),
    Input("btn_preview", "n_clicks"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    State("importing_type", "value"),
    State("import_is_append", "value"),
    State("store_db_info", "data"),
    prevent_initial_call=True,
)
def update_output(
    btn_1,
    btn_2,
    list_of_contents,
    list_of_names,
    list_of_dates,
    record_type,
    is_append,
    db_info,
):
    children = []
    is_append = eval(is_append)
    if list_of_contents is not None:
        if "btn_preview" == ctx.triggered_id:
            children = [
                preview_content(c, n, d)
                for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
            ]
        elif "btn_import" == ctx.triggered_id:
            # if not db_info["db_status"] or not db_info["table_status"]:
            #     children = ([html.H5("Database not available")])
            db_table = app_db.connect_db_table(db_info)
            children = [
                import_dataframe(c, n, record_type, is_append, db_table)
                for c, n, in zip(list_of_contents, list_of_names)
            ]
            # else:
            # children = html.Div([html.H5("Please enter data type")])

    return children


@dash.callback(
    Output("btn_delete_record_type", "disabled"),
    Input("text_delete_record_type", "value"),
    Input("text_delete_record_type", "required"),
)
def is_btn_delete_disabled(record_type, is_required):
    is_disabled = True
    if record_type is not None:
        is_disabled = False

    return is_disabled


@dash.callback(
    Output("md_delete_output", "children"),
    Input("btn_delete_record_type", "n_clicks"),
    State("text_delete_record_type", "value"),
    State("store_db_info", "data"),
    prevent_initial_call=True,
)
def delete_record_type(btn_delete, record_type, db_info):
    if record_type is None:
        raise PreventUpdate
    try:
        md = app_db.delete_all_items_record_type(db_info, record_type)
    except Exception as e:
        md = f"Please enter a record_type to delete all items. {e}"
    return md
