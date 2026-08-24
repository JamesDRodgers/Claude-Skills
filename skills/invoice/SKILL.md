---
name: invoice
description: "name: invoice-builder description: Generates client invoices for AI design, instructional design, and consulting work. Use when the user asks to create, draft, revise, or number an invoice, bill a client, log a payment, or check what has been invoiced. Anchors line items to signed agreements and never fabricates amounts, dates, hours, or approvals."
---

---

# Invoice Builder

Produces contract-anchored invoices for independent contractor work.

## Non-negotiable rule

Never invent a number, date, rate, hour count, address, or approval.
If a required field is unknown, stop and ask for it. An invoice with a
guessed figure on it is worse than no invoice, because it goes into the
client's accounting system as a claim the user did not actually make.

Fields that must never be inferred:
- Any dollar amount or hourly rate
- Hours worked
- The date out-of-scope work was approved, and by whom
- Client legal entity name, address, or tax ID
- Bank routing or account numbers
- Deliverable names not present in the signed agreement

Fields safe to generate: invoice number, invoice date (today), due date
(invoice date plus net terms).

## Step 1: Identify the paying entity

Ask who the contract counterparty is, not who asked for the invoice.
These are frequently different people. Common pattern: a program lead
requests the invoice, but a fiscal sponsor or parent organization is the
legal payer and the one whose accounts payable will process it.

Bill to the entity on the signed agreement, with the requester on an
attention line. An invoice made out to an individual when the contract
names an organization will stall in AP or be returned.

Check the Client Registry section below. If the client is listed, pull
the bill-to block from there. If not, collect the details and tell the
user to add an entry.

## Step 2: Establish the billing basis

Determine which applies:

- **Fixed fee against a signed agreement.** Line items mirror the
  deliverable names in the contract. Ask whether payment triggers on
  each deliverable or on completion of all of them.
- **Hourly.** Requires rate and hours. Ask for both.
- **Milestone.** Requires the milestone definition and its assigned
  amount from the agreement.
- **Mixed.** Contract work and additional work are separated into
  labeled sections. See Step 4.

Ask for the agreement's effective date and net terms. Do not assume
Net 30 without confirming, though Net 30 is the reasonable default for
nonprofit and fiscally sponsored clients if the contract is silent.

## Step 3: Build line items from contract language

Line items should be verifiable against the agreement by someone who
has never spoken to the user. Write what was delivered, not what it
took to deliver it.

Good: "Learning Hub asset 2 of 3: [deliverable name per agreement]"
Bad: "Prompt engineering, research, and iteration"

The second version invites questions, and questions delay payment.

## Step 4: Handle out-of-scope work explicitly

If work exceeded the signed scope, do not fold it into the contract
line items. Put it in its own section labeled with the approval date
and the name of the person who approved it.

If the user cannot name a date and a person who approved the extra
work, still generate the line item, but place a warning block directly
above the invoice in the chat response. The warning does not go into
the invoice itself. Format:

> UNVERIFIED APPROVAL
> The additional work below is not tied to a documented approval.
> Before sending, confirm with {client contact} that this work was
> authorized. If it was approved verbally, a short email restating
> the scope and amount creates the record retroactively and costs
> you one paragraph.

Label the section in the invoice as "ADDITIONAL WORK" without an
approval line rather than inventing one. Never write "approved by"
followed by a name the user did not supply.

If the user chooses not to bill for out-of-scope work, note the
decision in the log so the pattern is visible over time. Absorbing
work once is generosity. Absorbing it every engagement is a pricing
problem.

## Step 5: Generate

Default output is markdown for review. On request, also produce a
clean HTML version suitable for printing to PDF, single page, no
color dependencies, legible at 11pt.

Use the Invoice Template section below.

Invoice numbering: `YYYY-NNN`, sequential across all clients, never
restarting per client. Ask the user for the last number issued if the
log below is empty, then increment. Sequential-across-all-clients
numbering is what an accountant expects and what makes the record
legible if it is ever examined.

## Step 6: Post-generation checklist

Present these as a short list after the invoice, not as prose:

- W-9 sent to this client? Required before most organizations can
  issue payment.
- Payment method included, either ACH details or check payee and
  address.
- Contract reference line present, with effective date.
- Contractor status line present.
- Amount recorded in the log.
- Estimated tax set-aside noted. Self-employment tax plus federal
  and state income tax typically lands in the 30 to 40 percent range
  for a contractor with other W-2 income. Flag the amount but do not
  compute a tax liability, and do not present tax figures as advice.

## Step 7: Log it

Give the user a completed row for the Invoice Log section below. Never
rewrite existing rows. Update the status field when payment is reported.

## Writing standards

- No em dashes.
- Plain, direct language throughout, including in any cover message.
- Do not add invented next steps, deliverable descriptions, or
  flattering framing of the work.
- If asked to draft an accompanying email, keep it under five
  sentences. Attach, state the amount and terms, thank briefly, stop.

## Follow-up handling

- Unpaid past terms: draft a short, neutral follow-up. First follow-up
  at seven days past due, referencing the invoice number and date only.
  No apology for asking. No escalation in tone before day thirty.
- Revision requested: issue a corrected invoice with a new number and
  mark the original as voided in the log. Do not silently edit an
  invoice that has already been sent.

## Invoice Template

```
INVOICE

{contractor_legal_name}
{contractor_address}
{contractor_email} | {contractor_phone}

Invoice #: {YYYY-NNN}
Date: {invoice_date}
Terms: {net_terms}
Due: {due_date}

BILL TO
{client_legal_entity}
Attn: {requester_name}
{client_address}

For services under the {agreement_title} effective {agreement_date}

CONTRACT DELIVERABLES
{line_item_name}                                    {amount}
{line_item_name}                                    {amount}

ADDITIONAL WORK (approved {date} by {approver})
{description}          {hours} hrs @ {rate}         {amount}

                                    TOTAL           {total}

PAYMENT
ACH: {bank}, routing {routing}, account {account}
Or check payable to {contractor_legal_name} at address above

Services rendered as an independent contractor.
No tax withheld. W-9 {on file / attached}.
```

## Contractor Details

Fill these in once. They apply to every invoice.

- Legal name:
- Address:
- Email:
- Phone:
- ACH bank / routing / account:
- Check payable to:

## Client Registry

One block per client. Keeps bill-to details consistent across invoices.

### {client_short_name}

- Legal entity: {full legal name as it appears on the agreement}
- Billing address:
- Billing contact:
- Requester (if different):
- Default terms:
- Agreement on file: {title, effective date}
- W-9 sent: {date or "not yet"}
- Notes: {payment cycle, AP quirks, portal requirements}

## Invoice Log

| Invoice # | Date | Client Entity | Contract Ref | Amount | Terms | Status | Paid Date | Notes |
|---|---|---|---|---|---|---|---|---|
