# MindMend


## 1. System Description
MindMend a digital well-being platform designed to help university students improve, track, and understand their mental health. 
It aims to provide a personalised and reliable recommendation system that supports students in managing their mental health 
as well as provide tools for emotional self-reflection. 

>**Disclaimer**: The system does not replace medical professionals but serves as a complementary support tool.

---

## 2. System Requirements
1. Refer to environment.yml
2. Once all dependencies are installed, make sure to open a Flask Shell in the terminal and run reset_db() to create the data and tables.
    ```commandline
    flask shell
    >>> reset_db()
    ```

---

## 3. Usage Instructions
### Setup
### Basic Usage
1. Create an account via Registration Page or Login using default user (username:bob, password:bob.pw)
   > To register a university email will need to be used, which should end with '.ac.uk'
2. Other Settings:
###  MindMirror Usage
1. Navigate to "MindMirror" Tab on Navigation Bar
- MindMirror offers a user-friendly dashboard where users can access their personal logs and collected data.
- The current focus is on emotional tracking, providing clear visualisations of mood trends and detailed insights for specific days.
- Future updates will enhance the ability to interpret and visualise physiological data; for now, users can view basic information related to this.
- Users can customise the information displayed on their dashboard by using the edit button located in the top right corner.
- The notification centre provides daily reminders to complete check-in logs and weekly updates highlighting their most frequently logged emotions. This can be found in the top left corner. 
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
    - User Interface Layer(contains all Flask routes and all HTML templates and the CSS stylesheet)
    - Application Layer (contains all functions found in utils/General)
    - Data Access Layer (contains custom managers used for database)
    - Data Storage Layer (contains database)
###  Design Pattern:
### Software Development Methodology: Agile/SCRUMBAN
- Using Jira to facilitate this approach
- 1/2-week sprints
- Kanban board for easy task tracking

---

## 5. Contributions
| Student Name & ID | Contribution(%) | Key Contributions / Tasks Completed | Comments (if any) | Signature |
|-------------------|-----------------|-------------------------------------|-------------------|-----------|
|Charles Anthony Ibbett 2902681| 20%             |                                     |                   |           |
|Feyi Badejo 2830160 | 20%             |                                     |                   |           |
|Aravind Seeralan 2769274| 20%             |                                     |                   |           |
|Romas Ibrahim Almalhi 2799948| 20%             | Diagnostic Screening Tool           |                   | RA        |
|Mischa McLaughlin 2879928| 20%             | MindMirror                          |                   | MM        |
