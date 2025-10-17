locals {
  alb_metric_dims = jsonencode({
    LoadBalancer = "*"
  })
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-observability"
  dashboard_body = <<JSON
{
  "widgets": [
    {
      "type": "metric",
      "x": 0, "y": 0, "width": 12, "height": 6,
      "properties": {
        "title": "ALB RequestCount / 5xx",
        "metrics": [
          [ "AWS/ApplicationELB", "RequestCount", ${local.alb_metric_dims} ],
          [ ".", "HTTPCode_Target_5XX_Count", ".", { "yAxis": "right", "stat": "Sum" } ]
        ],
        "stat": "Sum",
        "period": 60,
        "region": "${var.region}",
        "yAxis": { "left": { "label": "requests" }, "right": { "label": "5xx" } },
        "view": "timeSeries",
        "stacked": false
      }
    },
    {
      "type": "metric",
      "x": 12, "y": 0, "width": 12, "height": 6,
      "properties": {
        "title": "ALB TargetResponseTime p50 p90 p99",
        "metrics": [
          [ "AWS/ApplicationELB", "TargetResponseTime", ${local.alb_metric_dims}, { "stat": "p50" } ],
          [ ".", "TargetResponseTime", ".", { "stat": "p90" } ],
          [ ".", "TargetResponseTime", ".", { "stat": "p99" } ]
        ],
        "period": 60,
        "region": "${var.region}",
        "view": "timeSeries"
      }
    },
    {
      "type": "log",
      "x": 0, "y": 6, "width": 12, "height": 6,
      "properties": {
        "title": "Errors by service (last 1h)",
        "query": "SOURCE '/eks/${var.project}/app' | fields @timestamp, @message, kubernetes.container_name as svc, level | filter level = 'ERROR' or @message like /ERROR/ | stats count() as errors by svc | sort errors desc",
        "region": "${var.region}",
        "view": "table"
      }
    },
    {
      "type": "log",
      "x": 12, "y": 6, "width": 12, "height": 6,
      "properties": {
        "title": "Top routes by requests (last 1h)",
        "query": "SOURCE '/eks/${var.project}/app' | fields @timestamp, @message, route, status | stats count() as hits by route | sort hits desc | limit 10",
        "region": "${var.region}",
        "view": "table"
      }
    },
    {
      "type": "log",
      "x": 0, "y": 12, "width": 12, "height": 6,
      "properties": {
        "title": "Recent error log lines",
        "query": "SOURCE '/eks/${var.project}/app' | filter @message like /ERROR|Error|exception/i | fields @timestamp, kubernetes.container_name, @message | sort @timestamp desc | limit 50",
        "region": "${var.region}",
        "view": "table"
      }
    },
    {
      "type": "log",
      "x": 12, "y": 12, "width": 12, "height": 6,
      "properties": {
        "title": "Frontend health hits",
        "query": "SOURCE '/eks/${var.project}/app' | filter route = '/healthz' | stats count() as health_hits by bin(1m)",
        "region": "${var.region}",
        "view": "timeSeries"
      }
    }
  ]
}
JSON
}
