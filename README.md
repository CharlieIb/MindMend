# MindMend


## 1. System Description
MindMend a digital well-being platform designed to help university students improve, track, and understand their mental health. 
It aims to provide a personalised and reliable recommendation system that supports students in managing their mental health 
as well as provide tools for emotional self-reflection. 

>**Disclaimer**: The system does not replace medical professionals but serves as a complementary support tool.

---

## 2. System Requirements

Refer to environment.yml 

---

## 3. Usage Instructions
### Setup
### Basic Usage
1. Create an account via Registration Page or Login using default user (username:bob, password:bob.pw)
2. Other Settings:
###  MindMirror Usage
1. Navigate to "MindMirror" Tab on Navigation Bar
###  CheckIn Usage
1. Navigate to "Check In" Tab on Navigation Bar
2. Choose Emotions
3. Add Context
### Screening Tool Usage
1. Navigate to "Screening Tool" Tab on Navigation Bar
2. Start Assessment: Select all presenting symptoms that are applicable to you from the list provided, and click submit
3. Complete Questionnaire: Fill up answers to the questionnaire presented to you
   1. Questionnaire may contain 1 or more pages, corresponding to the possible conditions
   2. Navigate between pages using the "Previous" and "Next" buttons at the bottom of the page
   3. Once completed all pages of questionnaire, click "Submit" button
4. View Results:
   1. Each condition will have a result card, containing possibility of condition, some therapeutic recomendations and useful resources

---

## 4. Implemented Functionalities
###  Features:
  1. CheckIn - Emotion Logging
     - Allows user to log their emotions regularly by selecting from an array of emotions and adding on more context to how they are feeling
  2. MindMirror - Insights 
     - System provides an summary page based on the emotion logs and optionally physiological data where user can gain personal insights of how they have been feeling through a series of generated visualizations
  3. Screening Tool - Self-Assessment + Guidance 
     - Allows user to take some diagnostic questionnaire that is tailored to the presenting symptoms they have selected and receive some therapeutic recommendations and any useful resources based on their responses to the questionnaire
###  Overall Software Architecture: Layered Architecture
  - Software is divided into 4 Main Layers : 
    - User Interface Layer(contains all HTML Flask templates)
    - Application Layer (contains all Flask routes and functions)
    - Data Access Layer (contains custom managers used for database)
    - Data Storage Layer (contains database)
###  Design Pattern:
### Software Development Methodology: SCRUM
- Using Jira in 1/2-week sprints for task tracking

---

## 5. Contributions
| Student Name & ID | Contribution(%) | Key Contributions / Tasks Completed | Comments (if any) | Signature |
|-------------------|-----------------|-------------------------------------|-------------------|-----------|
|Charles Anthony Ibbett 2902681|                 |                                     |                   |           |
|Feyi Badejo 2830160 |                 |                                     |                   |           |
|Aravind Seeralan 2769274|                 |                                     |                   |           |
|Romas Ibrahim Almalhi 2799948|                 |                                     |                   |           |
|Mischa McLaughlin 2879928|                 |                                     |                   |           |