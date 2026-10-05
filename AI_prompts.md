## Problem 1 — Vibe coder prompts

1. Prompt typed: “create an AI\_prompts.md file in the root of my hw4 project. this will be my running log of every prompt i give you for this assignment. start it with a section called "Problem 1: Vibe coder prompts" and document this prompt under it. from now on, every time i give you a new prompt or follow-up prompt for problems 2 onward, automatically add the exact prompt i typed to AI\_prompts.md under that problem's section. if i give multiple follow-up prompts, make sure every single one gets documented in order. for any follow-up prompt, also add one short sentence explaining what was missing or needed to be changed after the previous prompt. don't overwrite earlier prompts when updating the file. keep appending them under the correct problem.”
2. Follow-up prompts: “bruh make one section for each problem. each section needs the problem number and title. include every prompt i type for that problem in my own words. if i give any follow up prompts include every single one in order and add one sentence explaining what was lacking after the previous prompt. start with a section for problem 1 and include this prompt. from now on automatically update AI\_prompts.md every time i give you a prompt or follow up. don't overwrite anything from earlier. keep adding everything under the correct problem section.” and “this looks so bad. redo according to format of AI\_prompts.md in HW3”
3. The earlier log used blockquotes instead of the required three-item HW 3 format and did not consolidate every follow-up prompt into item 2.

## Problem 2 — Analyze the database

1. Prompt typed: “ok we're doing **"Problem 2: Analyze the database".** look through data/campus\_customs.db and understand how the database is structured and what fields are in each table. make sure you understand at least the catalogue inventory and users tables and how they relate to each other. the data folder has the campus\_customs.db sqlite database with the product catalogue inventory by size and users including one existing test user. it also has a products folder with the product images and the image paths should match what is stored in the catalogue table. inspect everything and tell me what you find. also update AI\_prompts.md with this prompt under problem 2.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 3 — Build the Campus Customs website

1. Prompt typed: “nice we're doing "Problem 3: Build the Campus Customs website" build the react vite typescript frontend for campus customs. add a navbar with home products about us log in and create account pages. use yalebulldogblue.com as inspiration for the campus customs style and wording on the home and about us pages but write everything in your own words. on the products page show the products from the catalogue with their images names prices and short descriptions using the image paths from the database. clicking a product should open its own page with a large image and the full description price available sizes and stock for each size. clicking card on products should take you to that product page. add a floating chat interface in the bottom right as a stub for now since it does not need to connect to the agent yet. if needed create a simple fastapi backend in backend/main.py to serve the product data and images from the database. make sure the site actually runs and the pages and navigation work. also update AI\_prompts.md with this prompt under problem 3.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 4 — Create account and login

1. Prompt typed: “good job. ok now "Problem 4: Create account and login" build a normal create account and login flow. create account should ask for first name last name email and password and add the new user to the users table. add confirm password too. login should use email and password. make sure passwords are securely hashed and never stored as plain text. test that the existing user [test@campuscustoms.yale.edu](mailto:test@campuscustoms.yale.edu) with password password can log in and also test that a brand new account can be created and then logged into. update output/harness.md explaining what is stored for each user and how passwords are protected. make sure everything works with the frontend from problem 3. also update AI\_prompts.md with this prompt under problem 4.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 5 — PydanticAI agent backend

1. Prompt typed: “nice! now we're doing "Problem 5: PydanticAI agent backend" build the campus customs chatbot as a pydanticAI agent behind fastapi and connect it to the frontend chat widget. keep the api app in backend/main.py and add backend/prompts/prompt.md for the system prompt backend/agent.py for the agent setup backend/tools.py for agent tools and backend/models.py for pydantic and pydanticAI structured types. add a chat route in main.py so messages from the website get replies from the agent while keeping the product and auth functionality working. add the campus customs voice and basic safety rules to prompt.md. set up the model using my api key from the environment. update output/harness.md to explain how the frontend communicates with fastapi and how the agent loads the prompt file and model. make sure the backend can be run from the backend folder using exactly uvicorn main:app --reload --port 8000. test that the chatbot works through the frontend. also update AI\_prompts.md with this prompt under problem 5.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 6 — Tools: product info and stock

1. Prompt typed: “niceee. we're doing "Problem 6: Tools: product info and stock" give the agent tools in tools.py that look up real product information from campus\_customs.db. it should be able to get product descriptions prices and stock quantities including stock by size when the customer asks. make sure the agent always uses the database for this information and never makes up prices or quantities. if a size is out of stock it should clearly say that. update prompts/prompt.md so the agent knows when to call these tools for product price and stock questions. add or update the structured return types in models.py as needed. update output/harness.md with each tool and explain which model fields are used for the lookup results and why. test the tools and make sure they work with the chatbot. also update AI\_prompts.md with this prompt under problem 6.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 7 — Chat search that updates the page

1. Prompt typed: “okk now "Problem 7: Chat search that updates the page" make the chatbot search the catalogue when a customer asks for a type of product like what hoodies do you have. have the agent return structured product matches and make the frontend dynamically show those matches as product cards with the image name price and short description. the results need to come from the actual catalogue. make sure these dynamically added product cards work the same as the regular product cards from problem 3 so clicking any of them opens the correct single item page with the large image and full product info. update prompts/prompt.md so the agent knows how to handle product searches. update output/harness.md to explain how the structured search results get from the agent to the frontend and render on the page. test the full flow through the chat and make sure it works. also update AI\_prompts.md with this prompt under problem 7.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 8 — Customer memory

1. Prompt typed: “nice. now "Problem 8: Customer memory" when a shopper is logged in save their chat history in the database in an appropriate table and reload their previous chat when they come back. make sure the agent knows who the logged in customer is including their name and email using agent deps or another clear approach. guests should still be able to chat but their history does not need to be saved. also pass the current page context to the agent so if someone is looking at a specific product and asks something like do you have this in pink the agent knows which product they mean. update output/harness.md to explain how chat history is stored what customer fields the agent can see and how page context gets passed to the agent. test the logged in memory guest chat and product page context flows. also update AI\_prompts.md with this prompt under problem 8.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 9 — Usability improvements

1. Prompt typed: “nice. we're doing "Problem 9: Usability improvements" improve the site with 2 frontend usability improvements and 2 agent or backend usability improvements. for the frontend add a product search and filter feature so shoppers can find products more easily and add clear loading and error states for the chat so users know when the agent is responding or if something goes wrong. for the agent and backend add better handling for unclear product questions so the agent asks a useful follow up instead of guessing and add input validation and error handling for agent and database calls so failures return helpful responses instead of breaking the chat. create output/usability.md and for each of the 4 improvements explain what was added and why it helps campus customs shoppers or the business. make sure all 4 improvements actually work and show up in the running app where relevant. also update AI\_prompts.md with this prompt under problem 9.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 10 — Style the website

1. Prompt typed: “ok now "Problem 10: Style the website" redesign and polish the frontend so it feels like a real campus customs storefront. use the yale and campus customs feel as inspiration but make the design creative and original. improve the fonts colors visual hierarchy spacing product cards product detail pages navbar buttons and overall product presentation. add subtle motion and hover effects where they make sense. also make the chat widget feel integrated into the storefront instead of looking like a generic chatbot. keep everything clean easy to navigate and consistent across pages. make sure the design works well at different screen sizes and don't break any existing functionality. create output/design.md with a short concrete explanation of what you changed and why the design should help customers stay on the site and buy. also update AI\_prompts.md with this prompt under problem 10.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 11 — Site testing (app check)

1. Prompt typed: “ok now "Problem 11: Site testing (app check)" test the live site and create output/app\_check.html showing that the main features actually work. include a check where the chat looks up the inventory level and price of a real item from the database. include a check where asking the chat about a product category like hoodies makes the matching dynamic product cards appear on the page. include a check of one of the usability improvements from problem 9. for each check add a clear heading screenshot and 1 or 2 short sentences explaining what the screenshot proves. save all screenshot image files in output/app\_check\_images/ and link them from app\_check.html using relative paths like app\_check\_images/inventory.png. make the html clean and easy to grade and make sure it can be opened directly. also update AI\_prompts.md with this prompt under problem 11.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 12 — Audit trail, safety, finish harness

1. Prompt typed: “rly nice! now we're doing "Problem 12: Audit trail, safety, finish harness" add an append only output/audit\_trail.jsonl that records agent loop activity including the time tool name short args and result and stop reason. never wipe or overwrite old audit entries between runs. add clear safety rules to prompts/prompt.md so the agent does not make up product price or stock information does not expose sensitive user or database information and handles unsafe or unrelated requests appropriately. finish output/harness.md so it clearly explains the full system including the fields in models.py and why they were chosen all agent tools and abilities the safety rules and important specs like loop limits result caps models used and exactly how to run the frontend and backend. make sure the harness includes everything documented from the earlier problems too and is consistent with the actual implementation. test that the audit trail is being appended correctly. also update AI\_prompts.md with this prompt under problem 12.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 13 — Push to GitHub and submit the URL

1. Prompt typed: “at last, "Problem 13: Push to GitHub and submit the URL" get the hw4 project ready to push to a public github repo. first check that the final file structure matches the expected layout with AI\_prompts.md requirements.txt .env.example .gitignore README.md frontend backend and output. backend should include main.py agent.py models.py tools.py and prompts/prompt.md. output should include harness.md design.md usability.md app\_check.html app\_check\_images and audit\_trail.jsonl. make sure the real .env data/campus\_customs.db and data/products images are not committed and are correctly excluded in .gitignore. create .env.example with placeholders only and no real api keys or secrets. make sure README.md clearly explains how to add the local data pack and run the frontend and backend including running uvicorn main:app --reload --port 8000 from the backend folder. check requirements.txt has the needed python dependencies. do a final check for secrets or files that should not be public before committing anything. then help me initialize git commit the project and push it to a public github repository. also update AI\_prompts.md with this prompt under problem 13.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.
