from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import re
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/execute")
async def execute(request: Request, q: str):
    # Force JSON response - bypass ngrok warning
    headers = {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json"
    }

    # 1. get_ticket_status(ticket_id)
    m = re.search(r'ticket\s+(\d+)', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": int(m.group(1))})
        }, headers=headers)

    # 2. schedule_meeting(date, time, meeting_room)
    m = re.search(r'meeting on (\d{4}-\d{2}-\d{2}) at (\d{2}:\d{2}) in (.+?)\.?$', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": m.group(1),
                "time": m.group(2),
                "meeting_room": m.group(3).strip()
            })
        }, headers=headers)

    # 3. get_expense_balance(employee_id)
    m = re.search(r'expense balance for employee\s+(\d+)', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": int(m.group(1))})
        }, headers=headers)

    # 4. calculate_performance_bonus(employee_id, current_year)
    m = re.search(r'bonus for employee\s+(\d+) for (\d{4})', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": int(m.group(1)),
                "current_year": int(m.group(2))
            })
        }, headers=headers)

    # 5. report_office_issue(issue_code, department)
    m = re.search(r'issue\s+(\d+) for the (.+?) department', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": int(m.group(1)),
                "department": m.group(2).strip()
            })
        }, headers=headers)

    return JSONResponse(
        content={"error": "No matching function found"},
        status_code=400,
        headers=headers
    )