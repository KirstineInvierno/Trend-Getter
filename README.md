# TrendGetter Project

## Summary
In a world driven by reputation and real-time information, individuals and brands need timely insights into how topics and trends are evolving across the web. While platforms like Google Trends and Bluesky hold valuable data about public interest and sentiment, accessing and interpreting this data requires technical expertise. As a result, most people are left relying on outdated, second-hand insights. There is a clear need for an accessible tool that empowers anyone to track, compare, and stay informed about the topics they care about — in real time.

## Project objective
Create a tool that allows users to select topics/tags on key sites (Google Trends, BlueSky) and monitor their growth/interest over time.

## Deliverables
- Users will be able to submit topics to be tracked by the service.
- Sites/feeds will be monitored frequently for mentions of the topics and related activity, storing all relevant data in a database.
- Users will be able to access a live dashboard of topics exploring:
    - Interest/activity over time
    - Comparison of keywords/topics against one another
    - Sentiment and related terms
- Notifications for changes in activity will be sent to subscribers.

## Architecture

## ERD

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

## Technology
- Python - pandas, psycopg2, pylint, pytest
- AWS - RDS
- Docker
- Terraform
- PostgreSQL
- Streamlit
- CI/CD
