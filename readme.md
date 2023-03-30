# Deployment Setup

## Required Environment Dependent Variables

1. AWS_LOGS_GROUP
2. CPU_RESERVATION
3. MEMORY_RESERVATION
4. START_CMD
5. RDS_HOST
6. RDS_USERNAME
7. RDS_PASSWORD
8. RDS_DB_NAME
9. DJANGO_SETTINGS_MODULE
10. DJANGO_SECRET_KEY
11. AWS_S3_ACCESS_KEY_ID
12. AWS_S3_SECRET_ACCESS_KEY
13. AWS_SES_ACCESS_KEY_ID
14. AWS_SES_SECRET_ACCESS_KEY
15. SUPER_ADMIN_PASS
16. VERSION_TAG

## Required Variables

1. AWS_DEFAULT_REGION
2. AWS_SES_REGION_NAME
3. PROJECT_NAME
4. AWS_ACCESS_KEY_ID
5. AWS_SECRET_ACCESS_KEY
6. REPOSITORY_URL

## Django Required Setting Variables
On production these setting variables should not be `[""]` or `["*"]`
for security reason

1. [ALLOWED_HOSTS](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts)
2. [CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES](https://github.com/adamchainz/django-cors-headers#configuration)


# AWS Environment Setup

## Deployment Users and Permissions

1. Todo

## Setting up the Cloud

1. Create a VPC named "project"-"env"-vpc with default settings
   1. Ensure public vpc has **Enable auto-assign public IPv4 addressInfo** checked
2. Create a RDS instance named "project"-"env"-db
   1. Template free (Single DB - Burstable t3 micro)
   2. Drop storage down to 20GB
   3. Select your VPC
   4. Create new VPC security group rds-"project"-"env"-sg
   5. Pick a username eg pu-"project"-"env and password - write both down and put it in the bitbucket deployment variables.
   6. Select Password & IAM database
   7. Create. Wait then grab url. Put host, database name, username, and password into bitbucket deployment variables.
3. Create keypair eg "project"-"env"-kp using defaults. Save this pem file cause otherwise it's gone forever
4. Create ecs cluster
   1. Name it "project"-"env"
   2. If staging / dev you can choose **spot** otherwise suggest **demand**; lowest price is fine for **spot**
   3. For staging choose **t3-micro**
   4. Select the keypair you made in the previous step so you can remote into the instances later
   5. Choose your vpc and subnet from step 1
   6. New Security Grouop
   7. Create
5. Create loggroup
   1. Name /ecs/"project"-"env"
   2. Retention 1 week
6. Attempt deploy
   1. This should test everything up to this point and you should have a task definition added called "project"-:env":1 under your cluster.
7. Create service from the cluster page
   1. Launch type - ec2
   2. Choose cluster from step 4
   3. Service name - "project"-service
   4. Tasks should be at least 1
   5. Change minimum healthy to 50%
   6. Hit create and go to Step 2 (Configure Network)
   7. Choose Application Load Balancer
   8. Create an application load balancer named "project"-"env"-lb. Note if it has a warning it won't work later, and you'll have to fix it. Choose your public subnets
   9. Scheme should be Internet-facing
   10. Select IPV4
   11. Select your vpc "project"-"env"-vpc
   12. Create a new security group "project"-"env"-lb-sg
       1. Select your vpc
       2. Create
   13. Create a target group
       1. Instance target type
       2. Name it "project"-"env"-tg
       3. Leave as port 80, your vpc (should be selected already), and http1
       4. Change checks both to 3 and timeout to 60 seconds, interval to 120, and success codes to 200,301,499
   14. Now you can select your target group and security group on the Application Load Balancer. Save it. Go back to the service tab from Step 6
   15. Select your load balancer and hit next step
   16. You just need to setup port 80 and hit create. If it fails hit back and hit save again
8. Update the service
   1. This will end up trying to deploy it out to an instance
   2. We still need to fix up all the ports so things can talk properly.
9. Update security groups
   1. Allow inbound Postgres port to rds from your ecs group
   2. Allow http and https for ipv4 and ipv6 to load balancer group
   3. Allow all ports from load balancer to ecs group
10. Add Route53 A Record for api to load balancer

# CustomImageField

## Fields
1. aspect_ratios (array) - If specified as None it will use the aspect ratio of the uploaded image. If specified a value - has to be a string with slash eg. "1/1", "16/9"
2. file_types (array) - specifies the file types the image will be generated to
3. container width (int) - used to limit the maximum width of layouts, to promote better readability on larger screens. We default to 1200px, but you can override this setting, via the PICTURES["CONTAINER_WIDTH"] setting.
You may also set it to None, should you not use a container.
4. width_field/height_field - to store the width and the height of the original image
5. grid_columns (int) - will generate container_width/grid_column number of pictures (eg. container_width = 1200, grid_column=2, will generate 600w and 1200w (2 pictures)). We default to 12 columns, but you can override this setting, via the PICTURES["GRID_COLUMNS"] setting.
6. pixel_densities (array of int) - generates pictures based on specified pixel densities eg. [1, 2] (will generate x2 images)
7. breakpoints - specifies the images you want to create for each breakpoint.You may define your own breakpoints, they should be identical to the ones used in your css library. Simply override the PICTURES["BREAKPOINTS"] setting.
8. max_file_size - specifies the largest size the image will be stored