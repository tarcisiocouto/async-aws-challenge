# Project Overview

This project is a Django application that implements an asynchronous product catalog using AWS services. The goal is to receive product information via a REST API, process it asynchronously using a message queue (SQS), and store it in a database (DynamoDB). The project is based on the "AsyncCatalog" challenge described in `CHALLENGE.md`.

**Key Technologies:**

*   **Backend:** Python, Django, Django REST Framework
*   **AWS Services:** API Gateway, Lambda, SQS, DynamoDB, S3
*   **AWS SDK:** `boto3`

**Architecture:**

1.  A `POST` request with product data is sent to a Django REST Framework endpoint.
2.  The Django view calls a service that triggers an AWS Lambda function (`CreateProductProcessor`).
3.  The `CreateProductProcessor` Lambda function sends a message containing the product data to an SQS queue (`product-queue`).
4.  A second Lambda function (`ProductSaverWorker`) is triggered by messages in the SQS queue.
5.  The `ProductSaverWorker` function processes the message, generates a unique ID for the product, and saves the product data to a DynamoDB table (`ProductTable`).
6.  The `ProductSaverWorker` also generates a report and uploads it to an S3 bucket.

# Building and Running

**1. Install Dependencies:**

```bash
pip install -r requirements.txt
```

**2. Configure Environment Variables:**

Create a `.env` file in the project root and add the necessary AWS credentials and other configuration:

```
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
AWS_REGION=<YOUR_AWS_REGION>
AWS_SQS_QUEUE_URL=<YOUR_SQS_QUEUE_URL>
```

**3. Run the Django Development Server:**

```bash
python manage.py runserver
```

**4. Deploying Lambda Functions:**

The Lambda functions in the `lambda/` directory need to be deployed to AWS. The `CHALLENGE.md` file provides instructions on how to set up the necessary AWS resources.

# Development Conventions

*   The main application logic is in the `challenge` Django app.
*   The `CHALLENGE.md` file is the primary source of requirements and architecture for this project.
*   Use `boto3` to interact with AWS services.
*   Environment variables are used for configuration. See `app/settings.py` and `lambda/CreateProductProcessor.py`.
*   The `Product` model is defined in `challenge/models.py`.
*   The API endpoint is defined in `challenge/views.py` and `challenge/urls.py`.
