There is an access log at `/app/access.log`. Analyze the traffic and summarize what you find.
Please write your findings to `/app/report.json` in JSON format.

Your JSON report must satisfy the following criteria:
1. It contains a "total_requests" key with the integer total number of requests found in the log.
2. It contains a "unique_ips" key with the integer count of unique client IP addresses.
3. It contains a "top_path" key with the string path of the most requested URI.
