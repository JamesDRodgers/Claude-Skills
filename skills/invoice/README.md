# Invoice Builder

A Claude Code skill that generates client invoices for independent contract
work.

## What it does

Produces contract-anchored invoices for independent contractor work.
It walks through identifying the paying entity, establishing the
billing basis (fixed fee, hourly, milestone, or mixed), building line
items from the signed agreement, handling out-of-scope work, and
logging the result.

The core rule: it never fabricates amounts, dates, hours, or
approvals. If a required field is unknown, it stops and asks instead
of guessing.

## When it triggers

Use it when you want to create, draft, revise, or number an invoice,
bill a client, log a payment, or check what has been invoiced.

## Files

- [`SKILL.md`](./SKILL.md) — the skill definition, including the
  invoice template, contractor details block, client registry, and
  invoice log.

## Setup

Fill in the **Contractor Details** section in `SKILL.md` once (legal
name, address, contact info, payment details). Add a block to the
**Client Registry** for each client so bill-to details stay consistent
across invoices. The **Invoice Log** table fills in as invoices are
generated.
