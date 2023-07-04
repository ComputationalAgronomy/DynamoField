# DynomoDB field trial database 


Utilise the flexibilities of the NoSQL database to store dynamic (wide ranges) data format for any field trials.


## Requirements and setup

Please make sure the following programs are installed.
- [Python 3.9 or higher](https://www.python.org/)
  - Install required Python libraries
    ```
    # MacOS/Linux - Terminal
    pip3 install -r requirement.txt
    # OR
    pip install -r requirement.txt

    # Windows - Command Prompt
    py -m pip install -r requirements.txt
    ```
    If `pip/pip3` is not available, please install it from [pip](https://pip.pypa.io/en/stable/).

- **DynamoDB**
  - Option 1: **DynamoDB Local version**
      - [Java (JRE 8 or higher)](https://www.java.com)
      - [DynamoDB Local](https://d1ni2b6xgvw0s0.cloudfront.net/dynamodb_local_latest.zip)
  - Option 2: **DynamoDB on AWS** (TODO: unfinished section)
    - AWS Account
    - Setup DynamoDB on AWS: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SettingUp.DynamoWebService.html



### Getting started with dynamofield
1. Download the latest dynamofield from the `release` page form GitHub
   - Alternatively, clone the latest version from the `main` branch.

2. Start DynamoDB
   - Option 1: Start DynamoDB Local
    ```
    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar [options]
    ```
    For more information on available options, run with the -help option:
    ```
    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -help
    ```
    - Option 2: AWS DynamoDB. (TODO)
      - AWS credential.
      - DynamoDB on AWS is created

3. Start dynamofield, and open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in the browser.
```
python3 app.py
```


## Usage
There are XXX fundamental **** for using this 
- Each database server can support multiple data table. Data are completely independent between each data table.
- Each trial requires a unique ID
- For each trial, all information are stored under "data_type"

Recommendation: Keep your naming scheme consistent. 


#### Database status panel 
- Connect to the database endpoint. The default endpoint for the local server is `http://localhost:8000/`
- Enter DB table name. 
  - If this is the first time using the database, please create a new table using `Create New Table`
  - Use "List Existing Tables" to get all tables in the current database endpoint.
- Click **Connect Database** 

#### Import data panel
- Add data to the database
- Upload csv file
- Enter "data_type"
- Choose between append/overwrite


#### Query data panel
- Query data from the database
- Merge data from multiple data_type
- Plotting data
- Perform basic statistical analysis
- Export data




## Example
1. **Database Status panel:** Connect to the database and DB table.
   1. Database endpoint: `http://localhost:8000`
   2. Click **Connect Database**. The database status should change to **ONLINE**. If not, please make the endpoint is correct and DynamoDB local server is running.
   3. First time user. Enter `ft_db` at "Create a new table", and click **Create New Table**.
   4. Enter `ft_db` in DB table name, and click "Connect Database" again. Both Database status and Table status should be **ONLINE**.
   
2. **Import data panel:**  Upload XX example dataset fromn the XXXX folder

    | filename | info_key/data_type |
    | --- | --- |
    | eg_plot.csv | plot | 
    | eg_trt.csv | trt | 
    | eg_seed.csv | seed | 
    | eg_management | management| 

    To import these tables into the database, 
    1. Select one csv file from the example folder.
    1. [Optional]: Use **Preview File** to check the contents
    2. Import data_type: Enter the corresponting value from the table.
    3. Select `Insert new data`, this will append import data to the current database. On the other hand `Replace existing` will overwrite the existing data for a given data_type
    4. Click **Import Data**

3. **Query database panel:** Fetch data
   1. Select trial ID: `trial_2B` and `trial_3C`
   2. Select **data_type**: `plot`, `trt`, and `seed`
   3. Click **Fetch Data**. This will query the database and fetch records satisfy these searching criteria. 

4. **Merging multiple data_type**
   1. Select two "data_type"
   2. Select the columns you would like to merge.
   3. Click "Merge Tables"
   4. The merged table is displayed at the bottom.

5. **Plotting data:**
   1. Select `trt` for "x-axis", and `yield` "y-axis"
   2. Optional: Select "Colour by"
   3. Select the "plot type".
   4. Click "Plot Data"
   5.  Plotting panel with build-in figure control.

6. **Statistical analysis:**
   1.  Select `trt` for "Factor", and `yield` for "Response"
   2. Optional: Select "Slice by"
   3. Click "Analysis" or "Summary"
    
   


<!-- ## editable install 
https://github.com/pypa/pip/issues/7953 
```
pip3 install  --prefix=~/.local/ -e  .
``` -->



<!-- <details>
<summary>Tips for collapsed sections</summary>

### You can add a header

You can add text within a collapsed section. 

You can add an image or a code block, too.

```ruby
   puts "Hello World"
```

</details> -->