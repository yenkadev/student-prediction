# Demo test data — Chat, Form, Upload

Three input modes, plus copy-paste data for each. Aim for a low → medium → high
spread so the risk colors are visible on screen.

> **Important (read first):** the frontend sends `predictionType: "ml"` for **Chat**
> and **Upload** (hardcoded in `src/api/httpClient.ts`). So in the UI:
> - **Chat** always uses the ML model → you must mention all **17** fields.
> - **Upload** always uses the ML model → use **`demo_ml.csv`** (the ML file).
> - **Form** is the only mode with a Rule-based / ML toggle → both files/values work.
>
> To demo a rule-based **upload**, call the API directly (see the curl at the bottom)
> with `demo_rule_based.csv`.

---

## 1) Chat  (ML — describe all 17 fields in plain language)

Paste one of these into the chat box. Each paragraph contains every field the ML
model needs, so it should return a result in a single turn.

### 🔴 High-risk student
```
I'm assessing a 22-year-old male student in Year 3 of the Engineering department.
His GPA is 1.7, his semester GPA is 1.6 and his CGPA is 1.8. He attends only about
60% of classes and studies roughly 1.5 hours per day. He submits assignments about
5 days late on average and his stress index is 9 out of 10. He has a part-time job,
no scholarship, and no reliable internet access at home. His family income is around
32,000 per year, his parents' highest education is high school, and he travels about
45 minutes to campus.
```

### 🟢 Low-risk student
```
Please assess a 20-year-old female student in Year 2 of Computer Science. Her GPA is
3.6, semester GPA 3.7, CGPA 3.5. Attendance is 96%, she studies about 4 hours a day,
never submits assignments late (0 delay days), and her stress index is 3 out of 10.
She has a scholarship, reliable internet access, and no part-time job. Family income
is about 150,000 a year, her parents hold a Master's degree, and she travels 15
minutes to campus.
```

### 🔁 Multi-turn version (to show the follow-up questions)
Send this first — it's deliberately incomplete, so the assistant will ask for the rest:
```
I want to assess a Year 3 Engineering student, male, age 22. His GPA is 1.7 and his
attendance is around 60%.
```
Then answer its follow-up with:
```
Semester GPA 1.6, CGPA 1.8. He studies about 1.5 hours a day, submits assignments ~5
days late, stress index 9/10. He has a part-time job, no scholarship, no internet
access at home. Family income about 32,000, parents finished high school, travel time
45 minutes.
```

---

## 2) Form  (New assessment → Form tab)

The Form tab has a **Rule-based / ML** toggle. Name and Student ID are optional.

### Rule-based (7 fields)

| Field | 🟢 Low | 🟡 Medium | 🔴 High |
|---|---|---|---|
| GPA | 3.5 | 2.3 | 1.6 |
| Attendance rate (%) | 95 | 80 | 62 |
| Stress index (1–10) | 3 | 6 | 9 |
| Study hours / day | 4 | 2.5 | 1 |
| Assignment delay (days) | 0 | 1 | 5 |
| Internet access | Yes | Yes | No |
| Part-time job | No | No | Yes |

### ML (17 fields)

| Field | 🟢 Low | 🔴 High |
|---|---|---|
| GPA | 3.6 | 1.7 |
| Semester GPA | 3.7 | 1.6 |
| CGPA | 3.5 | 1.8 |
| Attendance rate (%) | 96 | 60 |
| Study hours / day | 4 | 1.5 |
| Assignment delay (days) | 0 | 5 |
| Stress index (1–10) | 3 | 9 |
| Travel time (min) | 15 | 45 |
| Age | 20 | 22 |
| Family income | 150000 | 32000 |
| Gender | Female | Male |
| Department | CS | Engineering |
| Year of study | Year 2 | Year 3 |
| Parental education | Master | High School |
| Scholarship | Yes | No |
| Internet access | Yes | No |
| Part-time job | No | Yes |

---

## 3) Upload file  (New assessment → Upload file tab)

- **In the UI:** use **`demo_ml.csv`** (6 students: 2 low, 2 medium, 2 high).
  The UI forces the ML model, so the ML file is the one that validates.
- `demo_rule_based.csv` is included for the rule-based pipeline (7 columns).
  Both files have the required `name` and `studentId` columns.

### Files
- `demo_ml.csv` — headers: name, studentId + the 17 ML feature columns
- `demo_rule_based.csv` — headers: name, studentId + the 7 rule-based columns

### Rule-based upload via API (optional, for a rule-based batch demo)
```bash
curl -X POST http://localhost:8000/predict/batch \
  -F "file=@demo_rule_based.csv" \
  -F "predictionType=rule_based"
# → {"jobId":"..."}  then poll:
curl http://localhost:8000/predict/batch/<jobId>
```
Rule-based expected outcomes: An & Bich = **high**, Chau & Dat = **medium**,
En & Phuc = **low**.

---

### Tip
Batch results and single (chat/form) assessments all show up on the **Overview**
dashboard and **All sessions** afterward — good for showing the full flow end to end.
