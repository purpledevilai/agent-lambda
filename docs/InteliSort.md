# InteliSort

InteliSort is an LLM-powered sorting endpoint that ranks ambiguous items using natural language evaluation. Instead of a numeric comparator, the comparison function is a prompt — making it possible to sort things that don't have an obvious quantitative ordering.

**Use cases:** Ranking sales leads by buying intent, screening resumes by job fit, prioritizing support tickets by urgency, comparing product descriptions by appeal — anything where "better" is subjective and best judged by language understanding.

## How It Works

InteliSort uses a **tournament bracket** algorithm. Items are paired off and compared head-to-head using an LLM. Winners advance. The process repeats until a champion emerges, then the bracket is backfilled to extract the next-best items, and so on until the top `n` are selected.

### Phase 1: Build the Bracket

Items are paired and compared in parallel at each level. With 16 items, the first round runs 8 comparisons simultaneously, the second round runs 4, and so on. This parallelism keeps total wall-clock time low despite each comparison being an LLM call.

```
Level 0:  [A] [B] [C] [D] [E] [F] [G] [H]
             ↘↙     ↘↙     ↘↙     ↘↙
Level 1:    [B]     [C]     [F]     [H]
               ↘↙           ↘↙
Level 2:      [C]           [F]
                  ↘↙
Level 3:        [C]  ← Champion
```

### Phase 2: Backfill and Extract

Once the champion is selected, it's removed from every level of the bracket. The now-empty slots are re-evaluated: the opponent the champion beat at each level gets a second chance by competing against the remaining item in its pair. This bubbles up a new champion — the second-best item. Repeat until `n` items are extracted.

### Complexity

- **Phase 1:** ~`N` comparisons (one full bracket)
- **Phase 2:** ~`log(N)` comparisons per extraction
- **Total:** ~`N + n * log(N)` LLM calls

For 50 items selecting the top 5, that's roughly 50 + 5*6 = **80 LLM calls** — far fewer than a full sort's ~282 (`N * log(N)`).

## API Reference

### Endpoint

```
POST /inteli-sort
```

**Authentication:** Required (Cognito token or API key)

**Behavior:** Returns immediately with a `202` response containing a Job. The sort runs asynchronously. Poll `GET /job/{job_id}` for progress and results.

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `items` | `string[]` or `{id, value}[]` | The items to sort. Can be plain strings or objects with an `id` and `value` field. |
| `prompt` | `string` | The comparison prompt. Must contain `ARG_ITEM_A` and `ARG_ITEM_B` placeholders. |
| `n` | `integer` | Number of top results to return. Must be between 1 and `len(items)`. |

### Item Formats

**Plain strings** — IDs are auto-generated as string indices (`"0"`, `"1"`, ...):

```json
{
  "items": [
    "Experienced full-stack developer with 10 years in React and Node",
    "Recent grad with a passion for learning",
    "Senior architect who led a team of 30 engineers"
  ],
  "prompt": "...",
  "n": 2
}
```

**ID/value objects** — use your own IDs for traceability:

```json
{
  "items": [
    {"id": "resume-482", "value": "Experienced full-stack developer with 10 years in React and Node"},
    {"id": "resume-917", "value": "Recent grad with a passion for learning"},
    {"id": "resume-201", "value": "Senior architect who led a team of 30 engineers"}
  ],
  "prompt": "...",
  "n": 2
}
```

### Writing the Prompt

The prompt is the core of InteliSort — it tells the LLM how to compare two items. It must include **both** `ARG_ITEM_A` and `ARG_ITEM_B` placeholders. The algorithm replaces these with the actual item values before each comparison and extracts a single verdict: `"a"` or `"b"`.

**Example — Ranking leads by buying intent:**

```
You are evaluating two sales leads based on buying intent.
Which lead is hotter and more likely to convert into a paying customer?

Lead A: ARG_ITEM_A

Lead B: ARG_ITEM_B

Choose the lead that demonstrates stronger buying intent.
```

**Example — Screening resumes for a role:**

```
You are a hiring manager for a Senior Backend Engineer position.
Compare these two candidates and choose the one who is a stronger fit.

Candidate A: ARG_ITEM_A

Candidate B: ARG_ITEM_B

Choose the candidate with more relevant experience and stronger qualifications.
```

**Example — Prioritizing support tickets:**

```
Compare these two customer support tickets.
Which one is more urgent and should be addressed first?

Ticket A: ARG_ITEM_A

Ticket B: ARG_ITEM_B

Choose the ticket that requires more immediate attention.
```

### Response (202)

The endpoint returns immediately with a queued Job:

```json
{
  "job_id": "a1b2c3d4-...",
  "owner_id": "user-sub-...",
  "status": "queued",
  "message": "Job queued",
  "data": {},
  "created_at": 1700000000,
  "updated_at": 1700000000
}
```

### Polling for Results

```
GET /job/{job_id}
```

**While running** (`status: "in_progress"`), the Job's `message` field updates with progress and `data.logs` accumulates milestone entries:

```json
{
  "status": "in_progress",
  "message": "  #2 selected: Senior architect who led a team of 30 engineers...",
  "data": {
    "logs": [
      "InteliSort: 8 items, selecting top 3",
      "Phase 1: Building tournament bracket",
      "  Level 0: 8 items -> 4 matches, 0 byes -> 4 winners",
      "  Level 1: 4 items -> 2 matches, 0 byes -> 2 winners",
      "  Level 2: 2 items -> 1 matches, 0 byes -> 1 winners",
      "  Bracket complete (4 levels). Champion: Experienced full-stack developer...",
      "Phase 2: Extracting top 3 via backfill",
      "  #1 selected: Experienced full-stack developer...",
      "  #2 selected: Senior architect who led a team of 30 engineers..."
    ]
  }
}
```

**When complete** (`status: "completed"`), `data.results` contains the ranked items:

```json
{
  "status": "completed",
  "message": "InteliSort complete: top 3 selected",
  "data": {
    "results": [
      {"id": "resume-482", "value": "Experienced full-stack developer with 10 years in React and Node"},
      {"id": "resume-201", "value": "Senior architect who led a team of 30 engineers"},
      {"id": "resume-917", "value": "Recent grad with a passion for learning"}
    ],
    "logs": ["..."]
  }
}
```

**On failure** (`status: "error"`), the `message` field describes what went wrong:

```json
{
  "status": "error",
  "message": "prompt must contain both ARG_ITEM_A and ARG_ITEM_B placeholders"
}
```

### Callback URL (Optional)

If you include a `Callback-URL` header, the API will POST the completed Job to your URL when the sort finishes:

```
POST /inteli-sort
Authorization: <token>
Callback-URL: https://your-server.com/webhook
Callback-Token: <optional-auth-for-your-webhook>
```

The callback payload follows the standard format:

```json
{
  "request_id": "a1b2c3d4-...",
  "status_code": 200,
  "response": { "job_id": "...", "status": "completed", "data": { "results": [...] } }
}
```

## Full Example

### Request

```bash
curl -X POST https://api.ajentify.com/inteli-sort \
  -H "Authorization: <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      "Hi, can you send me some general info about your services?",
      "We urgently need a solution like yours. Can we get a contract signed this week?",
      "Please remove me from your mailing list.",
      "This looks promising! What is the pricing? We have budget allocated for Q1.",
      "Just browsing, not sure if this is relevant to us.",
      "We have evaluated three vendors and yours is our top pick. Lets close the deal.",
      "Interesting concept. I will bring it up at our next team meeting.",
      "Not the right time. Maybe revisit in a year."
    ],
    "prompt": "You are evaluating two sales leads. Which lead shows more buying intent and is closer to making a purchase?\n\nLead A: ARG_ITEM_A\n\nLead B: ARG_ITEM_B\n\nChoose the lead that is hotter and more likely to convert.",
    "n": 3
  }'
```

### Response (immediate)

```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "queued",
  "message": "Job queued"
}
```

### Result (after polling)

```json
{
  "status": "completed",
  "data": {
    "results": [
      {"id": "1", "value": "We urgently need a solution like yours. Can we get a contract signed this week?"},
      {"id": "5", "value": "We have evaluated three vendors and yours is our top pick. Lets close the deal."},
      {"id": "3", "value": "This looks promising! What is the pricing? We have budget allocated for Q1."}
    ]
  }
}
```
