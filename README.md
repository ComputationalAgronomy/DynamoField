# Dynamofield: Flexible field trial database

Dynamofield is a highly customizable database scheme designed to store field trial data.
Frontend web interface.
Backend NoSQL database powered by AWS DynamoDB.


## Requirements and setup

Please make sure the following programs are installed.
- [Python 3.9 or higher](https://www.python.org/)
- [Java (JRE 8 or higher)](https://www.java.com)
- Option 1: Run the setup script
  - MacOS/Linux: `0_init.sh`
  - Windows: `0_init.bat`
- Option 2: Manually install dependencies
  - Install required Python libraries
    ```
    # MacOS/Linux - Terminal
    pip3 install -r requirements.txt
    # OR
    pip install -r requirements.txt

    # Windows - Command Prompt
    py -m pip install -r requirements.txt
    ```
    If `pip/pip3` is not available, please install it from [pip](https://pip.pypa.io/en/stable/).
   - **DynamoDB**
     - Option A: **DynamoDB Local version**
           - Download and uncompress [DynamoDB Local](https://d1ni2b6xgvw0s0.cloudfront.net/dynamodb_local_latest.zip)
     - Option B: **DynamoDB on AWS** (TODO: unfinished section)
        - AWS Account
        - Setup DynamoDB on AWS: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SettingUp.DynamoWebService.html



### Getting started with dynamofield
1. Download the latest version of **dynamofield** from the `release` page form GitHub
   - Alternatively, `git clone` the latest version from the `main` branch.

2. Starts DynamoDB
   - Option 1: Execute startup script.
     - MacOS/Linux: `1_start_dynamodb.sh`
     - Windows: `1_start_dynamodb.bat`
   - Option 2: Manually starts DynamoDB Local
    ```
    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar [options]
    ```
    For more information on available options, run with the -help option:
    ```
    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -help
    ```
    - Option 3: AWS DynamoDB. (TODO)
      - AWS credential.
      - DynamoDB on AWS.

3. Start **dynamofield** and open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in the browser.
   - MacOS/Linux: `dynamofield.sh`
   - Windows: `dynamofield.bat`
   - Python:
      ```
      python3 app.py
      # OR
      py app.py
      ```


## Usage
There are a few core concepts and terminologies for **dynamofield**.

- **Database endpoint:** Each database server has a unique database endpoint address. The default endpoint for the local server is `http://localhost:8000/`

- **Data_table:** Each database can support multiple data_tables. Data_tables are independent of each other, and generally, they do not share data across multiple data_tables.
  - The typical usage for the data_table is storing unrelated trials at separate data_table, i.e., Yield trial for crops and Disease trial for fruit trees.

- **Field_Trial_ID:** Each trial (a plot with *n* rows and *m* columns) has a unique ID. This is a required column when importing data

- **data_type:** Within each trial, all information is categorized into multiple different **data_type**. There are no strict rules on how data is divided into categories; however, it is recommended that grouping data collected similar information together. For example;
  - Trt: Treatment information such as treatment id, treatment code, treatment name, etc.
  - Contact: Contact information include contact person, phone number, email address, company name, etc.
  - Plot: Yield for each plot, plot location, treatment id, etc.
  - Management: farm management throughout the trial season, including irrigation system, date and amount of fertilizer or pesticides applied, weed management, etc.

**Recommendation:** Keep the naming scheme consistent.


#### Database status panel
- Connect to the database endpoint. The default endpoint for the local server is `http://localhost:8000/`
- Enter data_table name.
  - If this is the first time using the database, please create a new data_table (i.e., `ft_db`) using `Create New Table`
  - Use "List Existing Tables" to get all tables in the current database endpoint.
- Click **Connect Database**
![DB_status](figures/db_status.png)


#### Import data panel
Import data in CSV format into the database
- Upload a CSV file
- Enter a **data_type**
- Choose between "Insert new data" or "Replace existing"
- Click **Import Data**

#### Query data panel
- Query data from the database
- Merge data from multiple **data_type**
- Plotting data
- Perform basic statistical analysis
- Export data




## Example
1. **Database Status panel:** Connect to the database and DB table.
   1. Database endpoint: `http://localhost:8000`
   2. Click **Connect Database**. The database status should change to **ONLINE**. If not, please make the endpoint is correct and DynamoDB local server is running.
   4. Enter `ft_db` in DB table name, and click "Connect Database" again. Both Database status and Table status should be **ONLINE**.
      - First time user. Enter `ft_db` at "Create a new table", and click **Create New Table**.

2. **Import data panel:**  Upload XX example dataset fromn the XXXX folder

    | filename | info_key/info_type |
    | --- | --- |
    | eg_plot.csv | plot |
    | eg_trt.csv | trt |
    | eg_seed.csv | seed |
    | eg_management | management|

    To import these tables into the database;
    1. Select one `CSV` file from the example folder.
    2. [Optional]: Use **Preview File** to check the contents
    3. Import info_type: Enter the corresponding value from the table.
    4. Select `Insert new data`, and this will append import data to the current database. On the other hand, `Replace existing` will overwrite the existing data for a given info_type
    5. Click **Import Data**

3. **Query database panel:** Fetch data
   1. Select trial ID: `trial_2B` and `trial_3C`
   2. Select **info_type**: `plot`, `trt`, and `seed`
   3. Click **Fetch Data**. This will query the database and fetch records that satisfy these filtering criteria.

4. **Merging multiple info_type**
   1. Select two **info_type**
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