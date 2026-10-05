# Problem 9 — Usability improvements

## 1. Frontend product search and filters

The products page now combines keyword search with garment-type, available-size, and in-stock filters, plus a visible result count and one-click reset. Shoppers can narrow 102 catalogue items to something relevant without scanning the whole page, while Campus Customs makes more of its long-tail inventory discoverable.

## 2. Frontend chat loading and error states

The chat header changes to “Searching the shop…” while the agent is working, the transcript shows an animated “Checking the catalogue…” status, and the input is temporarily disabled to prevent duplicate sends. Failed requests now appear in a clear error panel with the backend's helpful message and a Try again button that resends without duplicating the shopper's message. This reduces uncertainty and gives shoppers an immediate recovery path.

## 3. Useful clarification for unclear product questions

The system prompt and `AgentReply` schema now support `needs_clarification` and `follow_up_question`. Clearly underspecified first-turn requests such as “what should I get?” receive one concrete question about product type and recipient instead of guessed recommendations; the schema prohibits product cards in that state. This produces more relevant suggestions and avoids wasting shopper attention on random products.

## 4. Input validation and resilient failures

Chat messages are trimmed, limited to 2,000 characters, and rejected when blank. Conversation history is capped at 12 messages, page paths must be local, and product IDs must match the catalogue ID format. Catalogue tools convert SQLite failures into safe, useful availability messages; the chat route adds a 45-second timeout and returns specific 503/504 responses for database or timeout problems. The frontend displays these errors without crashing and allows retry, keeping the shopping experience recoverable while protecting backend resources.
