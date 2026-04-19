    #This dockerfile provides commands to build a container to run your project on AWS, since EC2 is not powerful enough to build the project
    #Python Image: 
    FROM python:3.12.2-slim 
    #Set the home variable 
    ENV HOME=/app
    #This replaces the database url in your .env file with the production database URL. The .env file is docker ignored (similar to a gitignore) so, it won't be available in production 
    ENV SQLALCHEMY_DATABASE_URI='REPLACE WITH YOUR PROD DATABASE URL' 
    #Set the current dirctory to app 
    WORKDIR /app
    #move the requirements.txt text file into the container 
    ADD ./requirements.txt ./requirements.txt
    #start a virtual environment and start it 
    RUN python -m venv venv
    RUN /bin/bash -c "source ./venv/bin/activate"
    #install the dependencies. Do not cache any from previous container builds 
    RUN pip install --no-cache-dir -r requirements.txt 
    #install open ssl -- this will allow your website to run on HTTPS and use SSL encryption rather than plain text 
    RUN apt-get update && apt-get install -y openssl
    #generate a self-signed SSL certificate for 365 days with the RSA hashing algorithm 
        #the "-nodes" option prevents encryption of the private key, -subj holds info for ssl certificate 
        #note - when entering your ec2 ipv4 address, do not include either https or http. Should be something like ec2-3-145-113-82.us-east-2.compute.amazonaws.com (note that there is not an instance of http or https in this string)
    RUN openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/key.pem -out /etc/ssl/certs/cert.pem -days 365 -nodes -subj "/C=US/ST=MA/L=Worcester/O=WPI/CN=[INSERT EC2 URL HERE]"
    #copy files from local machine to the app directory 
    COPY . /app
    #set flask to run the production environment and update path variable 
    ENV FLASK_ENV=production
    ENV PATH=/app/.local/bin:$PATH    
    #expose the port on which the app will accept connections inside the container 
    EXPOSE 3001
    #upgrade the database using the migrations and run the application on port 3001 with the SSL key and certificate
    CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=3001 --cert=/etc/ssl/certs/cert.pem --key=/etc/ssl/private/key.pem" ]