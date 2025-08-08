# 📈 TrendGetter

 ![alt text for screen readers](./trendgettertransparent.png "Architecture Diagram")

## Summary
In a world driven by reputation and real-time information, individuals and brands need timely insights into how topics and trends are evolving across the web. While platforms like Google Trends and Bluesky hold valuable data about public interest, accessing and interpreting this data requires technical expertise. As a result, most people are left relying on outdated, second-hand insights. There is a clear need for an accessible tool that empowers anyone to track, compare, and stay informed about the topics they care about — in real time.

TrendGetter is a trend monitoring and analytics tool that allows users to select topics and monitor their growth, sentiment, and related activity over time. It continuously collects data from targeted feeds, processes it, and stores results in a database, which can be explored via a live dashboard.

## Deliverables
- Users will be able to submit topics to be tracked by the service.
- Sites/feeds will be monitored frequently for mentions of the topics and related activity, storing all relevant data in a database.
- Users will be able to access a live dashboard (hosted on AWS) exploring:
    - Interest/activity of topics over time
    - Comparison of keywords/topics against one another
    - Topic sentiment
- Notifications for changes in activity will be sent to subscribers.

## Architecture
 ### System Architecture Diagram
 ![alt text for screen readers](./architecture.png "Architecture Diagram")

 ### Decisions
 #### Data Storage
 - The service requires the keeping of records of every message which hits one of the tracked topics, and the corresponding sentiment. 
 - Further, data is required from users about which topics they are subscribed to.
    - For this, a Postgres RDS instance is used, due to the automatic scaling and the volume of transactional queries required for the maintenance of user subscription records.
    - While the columnar queries generally used to produce visualisations are more expensive than a data-warehouse-style storage solution, we believe that the RDS will be better value overall.

 #### Extracting the data
 - To keep up with the volume of messages provided by the BlueSky firehose (around 4500/minute), a batch processing pipeline is used to extract and transform the data, slightly sacrificing the age of data in favour of performance and cost.
 - An EC2 instance stores every message posted on BlueSky and dumps the raw JSON into an S3 bucket.
 - This S3 bucket provides a cheap, unstructured data storage solution to store the unclean message data.
 - Every ten minutes, a Lambda function transforms the previous ten minutes' messages (around 45,000) into data for the RDS, ready to be visualised.

 #### Notification Service
 - Using the user data in the RDS, a step function containing the ETL Lambda function triggers another Lambda function which checks for topic thresholds set by the user. 
 - Once the threshold has been met, the user is notified via an SES.

 #### Displaying the Data and User Interface
 - A Streamlit dashboard deployed on an AWS ECS is used for the user facing aspect of TrendGetter.
 - This dashboard contains visualisations of both Google Trends data and BlueSky posts.
 - It also allows users to subscribe and unsubscribe from notifications for different topics, and request new topics to be tracked.
 - Streamlit was chosen due to the visually accessible user interfaces that can be created, as well as its integration with python code which allowed easy interaction with the rest of the architecture when required by a user action.

 ## Entity Relationship Diagram
 ![alt text for screen readers](./tg_erd.png "Architecture Diagram")
 - This is the ERD which represents the setup of the user/mention data in the Postgres RDS.
 - The database has been normalised to 3NF to avoid the keeping of redundant data.

## Set-up
- You must have the following repository secrets on GitHub:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - DB_HOST
    - DB_NAME
    - DB_PASSWORD
    - DB_PORT
    - DB_USER
    - TF_VAR_DB_PASSWORD
    - TF_VAR_DB_USERNAME

## Files explained

## CI/CD
- In order to smoothly develop and integrate changes to our service, we made use of github actions.
- Firstly, we used a workflow which automatically ran test files and pylint before any merge to the main branch, only allowing the merge to go ahead if the checks passed satisfactorily. This prevented bad quality, potentially disruptive code from being added to the main branch.
- We also implemented a Terraform which stored the current state of our cloud system and automatically applied any changes we merged to the main branch.

## Technology
- Python - pandas, psycopg2, pylint, pytest
- AWS - RDS, EC2, ECS, ECR, S3, Step Function, Lambda Function, SES, CloudWatch
- Docker
- Terraform
- PostgreSQL
- Streamlit
- CI/CD
