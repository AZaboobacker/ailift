import os
import boto3
import subprocess
import uuid

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET = os.getenv('S3_BUCKET')

# Initialize Boto3 clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
eb_client = boto3.client('elasticbeanstalk', region_name=AWS_REGION)

def create_s3_bucket(bucket_name):
    existing_buckets = s3_client.list_buckets().get('Buckets')
    if bucket_name not in [bucket['Name'] for bucket in existing_buckets]:
        s3_client.create_bucket(Bucket=bucket_name)

def upload_to_s3(identifier):
    file_name = f"{identifier}.zip"
    subprocess.run(['zip', '-r', file_name, f"{identifier}-app"])
    s3_client.upload_file(file_name, S3_BUCKET, file_name)
    return file_name

def create_eb_application(application_name):
    applications = eb_client.describe_applications()['Applications']
    if application_name not in [app['ApplicationName'] for app in applications]:
        eb_client.create_application(ApplicationName=application_name)

def create_eb_application_version(application_name, version_label, s3_key):
    eb_client.create_application_version(
        ApplicationName=application_name,
        VersionLabel=version_label,
        SourceBundle={
            'S3Bucket': S3_BUCKET,
            'S3Key': s3_key
        }
    )

def create_eb_environment(application_name, environment_name, version_label):
    environments = eb_client.describe_environments(ApplicationName=application_name)['Environments']
    if environment_name not in [env['EnvironmentName'] for env in environments]:
        eb_client.create_environment(
            ApplicationName=application_name,
            EnvironmentName=environment_name,
            VersionLabel=version_label,
            SolutionStackName='64bit Amazon Linux 2 v3.1.5 running Python 3.8'
        )
    else:
        eb_client.update_environment(
            EnvironmentName=environment_name,
            VersionLabel=version_label
        )

def get_environment_url(environment_name):
    environments = eb_client.describe_environments(EnvironmentNames=[environment_name])['Environments']
    if environments:
        return environments[0]['CNAME']

def main():
    unique_id = str(uuid.uuid4())
    identifier = unique_id

    # Create a directory for the app
    directory = f"{identifier}-app"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Copy contents from the current branch to the directory
    subprocess.run(['cp', '-r', '.', directory])

    create_s3_bucket(S3_BUCKET)
    s3_key = upload_to_s3(identifier)
    application_name = f"{identifier}-app"
    environment_name = f"{identifier}-env"
    version_label = identifier

    create_eb_application(application_name)
    create_eb_application_version(application_name, version_label, s3_key)
    create_eb_environment(application_name, environment_name, version_label)

    # Get the environment URL
    env_url = get_environment_url(environment_name)
    if env_url:
        print(f"The Streamlit app is deployed at: http://{env_url}")

if __name__ == '__main__':
    main()
