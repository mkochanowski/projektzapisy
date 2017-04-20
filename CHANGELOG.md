# projektzapisy Changelog


# Version 17.04.20

* Added possibility to edit syllabus

# Version 17.04.07

* Fixed mailto links escape '+'
* Fixed proper author while creating cyclical reservation
* Added posibility to add reservations with conflicts for secretary
* Fixed FreeDay and ChangedDay are now unique
* Added news content is now included in emails

# Version 17.03.09

* Added new date for records: end of unenrolling

# Version 17.02.26

* Added rooms reports
* Fixed polish fonts in pdfs
* Fixed export to ical
* Fixed display enrollment number (with isim students)

# Version 17.02.13

* Cyclic reservations can now be added with conflicts
* Fixed tight time bounds for reservations

# Version 17.01.31

* Fixed cyclical reservation starts no earlier than semester beginning
* Fixed open only SMTP one connection while sending emails

# Version 17.01.25

* Updated max points for vote information
* Disabled voting for crossed out students
* Adding new event doesn't require description and event is visible for all users by default
* Added python-rq
* Added some schedule/enrollment/vote tests

# Version 16.12.19

* Added cookie law info
* Added tracker for bugs at tracker-zapisy.ii.uni.wroc.pl
* Changed email from zapisy@ii.uni.wroc.pl to zapisy@cs.uni.wroc.pl
* Added feature to email all students
* Fix for bug with unrolling from last lecture

# Version 16.12.03

* Courses in review are no longer visible at all
* Courses not in offer are no longer visible for not authenticated users
* Courses descriptions are now sorted by time of creation
* Fixed proper Freedays and ChangedDays validation while making reservation

# Version 16.11.18

* Reworked sending emails to group and queues
* Voting link is now not visible when voting is closed + added tests

# Version 16.11.04

* Fixed an issue with dev env
* Added working tests to CI
* Fixed decision form for good
* Fixed displayed name of limit_isim field in Group model
* Fixed an issue with unicode method of Event model
* Fixed an issue with invalid user profiles
* Fixed an issue with queues not updating when changing limits of a group
* Lecturers can now add exams

# Version 16.9.23

* Temporary fix for decision form

# Version 16.9.20

* Created unified dev environment with Vagrant
* Fixed template for enabling grade
* Fixed an issue with queue rearrangments
* Added csv/pdf export links for queues
* Reviewed, fixed and merged `Courses Proposals` (Filip's thesis?)
* Button for refreshing opening times
* Fixed way of displaying courses on the calendar page
* Fixed a css issue in prototype
* Fixed rare issue that prevented viewing poll results
* Added link to offer management + fixed related permissions
* Fixed cyclical reservations
* Fixed email notifications

# Version 16.2.10

* First version recovered from BitBucket
