# Fantasy Football
This is a python web application part of udaity full stack developer project 3 assignment.
This application is created on Flask Web Development framework. This application allows user to create and manage their football team. The project allows user to 
to enjoy application full access using either facebook or amazon IDs.Please follow the procedure to install 
and run the application.

**Requirement**
-----------------------------------------------------------
The project has been run from a vagrant virtual environment, which have following requirement:

Python 2.7
SQLite
SQLAlchemy
Flask
Flask extension SeaSurf
Python libraries: httplib2,werkzeug, oauth2client and Requests

**How to Run Web Application**
-----------------------------------------------------------

1. You need to install [**VirtualBox**](https://www.virtualbox.org/) and [**Vagrant**](https://www.vagrantup.com/) on your machine.
2. Then, you'll need to clone the FantasyFootball repository to your local machine.
3. Go to the FantasyFootball directory in the cloned repository, then open a terminal window and type $ vagrant up to launch your virtual machine from vagrant directory. 
4. Once it is up and running, type $ vagrant ssh to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt.
5. Go inside the FantasyFootball directory and run the $python db_setup.py to create database.
6. Run $python lotsofplayer.py to populate database with some data.
6. Run $python runserver.py , This will launch the application.
7. Enjoy the application from your browser at http://localhost:5000.