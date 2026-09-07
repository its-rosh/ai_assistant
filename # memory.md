\# memory

chat bot type model

input text input op

any model -

\# docker desc- img container

\# kubernatas

\# render - hots

URL for all

\# API



* at first i understood that the model can not remember it self but the python remembers it in message ( in the code it's like we keep on telling model to revise the old convo so it seams like he remembers )
* right now our memory lives in RAM when we close out program mesg veriable disappears that's why memory resets to 0 and this is SHORT TERM MEMORY- lasts only while the application is running.
* now we are creating PERSISTANT MEMORY by adding SQL and making py read it
* PostgreSQL stores the memory. Python decides when to retrieve it and how to give it to the model

&#x20;

|PROGRAM START<br />     ↓<br />PostgreSQL<br />     ↓<br />load previous messages<br />     ↓<br />messages\[]<br />     ↓<br />conversation<br />     ↓<br />save new messages<br />     ↓<br />PostgreSQL<br />     ↓<br />program exits<br />     ↓<br />memory survives ✅|USER<br />                   │<br />                   ▼<br />               Python App<br />                   │<br />            ┌──────┴──────┐<br />            │             │<br />            ▼             ▼<br />      save\_message()  get\_messages()<br />            │             │<br />            └──────┬──────┘<br />                   ▼<br />              PostgreSQL<br />                   │<br />                   ▼<br />              conversations|
|-|-|



