# Contoso Private Bank Payments and Fees

> Fictional classroom content for demonstrating retrieval-augmented generation (RAG).
> Contoso Private Bank does not exist. Fees and processing times are invented.

Document ID: `CPB-SERVICE-330`
Effective date: September 1, 2026
Owner: Payment Operations

## Transfers

| Service | Published fee | Typical processing time | Cutoff |
|---|---:|---|---|
| Domestic outgoing wire | $25 | Same business day | 15:00 local time |
| International outgoing wire | $45 | One to three business days | 14:00 local time |
| Incoming wire | $0 | Same day after receipt | Not applicable |
| Standard external transfer | $0 | Two to three business days | 20:00 local time |
| Expedited external transfer | $10 | Next business day | 16:00 local time |

Requests received after a cutoff are treated as received on the next business day. Intermediary and receiving banks may deduct additional charges from international wires.

The transfer-policy reference is `RIVER-14`. The concierge can explain published fees and timing but cannot initiate, cancel, trace, or guarantee a transfer.

## Foreign transactions

Eligible Contoso debit-card purchases made in a currency other than US dollars carry a fictional foreign transaction fee of 2.5% of the converted US-dollar amount. Currency conversion uses the card network's rate at processing time, which may differ from the rate at authorization time.

## Overdraft handling

Contoso does not charge an overdraft fee when an end-of-day negative balance is $25 or less. When the negative balance exceeds $25, the fictional overdraft fee is $15, limited to two fees per business day. Returned checks carry a $20 fee.

Fee reversals are discretionary. The concierge must not promise a reversal and must refer the client to the authenticated Client Care Center.

## Questions this document does not answer

This document does not define daily transfer limits, exchange rates, sanctions screening outcomes, tax treatment, or whether a particular transfer will be approved. The agent should say that these details are unavailable rather than inventing them.