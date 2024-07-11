name: Deploy to AWS Elastic Beanstalk

on:
  push:
    paths:
      - '**/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 2  # Ensure we fetch enough history to access HEAD^

    - name: Find new folder
      id: newfolder
      run: |
        git fetch --depth=2
        NEW_FOLDER=$(git diff --name-only HEAD^ HEAD | grep -oE '^[^/]+/' | sort -u | head -n 1)
        echo "NEW_FOLDER=${NEW_FOLDER}" >> $GITHUB_ENV
      shell: bash

    - name: Debug new folder
      run: echo "New folder is: ${{ env.NEW_FOLDER }}"
      shell: bash

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        cd ${{ env.NEW_FOLDER }}
        if [ -f requirements.txt ]; then
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        else
          echo "No requirements.txt found in the new folder."
          exit 1
        fi
      shell: bash

    - name: Deploy to AWS Elastic Beanstalk
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_REGION: ${{ secrets.AWS_REGION }}
        S3_BUCKET: ${{ secrets.S3_BUCKET }}
      run: |
        UNIQUE_ID=$(uuidgen)
        DIRECTORY="${UNIQUE_ID}-app"
        
        # Create a directory for the app
        mkdir $DIRECTORY

        # Copy Streamlit app code into the directory
        cp ${{ env.NEW_FOLDER }}streamlit.py $DIRECTORY/app.py
        cp ${{ env.NEW_FOLDER }}requirements.txt $DIRECTORY/

        # Navigate to the app directory
        cd $DIRECTORY

        # Create a Procfile for the app
        echo "web: streamlit run app.py --server.port \$PORT" > Procfile

        # Zip the application
        cd ..
        zip -r ${UNIQUE_ID}.zip $DIRECTORY

        # Upload the application to S3
        aws s3 cp ${UNIQUE_ID}.zip s3://${S3_BUCKET}/${UNIQUE_ID}.zip

        # Create an Elastic Beanstalk application
        aws elasticbeanstalk create-application --application-name "${UNIQUE_ID}-app"

        # Create an Elastic Beanstalk application version
        aws elasticbeanstalk create-application-version --application-name "${UNIQUE_ID}-app" --version-label "${UNIQUE_ID}" --source-bundle S3Bucket=${S3_BUCKET},S3Key=${UNIQUE_ID}.zip

        # Create an Elastic Beanstalk environment
        aws elasticbeanstalk create-environment --application-name "${UNIQUE_ID}-app" --environment-name "${UNIQUE_ID}-env" --version-label "${UNIQUE_ID}" --solution-stack-name "64bit Amazon Linux 2 v3.4.5 running Python 3.8"

        # Get the environment URL
        ENV_URL=$(aws elasticbeanstalk describe-environments --application-name "${UNIQUE_ID}-app" --environment-names "${UNIQUE_ID}-env" --query "Environments[0].CNAME" --output text)
        echo "ENV_URL=http://$ENV_URL" >> $GITHUB_ENV

    - name: Print URL
      run: echo "The Streamlit app is deployed at: ${{ env.ENV_URL }}"
      shell: bash
