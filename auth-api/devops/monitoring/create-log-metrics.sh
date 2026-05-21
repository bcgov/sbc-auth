#!/bin/bash
# Creates two GCP log-based metrics for auth-api dashboard monitoring,
# using Cloud Run's httpRequest.latency directly.
#
# Uses 5 labels to identify every endpoint without including dynamic ID values:
#
#   route_group  — resource name: orgs, users, entities, tasks, ...
#   sub_route    — known literal sub-resource, skipping any dynamic segment:
#                  members, contacts, affiliations, @me, token, ...
#   has_id       — "/" when an integer ID is present in the URL, null otherwise
#   method       — HTTP method: GET, POST, PUT, PATCH, DELETE
#   api_version  — v1 or v2
#
# Calls the Cloud Logging REST API directly via curl (Python builds the JSON
# payload to avoid bash/YAML quoting issues with complex regex expressions).
#
# Usage: ./create-log-metrics.sh [dev|test|sandbox|prod]

set -euo pipefail

ENV=${1:-}
if [[ -z "$ENV" ]]; then
  echo "Usage: $0 [dev|test|sandbox|prod]"
  exit 1
fi

case "$ENV" in
  dev)     PROJECT="gtksf3-dev";   SERVICE="auth-api-dev"     ;;
  test)    PROJECT="gtksf3-test";  SERVICE="auth-api-test"    ;;
  sandbox) PROJECT="gtksf3-tools"; SERVICE="auth-api-sandbox" ;;
  prod)    PROJECT="gtksf3-prod";  SERVICE="auth-api-prod"    ;;
  *)       echo "Unknown environment: $ENV. Use dev|test|sandbox|prod"; exit 1 ;;
esac

echo "Project : $PROJECT"
echo "Service : $SERVICE"
echo ""

TOKEN=$(gcloud auth print-access-token 2>/dev/null)
if [[ -z "$TOKEN" ]]; then
  echo "Error: could not get access token. Run 'gcloud auth login' first."
  exit 1
fi

BASE_URL="https://logging.googleapis.com/v2/projects/${PROJECT}/metrics"
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT


python3 - "$SERVICE" "$WORK_DIR" << 'PYTHON'
import json, sys, pathlib

service, out_dir = sys.argv[1], sys.argv[2]

SUB_ROUTE_ALT = (
    "affiliations/search|admins/affidavits|@me|activity-logs|affidavits|affidavit|"
    "affiliations|affiliation|api-keys|authentication|authorizations|authorization|contacts|healthz|"
    "info|invitations|login-options|mailing-address|membership|members|notifications|otp|"
    "orgs|org|payment_info|products|readyz|settings|signatures|simple|tokens|token|"
    "unaffiliated|users"
)

labels = [
    {"key": "route_group", "valueType": "STRING", "description": "API resource"},
    {"key": "sub_route",   "valueType": "STRING", "description": "Literal sub-resource after any dynamic segment"},
    {"key": "has_id",      "valueType": "STRING", "description": "Slash when integer ID present; null for collection routes"},
    {"key": "method",      "valueType": "STRING", "description": "HTTP method"},
    {"key": "api_version", "valueType": "STRING", "description": "API version v1 or v2"},
]

# Simplified patterns: no (?:...) non-capturing groups, require /api/vN/ prefix explicitly.
# Routes outside /api/vN/ (e.g. /ops/healthz) will yield null for route_group/api_version.
extractors = {
    "route_group": 'REGEXP_EXTRACT(httpRequest.requestUrl, "/api/v[12]/([^/?]+)")',
    "sub_route":   f'REGEXP_EXTRACT(httpRequest.requestUrl, "/api/v[12]/[^/]+/(?:[^/]+/)*({SUB_ROUTE_ALT})")',
    "has_id":      'REGEXP_EXTRACT(httpRequest.requestUrl, "/api/v[12]/[^/]+(/)[0-9]+")',
    "method":      'REGEXP_EXTRACT(httpRequest.requestMethod, "([A-Z]+)")',
    "api_version": 'REGEXP_EXTRACT(httpRequest.requestUrl, "/api/(v[12])/")',
}

base_filter = (
    f'resource.type="cloud_run_revision" '
    f'resource.labels.service_name="{service}" '
    f'httpRequest.requestUrl!=""'
)

latency_metric = {
    "name": "auth_api_request_latency",
    "description": "auth-api per-endpoint request latency in seconds",
    "filter": base_filter,
    "metricDescriptor": {
        "metricKind": "DELTA",
        "valueType": "DISTRIBUTION",
        "unit": "s",
        "labels": labels,
    },
    "valueExtractor": "EXTRACT(httpRequest.latency)",
    "bucketOptions": {
        "exponentialBuckets": {
            "numFiniteBuckets": 20,
            "growthFactor": 2.0,
            "scale": 0.001,
        }
    },
    "labelExtractors": extractors,
}

count_metric = {
    "name": "auth_api_request_count",
    "description": "auth-api per-endpoint request count",
    "filter": base_filter,
    "metricDescriptor": {
        "metricKind": "DELTA",
        "valueType": "INT64",
        "labels": labels,
    },
    "labelExtractors": extractors,
}

pathlib.Path(f"{out_dir}/latency.json").write_text(json.dumps(latency_metric))
pathlib.Path(f"{out_dir}/count.json").write_text(json.dumps(count_metric))
PYTHON


create_or_update() {
  local name=$1
  local payload_file=$2

  printf "  %-45s\n" "$name"

  http_code=$(curl -s -o "$WORK_DIR/resp.json" -w "%{http_code}" \
    -X POST "$BASE_URL" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    --data-binary "@${payload_file}")

  if [[ "$http_code" == "200" ]]; then
    echo "  [created]"
    return
  fi

  if [[ "$http_code" == "409" ]] || grep -q "already exists" "$WORK_DIR/resp.json" 2>/dev/null; then
    upd_code=$(curl -s -o "$WORK_DIR/upd.json" -w "%{http_code}" \
      -X PUT "${BASE_URL}/${name}" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      --data-binary "@${payload_file}")

    if [[ "$upd_code" == "200" ]]; then
      echo "  [updated]"
    else
      echo "  [error on update (HTTP $upd_code)]"
      python3 -c "import json,sys; d=json.load(open('$WORK_DIR/upd.json')); print(json.dumps(d,indent=2))" 2>/dev/null || cat "$WORK_DIR/upd.json"
    fi
    return
  fi

  echo "  [error on create (HTTP $http_code)]"
  python3 -c "import json,sys; d=json.load(open('$WORK_DIR/resp.json')); print(json.dumps(d,indent=2))" 2>/dev/null || cat "$WORK_DIR/resp.json"
}

# ---------------------------------------------------------------------------
# Create / update
# ---------------------------------------------------------------------------
echo "Creating latency metric..."
create_or_update "auth_api_request_latency" "$WORK_DIR/latency.json"

echo ""
echo "Creating request count metric..."
create_or_update "auth_api_request_count" "$WORK_DIR/count.json"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Done."
echo ""
echo "Dashboard variables to configure in Cloud Monitoring:"
echo "  route_group  — resource.labels dropdown (orgs, users, entities, ...)"
echo "  sub_route    — sub-resource dropdown (members, contacts, affiliations, ...)"
echo "  has_id       — '/' for detail routes, unset for collection routes"
echo "  method       — HTTP method filter"
echo "  api_version  — v1 or v2"
echo ""
echo "Metrics created:"
gcloud logging metrics list \
  --project="$PROJECT" \
  --filter="name:auth_api_request" \
  --format="table(name,description)" 2>/dev/null || true
