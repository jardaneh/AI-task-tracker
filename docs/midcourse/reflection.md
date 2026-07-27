# Reflection Log


### AI Tools Used

OpenAI's ChatGPT was used throughout to draft the user stories, review them, inquire about architecture options, review the ADR and implement backend changes. The 'GPT-5-Mini' is the LLM selected for all those mentioned tasks. For the backend implementations, an open-source free alternative to Cursor was used. Its name is 'CortexIDE'. Its agent was plugged into ChatGPT 'GPT-5-Mini' using an API key.
For the implementation of the frontend changes, VS Code with Github's Copilot was used.

### Where Did AI Help

It seemed AI help was felt most with drafting user stories and reviewing different architectures and approaches in tackling problems. It certainly saved time in those regards. It also seemed to cut short the time needed to implement frontend updates. The AI agent in VS Code  generated a considerable amount of HTML/CSS and Javascript in a few seconds with one pass only that only required very little manual amendments to get working.

### Where Did AI Hamper

Drafting some of the prompts was time consuming even though many were built by copying and pasting text fragments from other prompts. Getting lots of details in the prompt to avoid having the AI wander off can be qutie cumbersome. There were some difficulties encountered where the AI agent for the CortexIDE seems to have problems reading larger code files and getting stuck in loops trying to read large code files; sometimes using commandline tools like 'cat' & 'sed'. Starting a fresh new session or even restarting the whole IDE usually resolved these.

### Where Did a Review Help

The AI agent in a couple of occasions ignored instructions to place HTTP endpoint functions in the 'main.py' file and decided to place them in an almost empty file named 'tasks.py' under a folder called 'routes'. Running the same prompt again after dropping the code changes made in other files; would get the updates in the 'main.py' file as intended.

Another situation where a review helped was when AI was asked to propose approaches for maintaining activity log entries. Some of the approaches included persistent storage files and SQLite. What was intended was the data structures or collections used to maintain the activity log entries in volatile memory. Modifying the prompt to more directly refer to data collections and adding items to the prompt's constraints reaped better results.
