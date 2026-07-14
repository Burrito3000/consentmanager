# AWS Deployment Guide — ap-south-1 (Mumbai)

This guide covers deploying the DPDP Consent Management Platform to AWS ap-south-1 for data residency compliance.

## Architecture

```
CloudFront (CDN)
    ├── S3 (Next.js static assets)
    └── ALB (TLS termination)
            ├── ECS Fargate — API (FastAPI :8000)
            ├── ECS Fargate — Admin (Flask :8001)
            ├── ECS Fargate — Worker (Celery)
            └── ECS Fargate — Beat (Celery scheduler)
    RDS PostgreSQL (Multi-AZ, encrypted)
    ElastiCache Redis (Cluster mode)
    S3 (Audit log archive)
    Secrets Manager (All secrets)
    WAF (Rate limiting, IP allowlist)
```

## Prerequisites

- AWS CLI configured
- Docker & docker-compose
- Domain name with Route53 hosted zone
- ACM certificate in ap-south-1

## Step 1: Infrastructure Setup

```bash
# Set region
export AWS_REGION=ap-south-1
export AWS_PROFILE=cmp-production

# Create ECR repositories
aws ecr create-repository --repository-name cmp-api
aws ecr create-repository --repository-name cmp-admin
aws ecr create-repository --repository-name cmp-worker
aws ecr create-repository --repository-name cmp-frontend

# Build and push images
cd backend
docker build -t cmp-api .
docker tag cmp-api:latest $AWS_ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/cmp-api:latest
docker push $AWS_ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/cmp-api:latest

cd ../frontend
docker build -t cmp-frontend .
docker tag cmp-frontend:latest $AWS_ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/cmp-frontend:latest
docker push $AWS_ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/cmp-frontend:latest
```

## Step 2: RDS PostgreSQL

```bash
aws rds create-db-instance \
    --db-instance-identifier cmp-db \
    --db-instance-class db.r6g.large \
    --engine postgres \
    --engine-version 16 \
    --master-username cmp_admin \
    --master-user-password $(aws secretsmanager get-secret-value --secret-id cmp/db-password --query SecretString --output text) \
    --db-name cmp \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --multi-az \
    --backup-retention-period 30 \
    --deletion-protection \
    --region ap-south-1
```

## Step 3: ElastiCache Redis

```bash
aws elasticache create-replication-group \
    --replication-group-id cmp-redis \
    --replication-group-description "CMP Redis" \
    --engine redis \
    --engine-version 7.1 \
    --cache-node-type cache.r6g.large \
    --num-cache-clusters 2 \
    --multi-az-enabled \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled \
    --region ap-south-1
```

## Step 4: ECS Fargate Cluster

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name cmp-cluster

# Create task definitions and services using provided CloudFormation template
aws cloudformation create-stack \
    --stack-name cmp-ecs \
    --template-body file://deploy/cloudformation/ecs.yml \
    --parameters \
        ParameterKey=VpcId,ParameterValue=vpc-xxxxx \
        ParameterKey=SubnetIds,ParameterValue=subnet-xxxx,subnet-yyyy \
        ParameterKey=DatabaseUrl,ParameterValue=$(aws secretsmanager get-secret-value --secret-id cmp/database-url --query SecretString --output text) \
        ParameterKey=RedisUrl,ParameterValue=$(aws elasticache describe-replication-groups --replication-group-id cmp-redis --query 'ReplicationGroups[0].ConfigurationEndpoint.Address' --output text) \
        ParameterKey=SecretKey,ParameterValue=$(aws secretsmanager get-secret-value --secret-id cmp/secret-key --query SecretString --output text) \
        ParameterKey=EncryptionKey,ParameterValue=$(aws secretsmanager get-secret-value --secret-id cmp/encryption-key --query SecretString --output text) \
        ParameterKey=JwtSecret,ParameterValue=$(aws secretsmanager get-secret-value --secret-id cmp/jwt-secret --query SecretString --output text) \
    --capabilities CAPABILITY_IAM \
    --region ap-south-1
```

## Step 5: CloudFront + S3

```bash
# Create S3 bucket for frontend
aws s3 mb s3://cmp-frontend --region ap-south-1

# Deploy frontend
aws s3 sync ./frontend/out/ s3://cmp-frontend/ --delete

# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name $ALB_DNS_NAME \
    --default-root-object index.html \
    --region ap-south-1
```

## Step 6: Secrets Manager

Create secrets in AWS Secrets Manager:

| Secret Name | Contents |
|-------------|----------|
| `cmp/secret-key` | 64-char random string |
| `cmp/encryption-key` | 32-byte base64-encoded AES key |
| `cmp/jwt-secret` | 64-char random string |
| `cmp/db-password` | RDS master password |
| `cmp/database-url` | Full Postgres DSN |
| `cmp/aws-keys` | API + secret for SES/SNS/S3 |

Generate keys:
```bash
python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

## Step 7: WAF + Rate Limiting

```bash
aws wafv2 create-web-acl \
    --name cmp-waf \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules '[
        {
            "Name": "RateLimit",
            "Priority": 0,
            "Action": {"Block": {}},
            "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "RateLimit"},
            "Statement": {"RateBasedStatement": {"Limit": 2000, "AggregateKeyType": "IP"}}
        }
    ]' \
    --region ap-south-1
```

## Step 8: DNS + TLS

```bash
# Get ACM certificate (request or import)
aws acm request-certificate \
    --domain-name cmp.example.com \
    --validation-method DNS \
    --region ap-south-1

# Create Route53 alias to CloudFront
aws route53 change-resource-record-sets \
    --hosted-zone-id ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "cmp.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "dxxxxx.cloudfront.net",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'
```

## Production Checklist

- [ ] TLS enabled on all endpoints (ACM certs)
- [ ] RDS encryption at rest + automated backups (30-day retention)
- [ ] ElastiCache encryption at rest + in transit
- [ ] S3 bucket policy restricts public access
- [ ] WAF rate limiting configured (2000 req/min per IP)
- [ ] Security groups locked down (no public RDS/Redis access)
- [ ] Secrets in Secrets Manager (never in .env or code)
- [ ] CloudFront geo-restriction set to India only (if required)
- [ ] VPC Flow Logs enabled
- [ ] CloudTrail enabled for API audit
- [ ] GuardDuty enabled for threat detection
- [ ] ECS tasks run with least-privilege IAM roles
- [ ] Database backups tested monthly
- [ ] Incident response runbook documented
- [ ] Contact: dpo@cmp.example.com published per DPDP §8

## Monitoring

- CloudWatch dashboards for ECS, RDS, Redis
- Structured JSON logging via structlog → CloudWatch Logs
- Alarms for: CPU > 80%, 5xx errors > 1%, RDS connections > 80%
- Audit log chain verification runs daily (scheduled task)

## DPDP Data Residency

All infrastructure is deployed in **AWS ap-south-1 (Mumbai)** to ensure:
- Personal data remains within Indian borders
- Meets DPDP data localization requirements
- Subpoenas and legal requests handled via Indian courts
- AWS operates local zone in Mumbai for low-latency access
