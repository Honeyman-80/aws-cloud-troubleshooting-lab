#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${1:-document-processing-sam}"
REGION="${AWS_REGION:-us-east-1}"
FILE="${2:-sample-document.txt}"
CONTENT_TYPE="${3:-text/plain}"

if [ ! -f "$FILE" ]; then
  echo "This is a test document uploaded by the developer test harness." > "$FILE"
fi

API_URL=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text)

echo "Creating upload job..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"$(basename "$FILE")\",\"content_type\":\"$CONTENT_TYPE\"}")

echo "$RESPONSE"

UPLOAD_URL=$(python3 - <<PY
import json
print(json.loads('''$RESPONSE''')['upload_url'])
PY
)

JOB_ID=$(python3 - <<PY
import json
print(json.loads('''$RESPONSE''')['job_id'])
PY
)

echo "Uploading file for job: $JOB_ID"
curl -s -X PUT "$UPLOAD_URL" \
  -H "Content-Type: $CONTENT_TYPE" \
  --upload-file "$FILE" >/dev/null

echo "Upload complete. Check Step Functions and DynamoDB for job_id: $JOB_ID"
