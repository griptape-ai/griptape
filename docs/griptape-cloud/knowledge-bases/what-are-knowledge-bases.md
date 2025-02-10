# What are Knowledge Bases?

Griptape Knowledge Bases are collections of Data Sources that applications can query to retrieve information. They give you control over which Data Sources can be accessed, as well as how the data can be retrieved. Once you have created the Data Source(s) you need, simply add them to a Knowledge Base so that your application, such as a Griptape Assistant or Agent, can access it.

When you add Data Sources to a Knowledge Base, your data is upserted to a database that is optimized for LLMs to retrieve quickly and process efficiently. Typically, this requires maintaining a database to store your data, operating a data ingestion (ETL) pipeline to collect it, and vending a query endpoint to make it available. Griptape Cloud automates this process for you.