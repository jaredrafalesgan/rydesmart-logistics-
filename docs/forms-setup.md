# Forms setup (GoHighLevel)

The site has three business forms, plus the existing driver application:

| Form | Page | `inquiry_type` |
|---|---|---|
| Freight capacity / quote request | /request-capacity | `capacity` |
| Carrier document request (packet, W-9, COI) | /broker-resources#documents | `documents` |
| Contact message (with department) | /contact | `contact` |
| CDL driver application | /careers, homepage "Apply Today" | existing GHL form |

Every built-in form validates input, shows sending / success / error states, blocks double clicks and
identical re-submissions, creates a reference number (e.g. `RSL-261117-7KQ2`) and timestamp, and records
the lead source (landing page, referrer, UTM tags).

**Where submissions go depends on what you configure** in `content/company.yml`:

| Setting | What happens |
|---|---|
| nothing (today) | The visitor's email app opens with the full request addressed to Admin@rydesmartlogistics.com. Works, but nothing is stored automatically and the visitor must press Send. |
| `inquiry_webhook_url` | Submissions are POSTed as JSON to your GoHighLevel workflow (option A). Recommended for the custom-designed forms. |
| `ghl_forms.capacity` / `documents` / `contact` | That page shows a GoHighLevel form instead of the built-in one (option B). |

## Option A — GoHighLevel Inbound Webhook (keeps the site's form design)

1. GoHighLevel → **Automation → Workflows → Create workflow → Start from scratch**.
2. Trigger: **Inbound Webhook**. Copy the webhook URL it shows.
3. Paste it into `content/company.yml` → `integrations.inquiry_webhook_url`, run `python3 tools/build.py`,
   and re-paste the updated pages into GoHighLevel.
4. Submit one test request on the site. In the trigger, click **Fetch sample requests** and select it so
   the fields can be mapped.
5. Add actions:
   - **Create/Update Contact** — map `email`, `phone`, `name`, `company` (top-level keys in the payload).
     GoHighLevel de-duplicates contacts by email/phone.
   - **Add Tag** — e.g. `website-{{inboundWebhookRequest.inquiry_type}}` (capacity / documents / contact).
   - **Internal Notification** (email/SMS to your team) — include `reference`, `inquiry_label`,
     `submitted_at` and the `fields.*` values.
   - **Send Email** to the contact — the confirmation ("We received your request, reference …").
     The site's success message tells visitors a confirmation is coming, so keep this step.
   - Optional: **Create Opportunity** in a "Freight inquiries" pipeline, **Assign to user**, and a
     **Wait 1 day → if no reply, Notify** follow-up reminder.
6. Turn the workflow on and send a final test from the live site.

Payload example:
```json
{
  "inquiry_type": "capacity",
  "inquiry_label": "Freight capacity request",
  "reference": "RSL-261117-7KQ2",
  "submitted_at": "2026-11-17T20:41:09.512Z",
  "page": "https://www.rydesmartlogistics.com/request-capacity",
  "source": {"landing_page": "/lanes", "referrer": "", "utm_source": "dat", "utm_medium": "", "utm_campaign": ""},
  "name": "Jane Broker", "email": "jane@broker.com", "phone": "(404) 555-0100", "company": "Acme Freight",
  "fields": {"role": "Freight broker", "origin": "Atlanta, GA", "destination": "Dallas, TX",
             "pickup_date": "2026-11-20", "equipment": "53' Dry Van", "commodity": "Paper goods",
             "weight": "40,000", "frequency": "Weekly", "message": "…"}
}
```

Things to know:
- **Not tested against a live GoHighLevel account.** GoHighLevel's servers aren't reachable from the build
  environment, so the browser-to-webhook request (including CORS) must be confirmed with step 4. If the
  test submission shows "We couldn't send that just now", use option B.
- Inbound Webhook is a **premium** GoHighLevel trigger (billed per execution).
- The webhook URL is visible in the page source, as with any client-side form endpoint. The forms include
  a hidden spam-trap field and a minimum fill time; GoHighLevel workflows can also filter on them.
- File attachments aren't sent through the webhook. The form asks visitors to email documents with their
  reference number. Option B supports file-upload fields.

## Option B — GoHighLevel forms (simplest, no webhook)

1. GoHighLevel → **Sites → Forms → Builder**. Build a form per row above with the fields listed in
   `src/templates/pages/request.html`, `resources.html` and `contact.html` (add a File Upload field to the
   capacity form if you want attachments).
2. In each form's settings set the **on-submit message**, **notification email** and an
   **autoresponder/confirmation** (or a workflow with trigger "Form Submitted").
3. Copy each form's share link (like the driver application:
   `https://api.leadconnectorhq.com/widget/form/…`) into `content/company.yml` → `integrations.ghl_forms`.
4. Rebuild. Those pages now embed the GoHighLevel form in place of the built-in one.

## Document requests
Documents are never posted on the website. Requests arrive tagged `documents`; your team (or a GoHighLevel
workflow) replies to the requester's business email. For certificates of insurance, forward the request
(certificate holder name/address is collected) to your insurance agent.
