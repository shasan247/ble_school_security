#username - ble
#pass - dmabd987
#dbname - dmabdcom_school_security
#host - dma-bd.com
import pymysql as MySQLdb

class Query:

    # Global variables
    
    # Connection string for connecting to MySQL database
    connection_string = ''

    # This will hold the cursor
    connection_cursor = ''


    #-----------------------------------------
    # Static
    # Same connection string for all instances
    @staticmethod
    # A single connection with database
    # For all threads
    def create_connection():

        try:

            # Access these global variables
            global connection_cursor
            global connection_string

            # A string that specifies information about a data source and the means of connecting to it
            # It is passed in code to an underlying driver or provider in order to initiate the connection
            #connection_string = MySQLdb.connect(host = 'localhost', port = 3306, user = 'root2', passwd = '123', db = 'test_wasa')
            
                        
            connection_string = MySQLdb.connect(host = 'dma-bd.com', port = 3306, user = 'dmabdcom_ble', passwd = 'dmabd987', db = 'dmabdcom_school_security')
            
            #connection_string = MySQLdb.connect(host = 'localhost', port = 3306, user = 'root', passwd = 'root', db = 'saklyn_school_security')
            # Database cursor is a control structure that enables traversal over the records in a database
            
            #connection_string = MySQLdb.connect(host = 'dma-bd.com', port = 3306, user = 'dmabdcom_ble_pro', passwd = 'dmabd987', db = 'dmabdcom_db_ble_school_project')
            
            #connection_string = MySQLdb.connect(host = 'dma-bd.com', port = 3306, user = 'dmabdcom_wtank', passwd = 'dmabd987', db = 'dmabdcom_sauditank')
            connection_cursor = connection_string.cursor()


            print ("Database connection created")

            return connection_string

        except MySQLdb.Error as e:

            print ("Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Afterwards resume other operations
            Query.create_connection()
    #-----------------------------------------
    

    #-----------------------------------------
    # Responsible for checking if a specific record exists in the database
    @staticmethod
    def check(sql_query): 

        try:
            
            # Executes sql query
            connection_cursor.execute(sql_query[0], sql_query[1])

            # Get a record from database
            return connection_cursor.fetchone()
          
        except MySQLdb.Error as e:

            print (" Check Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Query.check(sql_query)
    #-----------------------------------------

    @staticmethod
    def get_a_record(sql_query): 


        # print (connection_cursor)

        try:
            
            # Executes sql query
            #result = connection_cursor.execute(sql_query[0], sql_query[1])
            connection_cursor.execute(sql_query)
            # Get a record from database
            
            last_record_data = connection_cursor.fetchone()

            return last_record_data
          
        except MySQLdb.Error as e:

            print ("Check Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Querycheck(sql_query)
    #-----------------------------------------

    @staticmethod
    def get_a_record2(sql_query): 


        # print (connection_cursor)

        try:
            
            # Executes sql query
            connection_cursor.execute(sql_query[0], sql_query[1])
            #connection_cursor.execute(sql_query)
            # Get a record from database
            
            last_record_data = connection_cursor.fetchone()

            return last_record_data
          
        except MySQLdb.Error as e:

            print ("Check Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Querycheck(sql_query)
    #-----------------------------------------

    #-----------------------------------------

    @staticmethod
    def get_all_record(sql_query): 


        # print (connection_cursor)

        try:
            
            # Executes sql query
            #connection_cursor.execute(sql_query[0], sql_query[1])
            connection_cursor.execute(sql_query)
            # Get all records from database
            
            all_record_data = connection_cursor.fetchall()
            print(all_record_data)

            return all_record_data
          
        except MySQLdb.Error as e:

            print ("Check Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Querycheck(sql_query)
    #-----------------------------------------
    #-----------------------------------------

    @staticmethod
    def get_all_record2(sql_query): 


        # print (connection_cursor)

        try:
            
            # Executes sql query
            connection_cursor.execute(sql_query[0], sql_query[1])
            #connection_cursor.execute(sql_query)
            # Get all records from database
            
            all_record_data = connection_cursor.fetchall()

            return all_record_data
          
        except MySQLdb.Error as e:

            print ("Check Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Querycheck(sql_query)
    #-----------------------------------------

    #-----------------------------------------
    # Responsible for inserting a new record in the database
    @staticmethod
    def commit(sql_query):	

    	try:
            
    		# Executes sql query
            connection_cursor.execute(sql_query[0], sql_query[1])

            # Inserts/Updates a record into database
            result = connection_string.commit()
            print ("Result")
            print (result)

            return result
          
    	except MySQLdb.Error as e:

            print ("Commit Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Query.commit(sql_query)
    #----------------------------------------


    #-----------------------------------------
    # Responsible for inserting a new record in the database
    @staticmethod
    def close():	

    	try:
            
    		# Close connection cursor
            connection_cursor.close()
  
            # Close connection string
            connection_string.close()

            print ("Connection Closed")
          
    	except MySQLdb.Error as e:

            print ("Close Error !!!")

            # Print the specific error
            print (e)

            # Try to connect to database
            # Query.create_connection()

            # Afterwards resume other operations
            # Query.commit(sql_query)
        #----------------------------------------


        

