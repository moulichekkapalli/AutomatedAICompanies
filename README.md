# UC1 Automated Identification of AI Companies

Welcome to Automated Identification of AI Companies. A tool to automatically identify companies providing AI services assisting
in product creation. The required information to run the tool on local machine is provided below.

## Prerequisites

1. Python 3.8
2. PostgreSQL ([Download](https://www.pgadmin.org/download/))
3. IDE of your choice (recommendation: Visual Studio Code) 

## Installation 
1. Clone the repository using below command

   `git clone https://gitlab.cc-asp.fraunhofer.de/ai4se2/uc1-automated-identification-of-ai-companies.git`

2. Open the new terminal where the repo is cloned and install all the packages using the command

   `pip install -r requirements.txt`

4. Create the database using the PgAdmin tool
   
   - Open pgadmin 
   - Set the master password 
   - Right click on server > Create server
   - General > name : PostgreSQL <version_number>
   - Connection > Hostname: localhost
   - Connection > Port: 5432
   - Connection > Username: postgres
   - Click save
   - Right click Databases > Create > database
   - General > Database: companiesdata
   - Click save
   - Create table > name: companyinfo
   - Add columns 

      | name | datatype | not null |
      | ------ | ------ | ------ |
      | title | text | ------ |
      | url | text | yes |
      | extracteddata | text | yes |
      | category | text | yes |
      | summary | text | ------ |
      | created_on | timestamp without timezone | yes |
   - Click save 



5. Create .env in your root folder as per env-sample

6. Run the server

   `flask run`

6. The application should run on  http://127.0.0.1:10050/

Note: If you get any error related to package installation, try to install it manually using `pip install <package_name>`or by using the conda terminal



