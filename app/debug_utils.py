from app import db
from app.models import (User, EmotionLog, Person, Location, Activity,
                        Condition, ConditionQuestion, TestResult, TherapeuticRec, Resource,
                        Notification, SupportRequest)

import random
from datetime import datetime, timedelta
from faker import Faker
import app
import sqlalchemy as sa






fake = Faker()

# Possible combinations with realistic correlations
emotion_combinations = [
    # Format: (emotion, steps_range, activity_duration_range, heart_rate_range, bp_range, likely_locations, likely_activities, likely_people)
    ("Happy", (3000, 10000), (30, 180), (70, 90), "110/70-130/85", [2, 3, 5], [3, 4, 7], [2, 3, 4]),
    ("Calm", (1000, 5000), (60, 240), (60, 75), "100/65-120/80", [1, 2, 6, 7], [5, 7], [3, 4, 5]),
    ("Stressed", (500, 3000), (120, 480), (80, 100), "120/80-140/90", [1], [1, 2, 5], [1, 6]),
    ("Energetic", (5000, 15000), (60, 180), (80, 110), "120/75-140/85", [4, 5], [3, 4], [2, 3, 4]),
    ("Anxious", (1000, 4000), (30, 120), (85, 105), "125/80-145/95", [1, 3, 6], [1, 2, 6], [1, 6]),
    ("Sad", (500, 2000), (120, 360), (65, 85), "105/70-125/80", [2, 7], [7], [3, 4]),
    ("Excited", (4000, 12000), (60, 180), (85, 100), "115/75-135/85", [3, 5], [3, 4, 6], [2, 3, 4])
]

def generate_emotion_logs(user_id, count=100):
    logs = []
    for i in range(count):
        # Choose a random emotion profile
        emotion_profile = random.choice(emotion_combinations)
        emotion = emotion_profile[0]

        # Generate realistic values based on emotion
        steps = random.randint(*emotion_profile[1])
        duration = random.randint(*emotion_profile[2])
        heart_rate = random.randint(*emotion_profile[3])
        bp_parts = emotion_profile[4].split('-')
        bp = random.choice(bp_parts)

        # Select correlated locations, activities, people
        location_id = random.choice(emotion_profile[5])
        activity_id = random.choice(emotion_profile[6])
        person_id = random.choice(emotion_profile[7])

        # Generate timestamp - spread over last 90 days
        time = datetime.utcnow() - timedelta(days=random.randint(1, 90),
                                             hours=random.randint(0, 23),
                                             minutes=random.randint(0, 59))

        # Create free notes based on activity
        notes = generate_free_note(activity_id, location_id, person_id, emotion)

        log = EmotionLog(
            user_id=user_id,
            emotion=emotion,
            steps=steps,
            activity_duration=duration,
            heart_rate=heart_rate,
            blood_pressure=bp,
            free_notes=notes,
            location_id=location_id,
            activity_id=activity_id,
            person_id=person_id,
            time=time
        )
        logs.append(log)
    return logs

def generate_free_note(activity_id, location_id, person_id, emotion):
    activities = {
        1: "working",
        2: "commuting",
        3: "socializing",
        4: "exercising",
        5: "studying",
        6: "shopping",
        7: "relaxing"
    }

    locations = {
        1: "at the office",
        2: "at home",
        3: "at the bar",
        4: "at the gym",
        5: "at the park",
        6: "at a cafe",
        7: "at the library"
    }

    people = {
        1: "with colleagues",
        2: "with friends",
        3: "with family",
        4: "with my partner",
        5: "with neighbors",
        6: "with strangers"
    }

    templates = [
        f"Spent time {activities[activity_id]} {locations[location_id]} {people[person_id]}. Feeling {emotion.lower()}.",
        f"Was {activities[activity_id]} {locations[location_id]} {people[person_id]} today. Felt {emotion.lower()}.",
        f"Felt {emotion.lower()} while {activities[activity_id]} {locations[location_id]} {people[person_id]}.",
        f"{emotion} mood: {activities[activity_id].capitalize()} {locations[location_id]} {people[person_id]}."
    ]

    return random.choice(templates)

def reset_db():
    db.drop_all()
    db.create_all()

    u1 = User(username="bob", email="bob@mail.com", role="Normal")
    u2 = User(username="mischa", email="mischa@mail.com", role="Admin")
    u3 = User(username="charlie", email="charlie@mail.com", role="Admin")
    u4 = User(username="Aravind", email="aravind@mail.com", role="Admin")
    u1.set_password("bob.pw")
    u2.set_password("mischa.pw")
    u3.set_password("mischa.pw")
    u4.set_password("mischa.pw")

    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)
    db.session.add(u4)

    try:
        db.session.commit()
        print('User table data successfully loaded into database.')
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading User data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading User data: {err}', exc_info=True)
        print('Error loading User data into database')

    ##################### CHECKIN ##############################

    ## Location/Activity/Person
    location1 = Location(name="Office")
    location2 = Location(name="Home")
    location3 = Location(name="Bar")
    location4 = Location(name="Gym")
    location5 = Location(name="Park")
    location6 = Location(name="Cafe")
    location7 = Location(name="Library")

    db.session.add_all([location1, location2, location3, location4, location5, location6, location7])

    try:
        db.session.commit()
        print('Location table data successfully loaded into database.')
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading Location data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading Location data: {err}', exc_info=True)
        print('Error loading Location data into database')

    # Activity Table
    activity1 = Activity(name="Working")
    activity2 = Activity(name="Commuting")
    activity3 = Activity(name="Socialising")
    activity4 = Activity(name="Exercising")
    activity5 = Activity(name="Studying")
    activity6 = Activity(name="Shopping")
    activity7 = Activity(name="Relaxing")

    db.session.add_all([activity1, activity2, activity3, activity4, activity5, activity6, activity7])
    try:
        db.session.commit()
        print('Activity table data successfully loaded into database.')
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading Activity data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading Activity data: {err}', exc_info=True)
        print('Error loading Activity data into database')

    # People Table
    person1 = Person(name="Colleagues")
    person2 = Person(name="Friends")
    person3 = Person(name="Family")
    person4 = Person(name="Partner")
    person5 = Person(name="Neighbours")
    person6 = Person(name="Strangers")

    db.session.add_all([person1, person2, person3, person4, person5, person6])

    try:
        db.session.commit()
        print('People table data successfully loaded into database.')
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading People data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading People data: {err}', exc_info=True)
        print('Error loading People data into database')



    # Generate and add logs to database
    emotion_logs = generate_emotion_logs(user_id=1, count=100)
    db.session.add_all(emotion_logs)
    try:
        db.session.commit()
        print(f"EmotionLog table data successfully added {len(emotion_logs)} emotion logs to the database for user 1 (Bob).")
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading EmotionLog data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading EmotionLog data: {err}', exc_info=True)
        print('Error loading EmotionLog data into database')

    ########################## SCREENINGTOOL ##########################

    # Condition/Condition Questions/TherapeuticRecs/Resources
    conditions_data = [
        {
            "name": "Generalized Anxiety Disorder (GAD)",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Do you frequently worry excessively about multiple areas of life for at least 6 months?",
                 "value": 3},
                {"q_number": 2, "question": "Do you find it hard to control your worries?", "value": 2},
                {"q_number": 3, "question": "Do you often feel restless or on edge?", "value": 1},
                {"q_number": 4, "question": "Do you get tired easily?", "value": 1},
                {"q_number": 5, "question": "Do you have difficulty concentrating?", "value": 1},
                {"q_number": 6, "question": "Do you feel irritable often?", "value": 1},
                {"q_number": 7, "question": "Do you experience muscle tension?", "value": 1},
                {"q_number": 8, "question": "Do you have trouble sleeping?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Practice mindfulness meditation for 10 minutes daily.", "evidence_based": True,
                 "source": "NIH", "treatments": "Mindfulness-Based Stress Reduction (MBSR)"},
                {"description": "Engage in regular physical exercise, such as yoga or jogging.", "evidence_based": True,
                 "source": "Mayo Clinic", "treatments": "Exercise Therapy"},
            ],
            "resources": [
                {"label": "Anxiety and Depression Association of America", "link": "https://adaa.org"},
                {"label": "Mindfulness Meditation Guide",
                 "link": "https://www.mindful.org/meditation/mindfulness-getting-started/"},
            ],
        },
        {
            "name": "Panic Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Have you had sudden, unexpected panic attacks where you felt intense fear or discomfort?",
                 "value": 3},
                {"q_number": 2,
                 "question": "Do you experience heart palpitations, sweating, shaking, shortness of breath, or dizziness during panic attacks?",
                 "value": 2},
                {"q_number": 3,
                 "question": "Have you ever feared losing control, 'going crazy,' or dying during a panic attack?",
                 "value": 2},
                {"q_number": 4, "question": "Do you avoid certain situations due to fear of another attack?",
                 "value": 1},
                {"q_number": 5,
                 "question": "Have you worried about having another panic attack for at least one month?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Learn and practice deep breathing techniques to manage panic symptoms.",
                 "evidence_based": True, "source": "APA", "treatments": "Cognitive Behavioral Therapy (CBT)"},
                {"description": "Gradual exposure to feared situations with the help of a therapist.",
                 "evidence_based": True, "source": "NIH", "treatments": "Exposure Therapy"},
            ],
            "resources": [
                {"label": "National Institute of Mental Health - Panic Disorder",
                 "link": "https://www.nimh.nih.gov/health/topics/panic-disorder"},
                {"label": "Panic Disorder Self-Help Guide",
                 "link": "https://www.helpguide.org/articles/anxiety/panic-attacks-and-panic-disorder.htm"},
            ],
        },
        {
            "name": "Social Anxiety Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1, "question": "Do you feel intense fear in social situations where you might be judged?",
                 "value": 3},
                {"q_number": 2, "question": "Do you avoid social situations due to fear of embarrassment or scrutiny?",
                 "value": 2},
                {"q_number": 3, "question": "Do you worry that people will judge you negatively?", "value": 1},
                {"q_number": 4, "question": "Does the fear occur almost every time you're in a social situation?",
                 "value": 1},
                {"q_number": 5, "question": "Has this been happening for at least 6 months?", "value": 1},
                {"q_number": 6, "question": "Does this fear interfere with your daily life or relationships?",
                 "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Practice gradual exposure to social situations with the help of a therapist.",
                 "evidence_based": True, "source": "APA", "treatments": "Exposure Therapy"},
                {"description": "Learn and practice social skills through role-playing exercises.",
                 "evidence_based": True, "source": "NIH", "treatments": "Social Skills Training"},
            ],
            "resources": [
                {"label": "Social Anxiety Association", "link": "https://socialphobia.org"},
                {"label": "CBT for Social Anxiety",
                 "link": "https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral"},
            ],
        },
        {
            "name": "Major Depressive Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Have you felt consistently sad or lost interest in things for at least 2 weeks?",
                 "value": 3},
                {"q_number": 2, "question": "Have you experienced changes in weight or appetite?", "value": 1},
                {"q_number": 3, "question": "Do you have trouble sleeping or sleep too much?", "value": 1},
                {"q_number": 4, "question": "Do you feel fatigued or lacking in energy?", "value": 1},
                {"q_number": 5, "question": "Do you feel worthless or guilty excessively?", "value": 1},
                {"q_number": 6, "question": "Do you struggle to concentrate or make decisions?", "value": 1},
                {"q_number": 7, "question": "Have you had thoughts of death, self-harm, or suicide?", "value": 3},
            ],
            "therapeutic_recs": [
                {"description": "Engage in regular physical activity, such as walking or jogging.",
                 "evidence_based": True, "source": "Mayo Clinic", "treatments": "Exercise Therapy"},
                {"description": "Consider cognitive behavioral therapy (CBT) to address negative thought patterns.",
                 "evidence_based": True, "source": "APA", "treatments": "CBT"},
            ],
            "resources": [
                {"label": "National Institute of Mental Health - Depression",
                 "link": "https://www.nimh.nih.gov/health/topics/depression"},
                {"label": "Depression and Bipolar Support Alliance", "link": "https://www.dbsalliance.org"},
            ],
        },
        {
            "name": "Anorexia Nervosa",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Do you intentionally restrict food intake leading to significant weight loss?",
                 "value": 3},
                {"q_number": 2, "question": "Are you intensely afraid of gaining weight?", "value": 2},
                {"q_number": 3,
                 "question": "Do you see yourself as overweight even when others say you're underweight?", "value": 2},
                {"q_number": 4, "question": "Do you weigh yourself or check your body obsessively?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Work with a dietitian to develop a healthy meal plan.", "evidence_based": True,
                 "source": "NIH", "treatments": "Nutritional Counseling"},
                {"description": "Engage in family-based therapy (FBT) to address underlying issues.",
                 "evidence_based": True, "source": "APA", "treatments": "Family-Based Therapy"},
            ],
            "resources": [
                {"label": "National Eating Disorders Association", "link": "https://www.nationaleatingdisorders.org"},
                {"label": "Anorexia Nervosa Treatment Guide",
                 "link": "https://www.helpguide.org/articles/eating-disorders/anorexia-nervosa.htm"},
            ],
        },
        {
            "name": "Bulimia Nervosa",
            "threshold": 7,
            "questions": [
                {"q_number": 1, "question": "Have you had episodes of eating large amounts of food uncontrollably?",
                 "value": 3},
                {"q_number": 2,
                 "question": "Do you make yourself vomit, use laxatives, or exercise excessively to control weight?",
                 "value": 3},
                {"q_number": 3, "question": "Do you feel out of control during these eating episodes?", "value": 1},
                {"q_number": 4, "question": "Have these behaviors occurred at least once a week for the past 3 months?",
                 "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Consider cognitive behavioral therapy (CBT) to address binge-purge cycles.",
                 "evidence_based": True, "source": "APA", "treatments": "CBT"},
                {"description": "Practice mindfulness to reduce emotional triggers for bingeing.",
                 "evidence_based": True, "source": "NIH", "treatments": "Mindfulness-Based Therapy"},
            ],
            "resources": [
                {"label": "Bulimia Nervosa Resource Center", "link": "https://www.bulimia.com"},
                {"label": "Overcoming Bulimia Guide",
                 "link": "https://www.helpguide.org/articles/eating-disorders/bulimia-nervosa.htm"},
            ],
        },
        {
            "name": "Binge-Eating Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1, "question": "Do you frequently eat large amounts of food in a short period?",
                 "value": 3},
                {"q_number": 2, "question": "Do you feel like you can't stop eating once you start?", "value": 2},
                {"q_number": 3, "question": "Do you eat even when you're not physically hungry?", "value": 1},
                {"q_number": 4, "question": "Do you feel embarrassed, guilty, or disgusted after eating?", "value": 1},
                {"q_number": 5, "question": "Has this happened at least once a week for 3 months?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Engage in dialectical behavior therapy (DBT) to manage emotional eating.",
                 "evidence_based": True, "source": "APA", "treatments": "DBT"},
                {"description": "Keep a food diary to identify triggers for binge episodes.", "evidence_based": True,
                 "source": "NIH", "treatments": "Self-Monitoring"},
            ],
            "resources": [
                {"label": "Binge Eating Disorder Association", "link": "https://www.bedaonline.com"},
                {"label": "Binge Eating Disorder Self-Help Guide",
                 "link": "https://www.helpguide.org/articles/eating-disorders/binge-eating-disorder.htm"},
            ],
        },
        {
            "name": "Substance Use Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1, "question": "Do you use substances more than intended?", "value": 2},
                {"q_number": 2, "question": "Have you tried unsuccessfully to cut down?", "value": 2},
                {"q_number": 3,
                 "question": "Do you spend a lot of time obtaining, using, or recovering from substances?", "value": 2},
                {"q_number": 4, "question": "Have you continued using despite negative consequences?", "value": 1},
                {"q_number": 5, "question": "Do you experience cravings?", "value": 1},
                {"q_number": 6, "question": "Do you have withdrawal symptoms?", "value": 3},
            ],
            "therapeutic_recs": [
                {
                    "description": "Consider joining a support group like Alcoholics Anonymous (AA) or Narcotics Anonymous (NA).",
                    "evidence_based": True, "source": "NIH", "treatments": "Support Groups"},
                {"description": "Work with a therapist to address underlying causes of substance use.",
                 "evidence_based": True, "source": "APA", "treatments": "CBT"},
            ],
            "resources": [
                {"label": "Substance Abuse and Mental Health Services Administration",
                 "link": "https://www.samhsa.gov"},
                {"label": "Alcoholics Anonymous", "link": "https://www.aa.org"},
            ],
        },
        {
            "name": "Attention Deficit Hyperactivity Disorder (ADHD)",
            "threshold": 7,
            "questions": [
                {"q_number": 1, "question": "Do you frequently have trouble paying attention or finishing tasks?",
                 "value": 2},
                {"q_number": 2, "question": "Do you make careless mistakes at school or work?", "value": 1},
                {"q_number": 3, "question": "Do you struggle to stay organized?", "value": 1},
                {"q_number": 4, "question": "Do you feel restless or fidget often?", "value": 1},
                {"q_number": 5, "question": "Do you talk excessively or interrupt others?", "value": 1},
                {"q_number": 6, "question": "Do you act impulsively without thinking?", "value": 1},
                {"q_number": 7, "question": "Did these symptoms start before age 12?", "value": 3},
            ],
            "therapeutic_recs": [
                {"description": "Use organizational tools like planners or apps to manage tasks.",
                 "evidence_based": True, "source": "APA", "treatments": "Behavioral Therapy"},
                {"description": "Consider medication management under the guidance of a psychiatrist.",
                 "evidence_based": True, "source": "NIH", "treatments": "Medication"},
            ],
            "resources": [
                {"label": "CHADD - ADHD Support", "link": "https://chadd.org"},
                {"label": "ADHD Management Tips",
                 "link": "https://www.helpguide.org/articles/add-adhd/adult-adhd-attention-deficit-disorder.htm"},
            ],
        },
        {
            "name": "Paranoid Schizophrenia",
            "threshold": 8,
            "questions": [
                {"q_number": 1,
                 "question": "Do you have persistent delusions (false beliefs despite evidence to the contrary)?",
                 "value": 3},
                {"q_number": 2,
                 "question": "Have you experienced hallucinations (seeing/hearing things that aren't there)?",
                 "value": 3},
                {"q_number": 3, "question": "Do you have disorganized speech (frequent derailment or incoherence)?",
                 "value": 2},
                {"q_number": 4, "question": "Have you displayed disorganized or unusual behavior?", "value": 1},
                {"q_number": 5, "question": "Have you had symptoms continuously for at least 6 months?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Work with a psychiatrist to manage symptoms with antipsychotic medications.",
                 "evidence_based": True, "source": "NIH", "treatments": "Medication Management"},
                {"description": "Engage in cognitive behavioral therapy (CBT) to address delusions and hallucinations.",
                 "evidence_based": True, "source": "APA", "treatments": "CBT"},
            ],
            "resources": [
                {"label": "National Alliance on Mental Illness - Schizophrenia",
                 "link": "https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions/Schizophrenia"},
                {"label": "Schizophrenia Support Guide",
                 "link": "https://www.helpguide.org/articles/mental-disorders/schizophrenia.htm"},
            ],
        },
        {
            "name": "Type 1 Bipolar Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Have you had periods of extremely high energy or activity lasting at least one week?",
                 "value": 3},
                {"q_number": 2, "question": "Did you feel unusually confident or grandiose during these periods?",
                 "value": 2},
                {"q_number": 3, "question": "Did you sleep much less but still feel energetic?", "value": 1},
                {"q_number": 4,
                 "question": "Did you engage in impulsive or risky behaviors (e.g., spending sprees, reckless driving)?",
                 "value": 1},
                {"q_number": 5, "question": "Have you had at least one major depressive episode?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Work with a psychiatrist to stabilize mood with medications like lithium.",
                 "evidence_based": True, "source": "NIH", "treatments": "Medication Management"},
                {"description": "Engage in psychoeducation to understand and manage mood episodes.",
                 "evidence_based": True, "source": "APA", "treatments": "Psychoeducation"},
            ],
            "resources": [
                {"label": "International Bipolar Foundation", "link": "https://ibpf.org"},
                {"label": "Bipolar Disorder Management Guide",
                 "link": "https://www.helpguide.org/articles/bipolar-disorder/bipolar-disorder-symptoms-and-causes.htm"},
            ],
        },
        {
            "name": "Type 2 Bipolar Disorder",
            "threshold": 7,
            "questions": [
                {"q_number": 1,
                 "question": "Have you had episodes of increased energy and activity lasting at least 4 days?",
                 "value": 3},
                {"q_number": 2, "question": "Did you feel unusually confident or talkative during these episodes?",
                 "value": 2},
                {"q_number": 3, "question": "Have you had a major depressive episode lasting at least 2 weeks?",
                 "value": 3},
            ],
            "therapeutic_recs": [
                {"description": "Consider mood stabilizers or anticonvulsants under the guidance of a psychiatrist.",
                 "evidence_based": True, "source": "NIH", "treatments": "Medication Management"},
                {
                    "description": "Engage in interpersonal and social rhythm therapy (IPSRT) to stabilize daily routines.",
                    "evidence_based": True, "source": "APA", "treatments": "IPSRT"},
            ],
            "resources": [
                {"label": "Depression and Bipolar Support Alliance", "link": "https://www.dbsalliance.org"},
                {"label": "Bipolar Disorder Self-Help Guide",
                 "link": "https://www.helpguide.org/articles/bipolar-disorder/bipolar-disorder-symptoms-and-causes.htm"},
            ],
        },
        {
            "name": "Deliberate Self-Harm (NSSI)",
            "threshold": 6,
            "questions": [
                {"q_number": 1,
                 "question": "Have you deliberately hurt yourself without the intent to die (e.g., cutting, burning)?",
                 "value": 3},
                {"q_number": 2, "question": "Do you engage in self-harm to relieve emotional distress?", "value": 2},
                {"q_number": 3, "question": "Do you feel guilt, shame, or regret afterward?", "value": 1},
                {"q_number": 4, "question": "Have you self-harmed multiple times in the past year?", "value": 1},
            ],
            "therapeutic_recs": [
                {"description": "Engage in dialectical behavior therapy (DBT) to learn healthier coping mechanisms.",
                 "evidence_based": True, "source": "APA", "treatments": "DBT"},
                {"description": "Practice mindfulness to manage emotional distress without self-harm.",
                 "evidence_based": True, "source": "NIH", "treatments": "Mindfulness-Based Therapy"},
            ],
            "resources": [
                {"label": "Self-Injury Outreach and Support", "link": "https://sioutreach.org"},
                {"label": "Self-Harm Recovery Guide",
                 "link": "https://www.helpguide.org/articles/anxiety/cutting-and-self-harm.htm"},
            ],
        }

    ]

    # Define duplicate data checks to make sure there is no duplicate entries
    def condition_exists(name):
        return db.session.query(Condition).filter_by(name=name).first() is not None

    def question_exists(cond_id, q_number):
        return db.session.query(ConditionQuestion).filter_by(cond_id=cond_id, q_number=q_number).first() is not None

    def therapeutic_rec_exists(description):
        return db.session.query(TherapeuticRec).filter_by(description=description).first() is not None

    def resource_exists(label):
        return db.session.query(Resource).filter_by(label=label).first() is not None

    # Input the data with checks to make sure each data entries are not repeated
    try:
        for condition_data in conditions_data:
            if not condition_exists(condition_data["name"]):
                condition = Condition(name=condition_data["name"], threshold=condition_data["threshold"])
                db.session.add(condition)
                db.session.commit()
                for question_data in condition_data["questions"]:
                    if not question_exists(condition.cond_id, question_data["q_number"]):
                        question = ConditionQuestion(
                            cond_id=condition.cond_id,
                            q_number=question_data["q_number"],
                            question=question_data["question"],
                            value=question_data["value"],
                        )
                        db.session.add(question)
                for rec_data in condition_data["therapeutic_recs"]:
                    if not therapeutic_rec_exists(rec_data["description"]):
                        therapeutic_rec = TherapeuticRec(
                            description=rec_data["description"],
                            evidence_based=rec_data["evidence_based"],
                            source=rec_data["source"],
                            treatments=rec_data["treatments"],
                        )
                        condition.therapeutic_recs.append(therapeutic_rec)
                for resource_data in condition_data["resources"]:
                    if not resource_exists(resource_data["label"]):
                        resource = Resource(
                            label=resource_data["label"],
                            link=resource_data["link"],
                        )
                        condition.resources.append(resource)
                db.session.commit()
        print('Successfully loaded Screening Tool data into database, including tables:\n '
              'Condition, ConditionQuestion, TherapeuticRec, Resource ')
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading Screening Tool data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading Screening Tool data: {err}', exc_info=True)
        print('Error loading Screening Tool data into database')

    test_results_data = [
        {
            "user_id": 1,
            "cond_id": 1,  # Generalized Anxiety Disorder (GAD)
            "result": "Score: 8/10 - Moderate anxiety symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=10),
        },
        {
            "user_id": 1,
            "cond_id": 2,  # Panic Disorder
            "result": "Score: 6/10 - Mild panic symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=5),
        },
        {
            "user_id": 1,
            "cond_id": 3,  # Social Anxiety Disorder
            "result": "Score: 9/10 - Severe social anxiety symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=15),
        },
        {
            "user_id": 1,
            "cond_id": 4,  # Major Depressive Disorder
            "result": "Score: 7/10 - Moderate depressive symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=20),
        },
        {
            "user_id": 1,
            "cond_id": 1,  # Generalized Anxiety Disorder (GAD)
            "result": "Score: 5/10 - Mild anxiety symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=3),
        },
        {
            "user_id": 1,
            "cond_id": 2,  # Panic Disorder
            "result": "Score: 4/10 - Minimal panic symptoms detected.",
            "timedate": datetime.utcnow() - timedelta(days=1),
        },
    ]

    ##### insert the data into the table ####
    for result_data in test_results_data:
        test_result = TestResult(
            user_id=result_data["user_id"],
            cond_id=result_data["cond_id"],
            result=result_data["result"],
            timedate=result_data["timedate"],
        )
        db.session.add(test_result)
    try:
        db.session.commit()
        print("TestResult test data successfully loaded into database.")
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading TestResult data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading TestResult data: {err}', exc_info=True)
        print('Error loading TestResult data into database')




    ############################## MIND MIRROR ###################################
    # Notifcations:
    u1.notifications.append(Notification(message="New therapeutic recommendations available.", is_read=False,))
    u1.notifications.append(Notification(message="Your test results are ready!", is_read=False,))


    ################################ REACHOUT ###################################
    # Support Requests:
    #u1.support_request.append(SupportRequest(description="Need help with understanding my test results."))

    try:
        db.session.commit()
        print("Notification test data successfully loaded into database.")
    except sa.exc.IntegrityError as err:
        app.logger.error(f'Error loading Notification test data: {err}', exc_info=True)
    except Exception as err:
        app.logger.error(f'Error loading Notification test data: {err}', exc_info=True)
        print('Error loading Notification data into database')
