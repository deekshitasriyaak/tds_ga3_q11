from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    headers = {"ngrok-skip-browser-warning": "true"}

    # 1. get_ticket_status(ticket_id)
    m = re.search(r'ticket\s+(\d+)', q, re.IGNORECASE)
    if m:
        return JSONResponse(content={
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": int(m.group(1))})
        }, headers=headers)

    # 2. schedule_meeting(date, time, meeting_room)
    m = re.search(r'(\d{4}-\d{2}-\d{2}).*?(\d{2}:\d{2}).*?(?:in|room)\s+(.+?)\.?$', q, re.IGNORECASE)
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
    m = re.search(r'expense.*?(\d+)|(\d+).*?expense', q, re.IGNORECASE)
    if m and ('expense' in q.lower() or 'reimburs' in q.lower()):
        emp_id = int(m.group(1) or m.group(2))
        return JSONResponse(content={
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": emp_id})
        }, headers=headers)

    # 4. calculate_performance_bonus(employee_id, current_year)
    # Matches: "bonus for employee X for YYYY", "Employee X performance bonus YYYY", etc.
    if re.search(r'bonus|performance', q, re.IGNORECASE):
        emp = re.search(r'employee\s+(\d+)|(\d+)\s+performance|emp(?:loyee)?\s*[:#]?\s*(\d+)', q, re.IGNORECASE)
        yr = re.search(r'(20\d{2})', q)
        if emp and yr:
            emp_id = int(next(g for g in emp.groups() if g))
            return JSONResponse(content={
                "name": "calculate_performance_bonus",
                "arguments": json.dumps({
                    "employee_id": emp_id,
                    "current_year": int(yr.group(1))
                })
            }, headers=headers)

    # 5. report_office_issue(issue_code, department)
    if re.search(r'issue|report|office', q, re.IGNORECASE):
        code = re.search(r'issue\s+(\d+)|(\d+)\s+(?:for|in)\s+the', q, re.IGNORECASE)
        dept = re.search(r'(?:for the|department[:\s]+)\s*([A-Za-z]+)\s+department|([A-Za-z]+)\s+department', q, re.IGNORECASE)
        if code and dept:
            issue_code = int(next(g for g in code.groups() if g))
            department = next(g for g in dept.groups() if g)
            return JSONResponse(content={
                "name": "report_office_issue",
                "arguments": json.dumps({
                    "issue_code": issue_code,
                    "department": department.strip()
                })
            }, headers=headers)

    return JSONResponse(
        content={"error": "No matching function found", "query": q},
        status_code=400,
        headers=headers
    )