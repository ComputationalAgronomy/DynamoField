
import dash
from dash import ctx, dash_table, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate


from dynamofield import app_db, app_style
from dynamofield.db import aws_utils

# @dash.callback(
#     Output('get_item_count', 'children'),
#     Input('tabs-function', 'value'),
#     State('store_db_info', 'data'),
# )
# def update_item_count_import(x, info):
#     return update_item_count(info)


# @dash.callback(
#     Output('get_item_count_db', 'children'),
#     Input('tabs-function', 'value'),
#     State('store_db_info', 'data'),
# )
# def update_item_count_db(x, info):
#     return update_item_count(info)

@dash.callback(
    Output("db_regions", "options"),
    Input('btn_connect_db', 'n_clicks')
)
def list_regions(btn):
    return aws_utils.list_all_regions()


@dash.callback(
    Output('db_table_md', 'children'),
    Output("dt_list_table", "columns"),
    Output("dt_list_table", "data"),
    Input('btn_create_table', 'n_clicks'),
    Input('btn_list_tables', 'n_clicks'),
    Input('btn_delete_table', 'n_clicks'),
    State('store_db_info', 'data'),
    State('new_table_name', 'value'),
    State('text_delete_tablename', 'value'),
)
def add_new_table(btn_create, btn_list, btn_delete,
                  db_info, tablename, delete_tablename):
    print("Table info:", tablename, delete_tablename, db_info, dash.callback_context.triggered_id)
    if db_info is None or not db_info["db_status"]:
        raise PreventUpdate
    md = ""  # "Database offline."
    columns = None
    data = None
    list_tables = app_db.db_list_table(db_info)
    if dash.callback_context.triggered_id == 'btn_create_table':
        # if tablename is None or len(tablename) == 0:
        #     md = "Please enter a name for the new table (min length > 3)."
        #     print(md)
        #     raise PreventUpdate
        # # TODO: Check table not already exist
        try:
            md = app_db.create_new_table(db_info, tablename)
        except Exception as e:
            md = f"Please enter a name for the new table (min length > 3).<br>{e}"
    elif dash.callback_context.triggered_id == 'btn_list_tables':
        # md = f"List of available tables:\n<br>"
        # md = "" #+= "<br> - ".join([t.name for t in list_tables])
        data = [{"table_name": t.name} for t in list_tables]
        table_names = [t.name for t in list_tables]
        columns = [{"name": "Table name", "id": "table_name"}]
    elif dash.callback_context.triggered_id == 'btn_delete_table':
        # TODO: Pop up confirmation message

        try:
            md = app_db.delete_existing_table(db_info, delete_tablename)
        except Exception as e:
            md = f"Please enter a name to delete table.<br>{e}"
        print(md)
    return md, columns, data






# @dash.callback(
#     Output("dt_list_table", "columns"),
#     Output("dt_list_table", "data"),

#     State('store_db_info', 'data'),
#     prevent_initial_call=True,
# )
# def update_list_table(btn_list, db_info):
#     print(db_info, dash.callback_context.triggered_id)
#     columns = None
#     data = None
#     if db_info["db_status"]:






def check_status(status):
    if status:
        colour = "green"
        status_text = "ONLINE"
    else:
        colour = "red"
        status_text = "OFFLINE"
    status_html = status_template_text(colour, status_text)
    return status_html


def status_template_text(colour, text):
    status_html = f"""<b><span style="color: {colour}">{text}</span></b>"""
    return status_html




@dash.callback(
    Output("db_markdown", "children"),
    Input("refresh-graph-interval", "n_intervals"),
    Input('store_db_info', 'data'),
)
def update_status_interval(n, db_info):
    # if db_info is None:
    #     raise PreventUpdate
    try:
        md_db = check_status(db_info["db_status"])
        md_table = check_status(db_info["table_status"])
    except TypeError:
        md_db = check_status(False)
        md_table = check_status(False)
    md_output = f"""<p style="margin: 0;font-size:20pt">
    Database status: {md_db}
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    Table status: {md_table}
    </p>"""

    return md_output






@dash.callback(
    Output('db_endpoint', 'value'),
    Output('db_table_name', 'value'),
    Output('store_db_info', 'data'),
    Output("loading_update_db", "children"),
    Input('btn_connect_db', 'n_clicks'),
    Input("db_regions", "value"),
    State('db_endpoint', 'value'),
    State('db_table_name', 'value'),
    State('store_db_info', 'data'),
    # State('store_endpoint', 'data'),
    # State('store_table_name', 'data'),
    running=[
        (Output("btn_connect_db", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def update_db_status(btn_connect_db, region, ep, name, info):
    # if not ep:
    #     raise PreventUpdate
    endpoint = None
    table_name = None
    if dash.callback_context.triggered_id == 'db_regions':
        print("Update region: {region}")
        ep = aws_utils.get_endpoint(region)

    try:
        m_ep = info["endpoint"]
        m_name = info["table_name"]
    except Exception:
        m_ep = None
        m_name = None
    if ep:
        endpoint = ep
    elif m_ep:
        endpoint = m_ep
    if name:
        table_name = name
    elif m_name:
        table_name = m_name

    if dash.callback_context.triggered_id == 'btn_connect_db':

        print(f"Current status: ={ep}=={name}=\tmemory:{m_ep}=={m_name}==\t=={info}")
        if ep == m_ep and name == m_name:
            print("No update")
            # raise PreventUpdate
        db_status = False
        table_status = False
        if endpoint is not None:
            dynamodb_server = app_db.init_dynamodb(endpoint)
            db_status = dynamodb_server.is_online
        if db_status and table_name is not None:
            table_status = dynamodb_server.is_table_exist(table_name)
        print(f"Connect DB: {endpoint} {table_name}\tStatus:\t {db_status} {table_status}")

        info = {
            "endpoint": endpoint,
            "table_name": table_name,
            "db_status": db_status,
            "table_status": table_status,
            endpoint: db_status,
            table_name: table_status
        }
    return endpoint, table_name, info, True





# @dash.callback(
#     Output('btn_db_start', 'children'),
#     Input('btn_db_start', 'n_clicks')
# )
# def start_db(n_clicks):
#     start_dynamodb_server()