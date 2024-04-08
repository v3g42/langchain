PLAN_OUTPUT_FORMAT = """
```json

    {
      success: true,
      error_reason: "This query is not relevant to the provided data",
      steps: [
            {
                "action": "tool name",
                "description": "description of the task"
                "explanation": "explanation of the task",
            },
            ...
        ]
    }
    
```
"""


TOP_TXNS_REGION = """
SELECT * from users u, count(t.id) as txn_count
join transactions t on t.user_id = u.id
where u.region = {{region}}
group by u.id 
order by txn_count desc limit 20
"""


cube_name = "top_users"
dimension_name="category"
ENDPOINT_EXAMPLE=f"""
For example: a cube with name ${cube_name} is having the following predefined SQL 
{TOP_TXNS_REGION}.
To get data from this cube, you need to invoke endpoint/{cube_name} with method POST and body as below:
    {{
        "params": {{region: 'USA'}},
        "paginate": true,
        "page_size": 10,
        "offset": 0
    }}

Response will be json object with properties defined in dimensions
"""


RAW_QUERY_EXAMPLE = f"""
For example: You have cubes with names [users, customers, transactions].
        To get data from these cubes, you need to write SQL query to fetch data from these tables.
        For instance, you can write query as below:
            SELECT * FROM {cube_name} WHERE user.{dimension_name} = {{any value base on dimmension type}} LIMIT 10 OFFSET 0
            
            - Replace {{any value base on dimmension type}} with actual value based on dimension type.
            - Using Clickhouse SQL syntax to write query.
            - Get only collumn you need by using SELECT clause.
            - Pagination is supported by using LIMIT and OFFSET in the query.
            - Aggregation can be done by using GROUP BY and aggregate functions.
            - Filtering can be done by using WHERE clause.
            - Sorting can be done by using ORDER BY clause.
    
        Then execute the query to get data from the table by invoking endpoint /execute with method POST and body as below:
        {{
            "query": "your query here",
        }}
        Response will be json object with properties defined in dimensions
"""


DOZER_QUERY_PLAN_PROMPT = """
UNDERSTAND SEMANTICS OF CUBE

Here is the semantics  of the available data in YAML format representing OLAP cubes:
{semantics}

As you can see in the structure, there's 2 kind of cubes:
- Predefined SQL Query Cubes: Cubes with "sql" property. Feature optimized SQL queries for specific analytical tasks. Looking at sql query, you could also undertand the how to data is fetched by that query. These may need input parameters and support pagination and filtering.
    {endpoint_example} 
- Raw Table Cubes: Cubes without "sql" property, Represent raw database tables, useful for constructing custom SQL queries. These cubes can be used to fetch data by writing query for specific analytics tasks.
    {raw_query_example}

Your goal is to understand the semantics of the cube and brokendown the question into smaller tasks to get the data from the cube to answer the question.
 - A task is step invoke one of available tools
 - a planning response if successful is a list of tasks to be able get the data from the cube to answer the question.
 - a planning response if not successful returns success false with a valid reason and empty steps.                      
                      

Available tools:
  {tools_available_description}

Your planning response should be in JSON format with properties as below:
  {format_response}

QUESTION: {question}
Response: response in JSON format as described above
"""


DOZER_GENERATE_QUERY_RESPONSE = """
```json
    {
        "body": {
            "query": "your generated query"
        },
        "path: "execute",
        "description": "description of the query"
        "explanation": "explanation of the query"
    }
```
"""

DOZER_GENERATE_QUERY="""
UNDERSTAND SEMANTICS OF CUBE
Here is the semantics of the cube:
{raw_tables_yaml}

Each cube is a table with dimensions. Your task is to generate a valid Clickhouse SQL query to get data from these cubes.
    - Using Clickhouse SQL syntax to write query
    - Get only column you need by using SELECT clause. Only include columns that relevant to the question and valuable to natural response for user to understand.
    - Pagination is supported by using LIMIT and OFFSET in the query. Let assume that the page_size is 100 and offset is 0.
    - Aggregation can be done by using GROUP BY and aggregate functions.
    - Filtering can be done by using WHERE clause.
    - Sorting can be done by using ORDER BY clause.
    - When choosing columns to include in the SELECT statement, ensure that if any column is being aggregated (e.g., using SUM, AVG, etc.), all other non-aggregated columns are either aggregated too or included in the GROUP BY clause.

QUESTION: {input}
Response: SQL query as a string without any additional information.
"""

