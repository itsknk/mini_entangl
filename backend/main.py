# mini_entangl/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import re

app = FastAPI(title="Mini‑Entangl")

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # SvelteKit dev
        "http://127.0.0.1:5173",
        "*",                      # loosen for demo; tighten before production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    markdown: str          # raw MOP text pasted in

class Step(BaseModel):
    number: int
    raw: str

class StepIssue(BaseModel):
    step_number: int
    description: str
    suggestion: str

class AnalyzeResponse(BaseModel):
    steps: List[Step]
    issues: List[StepIssue]

class FixResponse(BaseModel):
    fixed_markdown: str
    applied_fixes: List[StepIssue]

# --- very first rule: "shutdown before backup" -----------------
SHUTDOWN = {"shut down", "power off", "disable"}
BACKUP   = {"backup generator", "start backup", "start generator", "ups", "redundant power"}

step_re = re.compile(r'^\s*(\d+)[\).\-:]*\s*(.+)$')

def parse_steps(md: str) -> List[Step]:
    steps: List[Step] = []
    for line in md.splitlines():
        m = step_re.match(line)
        if m:
            steps.append(Step(number=int(m.group(1)), raw=m.group(2).strip()))
    return steps

def analyze_steps(steps: List[Step]) -> List[StepIssue]:
    issues: List[StepIssue] = []
    for idx, step in enumerate(steps):
        text = step.raw.lower()
        if any(k in text for k in SHUTDOWN):
            # any backup mention *before* this index?
            if not any(any(b in prev.raw.lower() for b in BACKUP) for prev in steps[:idx]):
                issues.append(
                    StepIssue(
                        step_number=step.number,
                        description="Power shutdown occurs before backup is online",
                        suggestion="Move this step after the generator/UPS start step",
                    )
                )
    return issues

def apply_fixes(steps: List[Step], issues: List[StepIssue]) -> List[Step]:
    """
    For now we only support re‑ordering shutdown steps *after* the last backup step.
    """
    if not issues:
        return steps

    # split steps
    shutdown_idxs = [i for i, s in enumerate(steps)
                     if any(k in s.raw.lower() for k in SHUTDOWN)]
    last_backup_idx = max(i for i, s in enumerate(steps)
                          if any(k in s.raw.lower() for k in BACKUP))

    # move every offending shutdown step right after last_backup_idx
    reordered = steps.copy()
    offset = 0
    for idx in shutdown_idxs:
        if idx <= last_backup_idx:       # only if before backup
            step = reordered.pop(idx + offset)   # offset b/c list shrinks
            reordered.insert(last_backup_idx, step)
            offset -= 1                   # keep pointer correct
    # renumber
    for i, s in enumerate(reordered, 1):
        s.number = i
    return reordered
    
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Parse the markdown, run rule checks, and return both
    the cleaned step list and any issues found.
    """
    steps  = parse_steps(req.markdown)
    issues = analyze_steps(steps)
    return AnalyzeResponse(steps=steps, issues=issues)


@app.post("/fix", response_model=FixResponse)
def fix(req: AnalyzeRequest):
    steps = parse_steps(req.markdown)
    issues = analyze_steps(steps)
    fixed_steps = apply_fixes(steps, issues)
    fixed_md = "\n".join(f"{s.number}. {s.raw}" for s in fixed_steps)
    return FixResponse(fixed_markdown=fixed_md, applied_fixes=issues)

