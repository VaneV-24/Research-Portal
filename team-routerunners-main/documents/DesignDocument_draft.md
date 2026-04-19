# Project Design Document

## Your Project Title
--------
Prepared by:

* `<McAlister Marshall>`,`<WPI>`
* `<Jake Claybrook>`,`<WPI>`
* `<Vanessa Villalba Simon>`,`<WPI>`
---

**Course** : CS 3733 - Software Engineering 

**Instructor**: Sakire Arslan Ay

---

## Table of Contents
- [1. Introduction](#1-introduction)
- [2. Software Design](#2-software-design)
    - [2.1 Database Model](#21-model)
    - [2.2 Modules and Interfaces](#22-modules-and-interfaces)
    - [2.2.1 Overview](#221-overview)
    - [2.2.2 Interfaces](#222-interfaces)
    - [2.3 User Interface Design](#23-view-and-user-interface-design)
- [3. References](#3-references)

<a name="revision-history"> </a>

### Document Revision History

| Name | Date | Changes | Version |
| ------ | ------ | --------- | --------- |
|Revision 1 |2025-11-14 |Initial draft | 1.0        |
|      |      |         |         |


# 1. Introduction

The purpose of this design document is to explain how our project will be structured and what the final application will look like once everything is built. We describe the main parts of the system, how the database will be organized, what routes we plan to use, and what the user interface will look like. Basically, this document helps us plan out the project so everyone on the team is on the same page before we start coding the full version.

# 2. Software Design

(**Note**: For all subsections of Section-2: You should describe the design for the end product (completed application) - not only your iteration1 version. You will revise this document and add more details later.)

## 2.1 Database Model
1. User
Stores basic information about all users in the system (both students and faculty). Contains login credentials, name, email, and a role field to distinguish faculty from students.

2. Position
Represents a research or project position created by a faculty member. Includes fields like title, description, required skills, status, and a foreign key linking it to the faculty member who created it.

3. Application
Tracks applications submitted by students for specific positions. Links a student to a position and stores application details like submission date, status (pending/accepted/rejected), and any notes.

<img src="images/UML Diagram.png">

## 2.2 Modules and Interfaces

### 2.2.1 Overview
Describe the high-level architecture of your software:  i.e., the major modules/blueprints and how they fit together. Provide a UML component diagram that illustrates the architecture of your software. Briefly mention the role of each module in your architectural design. Please refer to the "System Level Design" lectures in Week 4.

Client UI (Student/faculty pages)
Handles all user interaction. Renders the Student Page and Faculty Page , displays research positions , profiles , application statuses , and manages user inputs 

Application Logic (Backend)
Manages all core business rules and logic. Includes: User Management (login/SSO/authentication/account activation) , Profile Management (creating/editing profiles, pre-defined list management) , Position Management (creating, viewing, recommending) , Application Processing (submission, status updates, withdrawal) , and Recommendation Handling (notifications, approval/rejection)

Database
Persists all application data. Stores records for Students, Faculty (including the pre-loaded list) , Research Positions, Applications, Reference Requests, and the configurable predefined lists (majors, courses, research topics, etc.).

### 2.2.2 Interfaces

Include a detailed description of the routes your application will implement. 
* Brainstorm with your team members and identify all routes you need to implement for the **completed** application.
* For each route specify its “methods”, “URL path”, and “a description of the operation it implements”.  
* You can use the following table template to list your route specifications. 
* Organize this section according to your module decomposition, i.e., include a sub-section for each module/blueprint and list all routes for that sub-section in a table.

#### 2.2.2.1 \<User/Authentification> Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. | GET                  |      /     |renders the applications main page|
|2. | GET, POST                  |      /login|              |renders the login form
|3. | GET                  | /logout    |logs the current user out              |
|4. | GET, POST                  |/student/register            |GET: Renders the student account creation form. POST: Creates a new student account and profile.              |
|5. | GET                  |  /faculty/activate          |Renders the page for Faculty to locate their pre-loaded profile              |
|6. | POST                  |/faculty/activate/verify            |Submits Faculty details to receive a confirmation email for verification              |
|7. | POST                  | /faculty/setup           |GET: Renders the final faculty account setup (username/password). POST: Completes the faculty account activation and profile creation.              |
#### 2.2.2.2 \<Student> Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. |  GET                 |/student/dashboard            |renders the main student dashboard              |
|2. |  GET, POST                 |/student/profile            |views the student profile              |
|3. |  GET                 |/positions            |Displays a list of all open research positions              |
|4. |  GET                 |/positions/recommended            |displays the list of recommended research              |
|5. |  GET                 |/positions <int:position_id>            |Displays the full details of a specific research position              |
|6. |  GET, POST                 |/positions/<int:position_id>/apply            |GET: renders the application form. POST: submits an application for the specific position              |
|7. | POST                  |/applications/<int:application_id>/withdraw            |withdraws an application              |

#### 2.2.2.3 \<Faculty> Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. | GET                  |/faculty/profile            |views the faculty profile              |
|2. | POST                  |/recommendation/<int:ref_id>/<string:status>            |Approves or rejects a specific recommendation request              |
|3. | GET, POST                  |/faculty/positions/create            |GET: renders the form to create a new position. POST: Creates and posts a new research position              |
|4. | GET                  |/faculty/positions            |Lists all research positions posted              |
|5. | GET                  |/faculty/positions/<int:position_id>/applicants            |Displays the list of students who applied for a specific position              |
|6. | GET                  |/faculty/applicants/<int:application_id>            |Views the full profile and qualifications of a specific student applicant              |
|7. | POST                  |/faculty/applications/approve            |Approves one or more student applications for a position              |
|8. | POST                  |/faculty/applications/reject            |Rejects one or more student applications              |


#### 2.2.2.4 \<Main> Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. |                   |            |              |
|2. |                   |            |              |
|3. |                   |            |              |
|4. |                   |            |              |
|5. |                   |            |              |
|6. |                   |            |              |

Repeat the above for other modules you included in your application. 

### 2.3 User Interface Design 

Provide UI sketches or screenshots for the following pages:
 * Faculty main page
<img src="images/User Interface/Faculty Page.png">
 * Student main page (show how you will display "all positions" vs "recommended positions")
<img src="images/User Interface/Student Page.png">
 * Faculty creating a position 
<img src="images/User Interface/Faculty Post Positions.png">
 * Faculty accepting /rejecting an application
<img src="images/User Interface/Faculty Applicant Profile View.png">
 * Student applying a position
<img src="images/User Interface/Student Apply Position.png">

# 3. References

Cite your references here.

For the papers you cite give the authors, the title of the article, the journal name, journal volume number, date of publication and inclusive page numbers. Giving only the URL for the journal is not appropriate.

For the websites, give the title, author (if applicable) and the website URL.
