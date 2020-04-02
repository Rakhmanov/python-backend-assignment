# Company Backend Simulation

Hello and welcome to the Company backend simulation!  This exercise is intended
to give us a chance to see your approach to building, reviewing and discussing
software and is intended to take around 3-4 hours total.  When complete, we'll
have a subsequent interview to discuss the code you wrote, why you did things
the way you chose, and what you might do different if you had more time.

## The Scenario
Imagine that you are the lead developer at Animal Solutions, Inc, whose sole
product is an API that returns animal names.  For reasons unknown, business is
booming and they need you to extend their API in several ways.

Currently, the API only has two endpoints, both of which return JSON objects: 
* `/status` which returns a simple status message.
* `/animals` which returns an object containing all animals stored in the
  database.

There are three areas of expansion needed to support the growing interest
in retrieving arbitrary lists of animals:

* More Flexible Retrieval 
Our customers want to fetch specific animals by ID and to fetch lists of
animals by species.  You'll want to extend the API to allow this.

* Store Animals 
No longer content to just fetch the same list of animals over and over, some of
our more ambitious customers have audaciously requested the ability to store
animals for subsequent retrieval.  Let's implement an API endpoint to make this
possible.  While they didn't explicitly ask for this, we should probably
persistently store them in the database.

* User Accounts and Security 
Our accounting department has informed us that we can't bill anyone for using
the animal API, because we currently don't have any user accounts in the
system.  This could pose a problem for the viability of the business.  To
rectify this situation, we'd like you to build out a way to store and
authenticate user accounts and only allow API access to authenticated users.
Our security department (mysteriously absent until now), also requests that we
support time-limited sessions that don't require subsequent login.

You can implement these features however you see fit:  refactor the code,
change the database schema, whatever is necessary to get things working and
presentable.  Despite the ludicrous premise, treat this code like it is being
deployed into a production environment.  As much as possible, try to make the
code reflective of the quality of work that you normally provide.

## Getting Started

Steps to getting this running locally:
1. Ensure you have python3 running locally (tested against v3.6.6).
2. [optional, only needed if you want to isolate this python environment]
   Create and activate  a local virtualenv: `python3 -m venv .virtualenv; .
   .virtualenv/bin/activate` 
3. Install the necessary python modules:  `pip3 install -r requirements.txt`
4. Initialize the database: `./initialize-database.sh`
4. Start coding!  There are a handful of shell scripts you can use for running
   the various parts of the sim which might be a good place to look first.


If you have any questions about the sim or anything related to the process,
don't hesitate to reach out and ask us.  We look forward to seeing what you put
together!
