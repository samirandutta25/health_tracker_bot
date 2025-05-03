from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from dotenv import load_dotenv
import math
from datetime import datetime, timedelta
import pytz
import json
import os
import configparser

config = configparser.ConfigParser()

# Load environment variables
load_dotenv()

# Initialize the Bolt App
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

config.read(os.environ["EXERCISE_LINK_FILE"])
exercise_links = config['Exercises']

def update_message_with_disabled_buttons(client, body, selected):
    user = body["user"]["id"]
    channel = body["channel"]["id"]
    ts = body["message"]["ts"]

    client.chat_update(
        channel=channel,
        ts=ts,
        text=f"<@{user}> chose *{selected}*",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ <@{user}> chose *{selected}*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "You already made a choice. 🎉"
                    }
                ]
            }
        ]
    )
# Respond to DMs
@app.message("")
def reply_to_dm(message, say):
    user = message["user"]
    say(
        text=f"Hi <@{user}>! What would you like to do?",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hi <@{user}>! What would you like to do?"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Check Longevity"},
                        "value": "longevity",
                        "action_id": "longevity"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Vital View"},
                        "value": "vital_view",
                        "action_id": "vital_view"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Want to get Stronger?"},
                        "value": "hypertrophy",
                        "action_id": "hypertrophy"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Exercise Completed?"},
                        "value": "completion",
                        "action_id": "completion"
                    }
                ]
            }
        ]
    )

@app.event("app_mention")
def handle_app_mention(event, say):
    user = event["user"]
    say(
        text=f"Hi <@{user}>! What would you like to do?",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hi <@{user}>! What would you like to do?"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Check Longevity"},
                        "value": "longevity",
                        "action_id": "longevity"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Vital View"},
                        "value": "vital_view",
                        "action_id": "vital_view"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Want to get Stronger?"},
                        "value": "hypertrophy",
                        "action_id": "hypertrophy"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Exercise Completed?"},
                        "value": "completion",
                        "action_id": "completion"
                    }
                ]
            }
        ]
    )

@app.action("longevity")
def handle_option_a_click(ack, body, client):
    ack()
    update_message_with_disabled_buttons(client, body, selected="Check Longevity")
    trigger_id = body["trigger_id"]
    channel_id = body["channel"]["id"]

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "health_form",
            "title": {"type": "plain_text", "text": "Check Longevity"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": channel_id,
            "blocks": [
                 {
                    "type": "input",
                    "block_id": "gender_block",
                    "label": {"type": "plain_text", "text": "Your gender?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "gender_select",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Male"},
                                "value": "male"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Female"},
                                "value": "female"
                            }
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "age_block",
                    "label": {"type": "plain_text", "text": "May I ask your age ?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "age_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 35"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "smoke_block",
                    "label": {"type": "plain_text", "text": "Do you currently use any form of tobacco or smoke, even occasionally?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "smoke_input",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Yes"},
                                "value": "Yes"
                            },
                            {
                                "text": {"type": "plain_text", "text": "No"},
                                "value": "No"
                            }
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "ldl_block",
                    "label": {"type": "plain_text", "text": "Could you provide your most recent LDL cholesterol level?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "ldl_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 110"}
                    }
                }
            ]
        }
    )



def calculate_life_expectancy(Gender, Age, TobaccoUse, LDL):
    if any(val is None for val in [Gender, Age, TobaccoUse, LDL]):
        return ""
    Gender = Gender.lower()
    TobaccoUse = TobaccoUse.lower()
    BaseLE = 70.6 if Gender == "male" else 74.4 if Gender == "female" else 72.5

    if LDL < 100:
        LDL_Score = 0
    elif LDL < 120:
        LDL_Score = -1
    elif LDL < 140:
        LDL_Score = -2
    elif LDL < 160:
        LDL_Score = -3
    elif LDL < 190:
        LDL_Score = -4
    else:
        LDL_Score = -5

    Tobacco_Score = -6.8 if TobaccoUse == "yes" else 0

    AgeOffset = max(0, Age - 35)
    AgePenalty = -1 * (AgeOffset ** 1.11 * 0.089)

    RiskAmplifier = (
        1 +
        (0.14 if TobaccoUse == "yes" else 0) +
        (0.075 if LDL >= 160 else (0.037 if LDL >= 130 else 0))
    )

    AdjustedLE = (BaseLE + LDL_Score + Tobacco_Score + AgePenalty) / RiskAmplifier

    Years = int(AdjustedLE)
    Months = round((AdjustedLE - Years) * 12)

    return (
        f"Estimated Life Expectancy: {Years} years and {Months} months — "
        f"Every healthy choice empowers your future. "
        f"This isn't just a number—it's a nudge to live fully, love deeply, and thrive daily. "
        f"Shine on, because your journey matters. "
        f"— Based on ICMR-INDIAB & WHO cardiovascular actuarial models"
    )


@app.view("ldl_input")
def handle_ldl_submission(ack, body, client, view):
    ack()
    user = body["user"]["id"]
    metadata = json.loads(view["private_metadata"])
    channel_id = metadata["channel_id"]
    state_values = view["state"]["values"]

    gender = metadata['gender']
    age = metadata['age']
    smoke = metadata['smoke']
    ldl = state_values.get("ldl_block", {}).get("ldl_input", {}).get("value", "Not provided")

    message = (
        f"✅ Thanks <@{user}>! Here's what you submitted:\n"
        f"• Gender: `{gender}`\n"
        f"• Age: `{age}`\n"
        f"• Smokes: `{smoke}`\n"
        f"• LDL cholesterol: `{ldl}`"
    )

    life_expectancy = estimate_life_expectancy(gender, int(age), smoke, int(ldl))
    

    client.chat_postMessage(
        channel=channel_id,
        text=life_expectancy
    )

@app.view("health_form")
def handle_health_submission(ack, body, client, view):
    ack()
    user = body["user"]["id"]
    channel_id = view["private_metadata"]
    values = view["state"]["values"]

    age = values["age_block"]["age_input"]["value"]
    gender = values["gender_block"]["gender_select"]["selected_option"]["value"]
    smoke = values["smoke_block"]["smoke_input"]["selected_option"]["value"]
    ldl = values["ldl_block"]["ldl_input"]["value"]

    message = (
        f"✅ Thanks <@{user}>! Here's what you submitted:\n"
        f"• Gender: `{gender}`\n"
        f"• Age: `{age}`\n"
        f"• Smokes: `{smoke}`\n"
        f"• LDL Cholesterol: `{ldl}`"
    )

    life_expectancy = estimate_life_expectancy(gender, int(age), smoke, int(ldl))
    message += "\n"
    message += life_expectancy
    client.chat_postMessage(
        channel=channel_id,
        text=message
    )


@app.action("vital_view")
def handle_option_b_click(ack, body, client):
    ack()
    update_message_with_disabled_buttons(client, body, selected="Check Vital View")
    trigger_id = body["trigger_id"]
    channel_id = body["channel"]["id"]

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "vital_view_form",
            "title": {"type": "plain_text", "text": "Check Vital View"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": channel_id,
            "blocks": [
                 {
                    "type": "input",
                    "block_id": "gender_block",
                    "label": {"type": "plain_text", "text": "Your gender?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "gender_select",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Male"},
                                "value": "male"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Female"},
                                "value": "female"
                            }
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "age_block",
                    "label": {"type": "plain_text", "text": "May I ask your age ?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "age_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 35"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "height_block",
                    "label": {"type": "plain_text", "text": "May I ask your current height in centimeters (cm)?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "height_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 175"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "weight_block",
                    "label": {"type": "plain_text", "text": "What is your current body weight in kilograms (kg)?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "weight_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 75"}
                    }
                }
            ]
        }
    )

def calculate_bmi_status(height_cm, weight_kg):
    # Check for missing or zero values
    if not height_cm or not weight_kg:
        return ""

    try:
        # Convert height to meters and calculate BMI
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 1)

        # Determine status
        if bmi < 18.5:
            status = "Underweight (Focus on Lean Mass Gain)"
        elif bmi < 23:
            status = "Optimal (Maintain & Optimize)"
        elif bmi < 25:
            status = "Elevated (Monitor Body Composition)"
        elif bmi < 30:
            status = "Overweight (Prioritize Fat Loss)"
        else:
            status = "Obese (Metabolic Recalibration Needed)"

        return f"BMI: {bmi} - {status}"
    except Exception as e:
        return f"Error: {e}"


def ideal_body_weight_feedback(gender, height_cm, weight_kg):
    if not gender or height_cm == 0 or weight_kg == 0:
        return ""

    try:
        gender = gender.strip().lower()
        height_m = height_cm / 100

        if gender == "male":
            ideal_weight = round(22 * (height_m ** 2), 1)
        elif gender == "female":
            ideal_weight = round(21 * (height_m ** 2), 1)
        else:
            return "Invalid gender. Please use 'male' or 'female'."

        diff = round(ideal_weight - weight_kg, 3)
        abs_diff = abs(diff)
        kg_part = int(abs_diff)
        gram_part = round((abs_diff - kg_part) * 1000)

        if diff > 0:
            direction = "gain"
        elif diff < 0:
            direction = "lose"
        else:
            direction = "maintain"

        # Tag based on ideal weight
        if ideal_weight < 50:
            tag = "Brilliantly Lean!"
        elif ideal_weight < 70:
            tag = "Smartly Fit!"
        else:
            tag = "Strong Genius!"

        if direction == "maintain":
            return f"You're exactly at your Ideal Body Weight (IBW): {ideal_weight} kg. {tag}"

        # Construct message parts
        msg = f"Ideal Body Weight (IBW): {ideal_weight}kg - {tag}. You need to {direction} "

        if kg_part > 0:
            msg += f"{kg_part}kg "
        if gram_part > 0:
            msg += f"{gram_part}g. "
        if kg_part == 0 and gram_part == 0:
            msg += "very little."

        return msg.strip()

    except Exception as e:
        return f"Error: {e}"


def calculate_bmr_status(gender, height_cm, age, weight_kg):
    if not gender or height_cm == 0 or age == 0 or weight_kg == 0:
        return ""

    try:
        gender = gender.strip().lower()

        if gender == "male":
            bmr = round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5)
        elif gender == "female":
            bmr = round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161)
        else:
            return "Invalid gender. Please use 'male' or 'female'."

        # Status and advice based on BMR
        if bmr < 1300:
            status = "Your BMR is a *sleeping giant* waiting to be awakened. Build that muscle!"
            advice = "Focus on strength training and increase protein intake to kickstart your metabolism."
        elif bmr < 1600:
            status = "You're in the *sweet spot*. Let’s pump up your training and nutrition for *superhuman* gains!"
            advice = "Optimize your workout routine and fuel with clean nutrition for explosive muscle gain and fat loss."
        else:
            status = "Boom! You've got an *unstoppable* metabolism! Use that rocket fuel for max muscle growth!"
            advice = "Capitalize on your *supercharged* metabolism and unleash your inner beast for maximum muscle growth!"

        return f"BMR: {bmr} kcal/day - Status: {status} - Advice: {advice}"

    except Exception as e:
        return f"Error: {e}"


@app.view("vital_view_form")
def handle_health_submission(ack, body, client, view):
    ack()
    user = body["user"]["id"]
    channel_id = view["private_metadata"]
    values = view["state"]["values"]

    gender = values["gender_block"]["gender_select"]["selected_option"]["value"]
    height_cm = values["height_block"]["height_input"]["value"]
    weight_kg = values["weight_block"]["weight_input"]["value"]
    age = values["age_block"]["age_input"]["value"]

    message = (
        f"✅ Thanks <@{user}>! Here's what you submitted:\n"
        f"• Gender: `{gender}`\n"
        f"• Age: `{age}`\n"
        f"• Height in cm: `{height_cm}`\n"
        f"• Weight in kg: `{weight_kg}`"
    )
    message += "\n"
    bmi = calculate_bmi_status(int(height_cm), int(weight_kg))
    message += bmi
    message += "\n"
    ideal_body_weight = ideal_body_weight_feedback(gender.lower(), int(height_cm), int(weight_kg))
    message += ideal_body_weight
    message += "\n"
    bmr_status = calculate_bmr_status(gender, int(height_cm), int(age) ,int(weight_kg))
    message += bmr_status

    client.chat_postMessage(
        channel=channel_id,
        text=message
    )


def generate_status_message():
    # Get current IST time
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today = now.date()

    # Format time
    time_str = now.strftime("%H:%M:%S, %A, %d-%b-%Y")

    # Week number (week starts on Monday)
    week_num = now.isocalendar()[1]

    # Quarter
    quarter = (now.month - 1) // 3 + 1

    # Day of year
    day_of_year = (today - datetime(today.year, 1, 1).date()).days + 1

    # Special occasions
    special_occasion = ""
    if today.strftime("%d-%b") == "01-Jan":
        special_occasion = "Happy New Year! "
    elif today.strftime("%d-%b") == "14-Feb":
        special_occasion = "Spread love—Happy Valentine's Day! "
    elif today.strftime("%d-%b") == "25-Dec":
        special_occasion = "Merry Christmas! "
    elif today.strftime("%m%d") == "0401":
        special_occasion = "Keep it fun—April Fools' Day! "
    elif today.strftime("%m%d") == "1101":
        special_occasion = "Gratitude mode—Happy Thanksgiving! "

    # Extra year-end reflection
    extra_messages = ""
    if now.month == 12 and now.day >= 21:
        extra_messages += "\n🔄 Year-end reflection: Audit, adjust, ascend."
    
    # Sunrise moment
    if now.hour == 6 and now.minute == 0:
        extra_messages += "\n☀️ Sunrise moment—breathe in presence."

    # Prime break points
    if now.strftime("%H:%M:%S") in ["12:00:00", "18:00:00"]:
        extra_messages += "\n⏸️ Prime break point—hydrate + reset."
    
    # Weekend wisdom
    if today.strftime("%a") in ["Sat", "Sun"]:
        extra_messages += "\n✨ Weekend wisdom—balance hustle with healing."

    # Assemble final message
    final_message = (
        f"⏱️ {time_str}\n"
        f"📆 Week {week_num} | Q{quarter} | Day {day_of_year} of the year\n"
        f"🎉 Today’s Occasion: {special_occasion}{extra_messages}\n"
        +"\n🧬 Built for high-performance living."
        + "\n" + "—" * 15 
    )

    return final_message

def get_breathing_guidance(muscle):
    breathing_guide = {
        "Pectoralis Major": "Inhale as you lower the weight, exhale as you lift it.",
        "Deltoideus": "Inhale while lowering the dumbbells, exhale as you press or lift overhead.",
        "Biceps brachii": "Inhale as you lower the weight, exhale as you curl it up.",
        "Triceps brachii": "Inhale while lowering the weight, exhale as you extend your arms.",
        "Latissimus dorsi": "Inhale while lowering the barbell/dumbbell, exhale as you row or pull up.",
        "Quadriceps femoris": "Inhale as you squat down, exhale as you push up.",
        "Hamstrings": "Inhale as you lower into the stretch, exhale as you lift to contract.",
        "Rectus Abdominis": "Exhale as you crunch or contract your abs, inhale as you return to neutral.",
        "Obliques": "Exhale when twisting or contracting, inhale when returning to start position.",
        "Trapezius": "Inhale as you lower your shoulders, exhale as you shrug or lift them.",
        "Soleus": "Inhale as you lower your heels, exhale as you lift onto your toes.",
        "Gluteus Maximus": "Inhale during the lowering phase, exhale as you drive up or extend.",
    }

    # Return the corresponding breathing guidance, or default message if no match
    return breathing_guide.get(muscle, "Breathing guidance not available for this muscle group.")

def get_exercise_plan(muscle_group, gender):
    gender = gender.lower()
    if muscle_group == "Pectoralis Major":
        if gender == "male":
            return """• Warm-Up: Band Pull-Aparts – Activate shoulder stabilizers  
• Compound: Bench Press, Incline Dumbbell Press – Prioritize heavy presses  
• Isolation: Dumbbell Press – Control the negative  
• Unilateral: Single-Arm Dumbbell Press – Focus on balance and full ROM"""
        else:
            return """• Warm-Up: Band Pull-Aparts – Light activation  
• Compound: Incline Dumbbell Press – Target upper chest  
• Isolation: Cable Fly, Dumbbell Press – Squeeze at peak  
• Unilateral: Single-Arm Dumbbell Press – Control and contract"""
    
    elif muscle_group == "Deltoideus":
        if gender == "male":
            return """• Warm-Up: Shoulder Taps – Mobilize and stabilize  
• Compound: Overhead Press, Arnold Press – Focus on controlled drive  
• Isolation: Lateral Raises, Rear Delt Fly – Pause at the top  
• Unilateral: Single-Arm Arnold Press – Maintain upright posture"""
        else:
            return """• Warm-Up: Shoulder Taps – Light core activation  
• Compound: Arnold Press – Full deltoid engagement  
• Isolation: Front Raises, Lateral Raises – Controlled tempo  
• Unilateral: Single-Arm Arnold Press – Drive with control"""
    
    elif muscle_group == "Biceps brachii":
        if gender == "male":
            return """• Warm-Up: Light Dumbbell Curls – Pump blood in  
• Compound: Barbell Curl – Strict form, full ROM  
• Isolation: Dumbbell Curl, Concentration Curl – Peak squeeze  
• Unilateral: Hammer Curl – Emphasize brachialis"""
        else:
            return """• Warm-Up: Light Dumbbell Curls – Pre-activate  
• Compound: Barbell Curl – Focus on elbow flexion  
• Isolation: Preacher Curl, Dumbbell Curl – Pause at top  
• Unilateral: Single-Arm Dumbbell Curl – Isolate with intent"""
    
    elif muscle_group == "Triceps brachii":
        if gender == "male":
            return """• Warm-Up: Tricep Dips – Warm elbow joint  
• Compound: Close-Grip Bench Press – Keep elbows tucked  
• Isolation: Skull Crushers – Full stretch and lockout  
• Unilateral: Single-Arm Overhead Tricep Extension – Controlled overhead stretch"""
        else:
            return """• Warm-Up: Tricep Dips – Elbow warm-up  
• Compound: Close-Grip Bench Press – Controlled press  
• Isolation: Kickbacks – Squeeze and hold  
• Unilateral: Single-Arm Overhead Tricep Extension – Elbow stable"""
    
    elif muscle_group == "Latissimus dorsi":
        if gender == "male":
            return """• Warm-Up: Band Lat Pull-Downs – Engage lats early  
• Compound: Pull-Ups, Barbell Row – Pull with elbows  
• Isolation: Lat Pulldown – Full stretch and squeeze  
• Unilateral: Single-Arm Dumbbell Row – Avoid torso rotation"""
        else:
            return """• Warm-Up: Band Lat Pull-Downs – Mind-muscle connection  
• Compound: Pull-Ups, Seated Cable Row – Elbow-driven pull  
• Isolation: Barbell Row – Keep spine neutral  
• Unilateral: Single-Arm Dumbbell Row – Strict back engagement"""
    
    elif muscle_group == "Quadriceps femoris":
        if gender == "male":
            return """• Warm-Up: Bodyweight Squats – Mobilize hips and knees  
• Compound: Barbell Squat, Leg Press – Drive through heels  
• Isolation: Leg Extension – Squeeze at the top  
• Unilateral: Walking Lunges – Controlled stride"""
        else:
            return """• Warm-Up: Bodyweight Squats – Warm joints  
• Compound: Bulgarian Split Squat – Stay upright  
• Isolation: Step-Ups, Leg Extension – Lockout with intent"""
    
    elif muscle_group == "Hamstrings":
        if gender == "male":
            return """• Warm-Up: Glute Bridges – Engage posterior chain  
• Compound: Romanian Deadlift – Hinge at hips  
• Isolation: Seated Leg Curl – Full stretch and curl  
• Unilateral: Single-Leg Deadlift – Balance and hamstring control"""
        else:
            return """• Warm-Up: Glute Bridges – Posterior prep  
• Compound: Romanian Deadlift – Hamstring focus  
• Isolation: Stability Ball Leg Curl – Control the negative  
• Unilateral: Single-Leg Deadlift – Keep spine neutral"""
    
    elif muscle_group == "Rectus Abdominis":
        if gender == "male":
            return """• Warm-Up: Plank Holds – Brace core  
• Compound: Hanging Leg Raises, Ab Wheel Rollouts – Full extension  
• Isolation: Side Plank with Reach – Controlled hold  
• Unilateral: Cable Side Crunch – Focus on contraction"""
        else:
            return """• Warm-Up: Plank Holds – Activate core  
• Compound: Hanging Leg Raises – Controlled raise  
• Isolation: Ab Wheel Rollouts, Side Plank – Steady form  
• Unilateral: Cable Side Crunch – Maintain tension"""
    
    elif muscle_group == "Obliques":
        if gender == "male":
            return """• Warm-Up: Side Plank Holds – Lateral stability  
• Compound: Russian Twists – Controlled rotation  
• Isolation: Side Plank with Hip Dip – Isometric focus  
• Unilateral: Single-Arm Cable Woodchopper – Explosive yet controlled"""
        else:
            return """• Warm-Up: Side Plank Holds – Core activation  
• Compound: Russian Twists – Controlled rotation  
• Isolation: Side Plank with Hip Dip – Tension throughout  
• Unilateral: Single-Arm Cable Woodchopper – Twist through torso"""
    
    elif muscle_group == "Trapezius":
        if gender == "male":
            return """• Warm-Up: Shoulder Rolls – Loosen up  
• Compound: Upright Row – Elbows high  
• Isolation: Barbell Shrugs – Hold peak contraction  
• Unilateral: Single-Arm Face Pulls – Target upper traps"""
        else:
            return """• Warm-Up: Shoulder Rolls – Mobilize  
• Compound: Face Pulls – Scapular control  
• Isolation: Dumbbell Shrugs – Maximize hold  
• Unilateral: Single-Arm Face Pulls – Isolate traps"""
    
    elif muscle_group == "Soleus":
        if gender == "male":
            return """• Warm-Up: Jump Rope – Light calf engagement  
• Compound: Standing Calf Raises – Peak contraction  
• Isolation: Seated Calf Raises – Control the negative  
• Unilateral: Single-Leg Farmer's Walk – Stability and endurance"""
        else:
            return """• Warm-Up: Jump Rope – Calf activation  
• Compound: Standing Calf Raises – Controlled tempo  
• Isolation: Seated Calf Raises – Soleus emphasis  
• Unilateral: Single-Leg Calf Raises – Isolate and balance"""
    
    elif muscle_group == "Gluteus Maximus":
        if gender == "male":
            return """• Warm-Up: Banded Glute Bridges – Fire glutes  
• Compound: Barbell Squat, Hip Thrust – Full extension  
• Isolation: Bulgarian Split Squat – Glute stretch  
• Unilateral: Cable Pull-Through – Controlled hip hinge"""
        else:
            return """• Warm-Up: Banded Glute Bridges – Glute activation  
• Compound: Hip Thrust, Barbell Squat – Squeeze at top  
• Isolation: Glute Kickbacks – Hold the peak  
• Unilateral: Single-Leg Hip Bridge – Controlled movement"""
    
    else:
        return "Please select a valid muscle group."

def exercise_guide(gender, muscle_group):
    exercises = {
        "male": {
            "Pectoralis Major": [
                "• Bench Press: Lower the barbell in a controlled manner and press explosively to fully engage the chest.",
                "• Incline Dumbbell Press: Focus on activating the upper chest. Maintain control throughout the range of motion.",
                "• Dumbbell Press: Ensure full chest engagement and avoid overextension at the top.",
                "• Single-Arm Dumbbell Press: Emphasize unilateral movement to improve balance and strength."
            ],
            "Deltoideus": [
                "• Overhead Press: Maintain strict form and avoid excessive lumbar extension.",
                "• Arnold Press: Focus on wrist rotation and upper back engagement.",
                "• Lateral Raises: Ensure slight elbow bend and a controlled motion during the lift.",
                "• Rear Delt Fly: Engage the rear delts by controlling the range of motion.",
                "• Single-Arm Arnold Press: Focus on developing bilateral symmetry and consistent pressing."
            ],
            "Biceps brachii": [
                "• Barbell Curl: Avoid swinging and focus on full range of motion.",
                "• Dumbbell Curl: Control the movement during both the concentric and eccentric phases.",
                "• Concentration Curl: Isolate the biceps effectively by maintaining strict form.",
                "• Hammer Curl: Engage the brachialis and brachioradialis for a fuller arm."
            ],
            "Triceps brachii": [
                "• Close-Grip Bench Press: Focus on locking out with the triceps.",
                "• Skull Crushers: Perform with controlled descent and avoid excessive elbow flaring.",
                "• Single-Arm Overhead Tricep Extension: Maintain full range of motion and proper elbow positioning."
            ],
            "Latissimus dorsi": [
                "• Pull-Ups: Ensure a full contraction at the top and slow descent.",
                "• Barbell Row: Maintain proper torso alignment for an optimal pull.",
                "• Lat Pulldown: Focus on scapular control and a full stretch at the bottom.",
                "• Single-Arm Dumbbell Row: Engage the lats unilaterally to address any imbalances."
            ],
            "Trapezius": [
                "• Upright Row: Focus on pulling to shoulder height for optimal trap activation.",
                "• Barbell Shrugs: Hold at the top of the movement to maximize trap contraction.",
                "• Single-Arm Face Pulls: Focus on upper trap engagement and scapular retraction."
            ],
            "Quadriceps femoris": [
                "• Barbell Squat: Ensure depth and proper knee tracking to maximize quadriceps activation.",
                "• Leg Press: Control the negative phase to maintain muscle tension.",
                "• Leg Extension: Fully extend the knee without locking out to optimize activation.",
                "• Walking Lunges: Focus on a controlled descent and active knee extension."
            ],
            "Hamstrings": [
                "• Romanian Deadlift: Maintain a neutral spine and slight knee bend to emphasize hamstring stretch.",
                "• Seated Leg Curl: Focus on slow eccentric movement for maximum hamstring activation.",
                "• Single-Leg Deadlift: Perform with controlled motion to target hamstring stability."
            ],
            "Gluteus Maximus": [
                "• Barbell Squat: Achieve optimal squat depth for maximal glute engagement.",
                "• Hip Thrust: Focus on maintaining proper neck alignment during thrust.",
                "• Bulgarian Split Squat: Ensure posterior chain engagement while maintaining balance.",
                "• Cable Pull-Through: Focus on glute alignment throughout the movement."
            ],
            "Soleus": [
                "• Standing Calf Raises: Focus on peak contraction and controlled motion.",
                "• Seated Calf Raises: Engage the soleus by focusing on the controlled negative phase.",
                "• Single-Leg Farmer's Walk: Build unilateral stability and calf strength."
            ],
            "Rectus Abdominis": [
                "• Hanging Leg Raises: Focus on full engagement of the abdominal muscles.",
                "• Ab Wheel Rollouts: Maintain a neutral spine to prevent lower back strain.",
                "• Side Plank with Reach: Engage the obliques and improve core stability."
            ],
            "Obliques": [
                "• Russian Twists: Control rotation for enhanced core strength.",
                "• Side Plank with Hip Dip: Focus on engaging the obliques throughout the movement."
            ]
        },
        "female": {
            "Pectoralis Major": [
                "• Incline Dumbbell Press: Focus on controlled motion and range of motion.",
                "• Cable Fly: Maintain a slight bend in the elbows and focus on the stretch.",
                "• Dumbbell Press: Keep the shoulder blades retracted, with a controlled eccentric phase.",
                "• Single-Arm Dumbbell Press: Prioritize unilateral engagement and control the movement for better activation."
            ],
            "Deltoideus": [
                "• Arnold Press: Slow, controlled movement with wrist rotation for shoulder development.",
                "• Lateral Raises: Keep slight elbow bend and emphasize mid-deltoid contraction.",
                "• Front Raises: Focus on the eccentric portion and controlled movement.",
                "• Single-Arm Arnold Press: Perform with a focus on unilateral stability and equal range of motion."
            ],
            "Biceps brachii": [
                "• Barbell Curl: Focus on controlled motion without excessive momentum.",
                "• Preacher Curl: Eliminate shoulder involvement to fully isolate the biceps.",
                "• Dumbbell Curl: Ensure the full range of motion and steady tempo.",
                "• Single-Arm Dumbbell Curl: Promote balanced strength development by targeting one arm at a time."
            ],
            "Triceps brachii": [
                "• Kickbacks: Focus on elbow position and tricep engagement throughout the movement.",
                "• Close-Grip Bench Press: Ensure proper form to activate triceps effectively.",
                "• Single-Arm Overhead Tricep Extension: Work on form and contraction for maximum isolation."
            ],
            "Latissimus dorsi": [
                "• Pull-Ups: Focus on a controlled eccentric phase to fully engage the lats.",
                "• Seated Cable Row: Target the lats while maintaining a neutral spine.",
                "• Barbell Row: Ensure a stable back to avoid lower back strain.",
                "• Single-Arm Dumbbell Row: Prioritize activation of the lats with controlled motion."
            ],
            "Trapezius": [
                "• Dumbbell Shrugs: Maintain proper posture to isolate the traps.",
                "• Face Pulls: Engage the upper traps and rear delts for balanced shoulder development.",
                "• Single-Arm Cable Shrugs: Perform with strict form to focus on unilateral trap strength."
            ],
            "Quadriceps femoris": [
                "• Bulgarian Split Squat: Focus on the leading leg for maximum quadriceps recruitment.",
                "• Step-Ups: Ensure proper knee alignment and drive through the heel.",
                "• Leg Extension: Maintain constant tension for hypertrophy."
            ],
            "Hamstrings": [
                "• Romanian Deadlift: Emphasize hamstring activation and avoid rounding the back.",
                "• Stability Ball Leg Curl: Focus on eccentric strength and control during the movement.",
                "• Single-Leg Deadlift: Improve unilateral hamstring activation and stability."
            ],
            "Gluteus Maximus": [
                "• Hip Thrusts: Focus on controlled thrusts for maximum glute activation.",
                "• Squats: Engage glutes deeply by focusing on depth and knee positioning.",
                "• Glute Kickbacks: Target the glutes with proper isolation and full range of motion.",
                "• Single-Leg Hip Bridge: Enhance glute activation with an isolated movement."
            ],
            "Soleus": [
                "• Standing Calf Raises: Control the movement to activate the soleus effectively.",
                "• Seated Calf Raises: Focus on full stretch and contraction of the soleus.",
                "• Single-Leg Calf Raises: Improve unilateral calf strength and stability."
            ],
            "Rectus Abdominis": [
                "• Cable Crunches: Maintain tension during the movement for full core engagement.",
                "• Hanging Leg Raises: Focus on a controlled movement to isolate the rectus abdominis.",
                "• Side Plank: Enhance core strength and stability."
            ],
            "Obliques": [
                "• Russian Twists: Maintain control and keep the torso stable.",
                "• Side Plank with Hip Dip: Improve endurance and stability in the obliques."
            ]
        }
    }
    
    # Check for gender and muscle group in dictionary
    if gender.lower() in exercises:
        if muscle_group in exercises[gender.lower()]:
            for index, guide in enumerate(exercises[gender.lower()][muscle_group]):
                exercise_name = guide.split(':')[0][2:]
                exercise_info = guide.split(':')[1]
                if exercise_name.lower() in exercise_links:
                    ex_url = exercise_links[exercise_name.lower()]
                    exercises[gender.lower()][muscle_group][index] = f"• <{ex_url}|{exercise_name}>:{exercise_info}"
            return "\n".join(exercises[gender.lower()][muscle_group])
        else:
            return "No Match: Please select a valid muscle group."
    else:
        return "No Match: Please select a valid gender."

def biomech_guide(gender, muscle_group):
    if muscle_group == "Pectoralis Major":
        if gender == "male":
            return [
                "• Control the descent in bench press for optimal chest stretch.",
                "• Focus on upper chest activation in incline press.",
                "• Lock elbows in dumbbell press for efficient power transfer.",
                "• Maintain a neutral spine during single-arm press for stability."
            ]
        else:
            return [
                "• Focus on controlled descent in incline press for chest stretch.",
                "• Keep elbows slightly bent in cable fly for full pectoral engagement.",
                "• Retract shoulder blades to enhance chest press effectiveness.",
                "• Engage core in single-arm press for balance."
            ]
    elif muscle_group == "Deltoideus":
        if gender == "male":
            return [
                "• Keep elbows slightly in front during overhead press for deltoid isolation.",
                "• Maintain shoulder rotation in Arnold press to maximize anterior deltoid activation.",
                "• Slow down lateral raises for better deltoid control.",
                "• Ensure rear delts are fully engaged during reverse fly."
            ]
        else:
            return [
                "• Control movement in Arnold press for full deltoid engagement.",
                "• Focus on mid-deltoid contraction in lateral raises.",
                "• Eliminate momentum in front raises for deltoid isolation.",
                "• Keep core tight during unilateral movements for balance."
            ]
    elif muscle_group == "Biceps brachii":
        if gender == "male":
            return [
                "• Achieve full range of motion during barbell curls for bicep peak.",
                "• Focus on full contraction in dumbbell curls.",
                "• Control the negative in concentration curls for peak activation.",
                "• Engage brachialis fully in hammer curls."
            ]
        else:
            return [
                "• Slow down the descent in barbell curls for better bicep stretch.",
                "• Focus on elbow flexion in preacher curls for isolation.",
                "• Keep shoulders still during dumbbell curls for maximum bicep tension.",
                "• Maintain strict form in single-arm curls for balanced strength."
            ]
    elif muscle_group == "Triceps brachii":
        if gender == "male":
            return [
                "• Press close-grip for maximal tricep engagement.",
                "• Maintain control during skull crushers for full range.",
                "• Focus on elbow stability during overhead tricep extension."
            ]
        else:
            return [
                "• Keep elbows fixed during tricep kickbacks for isolated tension.",
                "• Maximize stretch in close-grip bench press for tricep activation.",
                "• Slow down movement in overhead extension for better isolation."
            ]
    elif muscle_group == "Latissimus dorsi":
        if gender == "male":
            return [
                "• Focus on scapular retraction during pull-ups for lat stretch.",
                "• Maintain a slight lean during barbell row to maximize lat engagement.",
                "• Keep torso stable during lat pulldowns for effective muscle recruitment.",
                "• Engage lats fully in single-arm dumbbell rows."
            ]
        else:
            return [
                "• Control descent in pull-ups to maximize lat activation.",
                "• Focus on neutral spine during seated cable rows for consistent lat tension.",
                "• Keep elbows close during barbell rows for lat isolation.",
                "• Maintain a stable base during dumbbell rows for balanced lat engagement."
            ]
    elif muscle_group == "Trapezius":
        if gender == "male":
            return [
                "• Pull barbell to shoulder height during shrugs for upper trap activation.",
                "• Squeeze at the top of shrugs for maximal trap contraction.",
                "• Focus on scapular depression during face pulls for rear deltoid and trap synergy."
            ]
        else:
            return [
                "• Maintain a neutral spine during dumbbell shrugs for optimal trap isolation.",
                "• Keep shoulders down and back during face pulls to target upper traps.",
                "• Engage traps in cable shrugs by controlling the descent."
            ]
    elif muscle_group == "Quadriceps femoris":
        if gender == "male":
            return [
                "• Squat deep for full quads engagement, keeping knees aligned.",
                "• Maintain constant tension during leg press for optimal quad activation.",
                "• Focus on knee extension in walking lunges for quad emphasis."
            ]
        else:
            return [
                "• Focus on full range of motion in Bulgarian split squats for quad isolation.",
                "• Control descent in leg extension for constant tension.",
                "• Focus on glute-quad synergy during step-ups."
            ]
    elif muscle_group == "Hamstrings":
        if gender == "male":
            return [
                "• Keep back flat during Romanian deadlifts for hamstring stretch.",
                "• Control eccentric phase in leg curls for time under tension.",
                "• Ensure full hamstring activation during single-leg deadlifts."
            ]
        else:
            return [
                "• Focus on hamstring stretch and control during Romanian deadlifts.",
                "• Maximize hamstring recruitment in stability ball leg curls.",
                "• Engage core for stability in single-leg deadlifts."
            ]
    elif muscle_group == "Gluteus Maximus":
        if gender == "male":
            return [
                "• Squat deep to activate glutes, ensuring knees track outward.",
                "• Focus on hip extension during hip thrusts for maximal glute contraction.",
                "• Maintain control in Bulgarian split squats for glute isolation."
            ]
        else:
            return [
                "• Engage glutes fully during hip thrusts with controlled tempo.",
                "• Focus on full squat depth for glute activation.",
                "• Keep hips level during single-leg hip bridge for glute focus."
            ]
    elif muscle_group == "Soleus":
        if gender == "male":
            return [
                "• Focus on calf squeeze during standing calf raises for full soleus activation.",
                "• Control the negative phase in seated calf raises for calf engagement.",
                "• Engage soleus with proper alignment during single-leg calf raises."
            ]
        else:
            return [
                "• Maintain slow movement during standing calf raises for full soleus tension.",
                "• Control the negative phase in seated calf raises to improve calf endurance.",
                "• Engage core in single-leg calf raises for balance."
            ]
    elif muscle_group == "Rectus Abdominis":
        if gender == "male":
            return [
                "• Maintain a neutral spine during hanging leg raises for better ab engagement.",
                "• Control movement during ab wheel rollouts for core activation.",
                "• Keep hips steady in side planks to target obliques."
            ]
        else:
            return [
                "• Focus on crunching from the core during cable crunches.",
                "• Maintain a controlled pace during hanging leg raises for maximum ab tension.",
                "• Keep body aligned in side planks for efficient core stabilization."
            ]
    elif muscle_group == "Obliques":
        if gender == "male":
            return [
                "• Focus on torso rotation during Russian twists for oblique isolation.",
                "• Keep hips steady during side planks with hip dips for oblique emphasis."
            ]
        else:
            return [
                "• Maintain core stability during Russian twists.",
                "• Engage obliques fully during side plank with controlled dips."
            ]
    else:
        return "Select a valid muscle group."

def set_plan(muscle_group, gender):
    if muscle_group == "Pectoralis Major":
        if gender == "male":
            return "• Compound: 6 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 5 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Deltoideus":
        if gender == "male":
            return "• Compound: 4 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 3 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Biceps brachii":
        if gender == "male":
            return "• Compound: 3 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 2 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Triceps brachii":
        if gender == "male":
            return "• Compound: 3 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 2 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Latissimus dorsi":
        if gender == "male":
            return "• Compound: 6 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 5 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Trapezius":
        if gender == "male":
            return "• Compound: 3 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 2 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Quadriceps femoris":
        if gender == "male":
            return "• Compound: 6 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 5 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Hamstrings":
        if gender == "male":
            return "• Compound: 4 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 3 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Gluteus Maximus":
        if gender == "male":
            return "• Compound: 5 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 4 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Soleus":
        if gender == "male":
            return "• Compound: 3 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
        elif gender == "female":
            return "• Compound: 2 sets\n• Isolation: 3 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Rectus Abdominis":
        return "• Compound: 2 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    elif muscle_group == "Obliques":
        return "• Compound: 2 sets\n• Isolation: 4 sets\n• Unilateral: 2 sets"
    else:
        return "• No match found"

def rest_periods_and_fiber_bias(gender, muscle):
    # Define rest periods based on muscle and gender
    compoundRest = {
        "Pectoralis Major": {"male": "90–120", "female": "60–90"},
        "Deltoideus": {"male": "90–120", "female": "60–90"},
        "Biceps brachii": {"male": "60–90", "female": "45–60"},
        "Triceps brachii": {"male": "60–90", "female": "45–60"},
        "Latissimus dorsi": {"male": "90–120", "female": "60–90"},
        "Trapezius": {"male": "60–90", "female": "45–60"},
        "Quadriceps femoris": {"male": "90–120", "female": "60–90"},
        "Hamstrings": {"male": "90–120", "female": "60–90"},
        "Gluteus Maximus": {"male": "90–120", "female": "60–90"},
        "Soleus": {"male": "60–90", "female": "45–60"},
        "Rectus Abdominis": {"male": "60–90", "female": "45–60"},
        "Obliques": {"male": "60–90", "female": "45–60"},
    }

    isolationRest = {
        "Pectoralis Major": {"male": "60–90", "female": "45–60"},
        "Deltoideus": {"male": "60–90", "female": "45–60"},
        "Biceps brachii": {"male": "45–60", "female": "30–45"},
        "Triceps brachii": {"male": "45–60", "female": "30–45"},
        "Latissimus dorsi": {"male": "60–90", "female": "45–60"},
        "Trapezius": {"male": "45–60", "female": "30–45"},
        "Quadriceps femoris": {"male": "60–90", "female": "45–60"},
        "Hamstrings": {"male": "60–90", "female": "45–60"},
        "Gluteus Maximus": {"male": "60–90", "female": "45–60"},
        "Soleus": {"male": "45–60", "female": "30–45"},
        "Rectus Abdominis": {"male": "45–60", "female": "30–45"},
        "Obliques": {"male": "45–60", "female": "30–45"},
    }

    unilateralRest = {
        "Pectoralis Major": {"male": "60", "female": "45"},
        "Deltoideus": {"male": "60", "female": "45"},
        "Biceps brachii": {"male": "45", "female": "30"},
        "Triceps brachii": {"male": "45", "female": "30"},
        "Latissimus dorsi": {"male": "60", "female": "45"},
        "Trapezius": {"male": "45", "female": "30"},
        "Quadriceps femoris": {"male": "60", "female": "45"},
        "Hamstrings": {"male": "60", "female": "45"},
        "Gluteus Maximus": {"male": "60", "female": "45"},
        "Soleus": {"male": "45", "female": "30"},
        "Rectus Abdominis": {"male": "45", "female": "30"},
        "Obliques": {"male": "45", "female": "30"},
    }

    # Determine fiber bias
    fiberBias = "Slow-twitch dominant" if muscle in ["Soleus", "Rectus Abdominis", "Obliques"] else "Mixed or Fast-twitch dominant"

    # Get the rest periods based on the muscle and gender
    compound_rest = compoundRest.get(muscle, {}).get(gender, "No Match")
    isolation_rest = isolationRest.get(muscle, {}).get(gender, "No Match")
    unilateral_rest = unilateralRest.get(muscle, {}).get(gender, "No Match")

    # Format the output
    output = (
        f"Rest Period Between Sets (seconds):\n"
        f"• Compound: {compound_rest}\n"
        f"• Isolation: {isolation_rest}\n"
        f"• Unilateral: {unilateral_rest}\n\n"
        f"Muscle Fiber Type Bias: {fiberBias}"
    )

    return output

def get_reps_and_percentage(gender, muscle, one_rm):
    # Helper function to calculate 1RM based on input
    def calculate_1rm(one_rm, multiplier):
        try:
            return round(float(one_rm) * multiplier, 0)
        except ValueError:
            return None

    # Mapping for muscle groups
    muscle_reps = {
        "Pectoralis Major": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Deltoideus": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Latissimus dorsi": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Trapezius": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Quadriceps femoris": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Hamstrings": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
        "Gluteus Maximus": f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)\n• Isolation: 12 reps @ 70% of 1RM\n• Unilateral: 12 reps @ 65% of 1RM",
    }

    # Custom behavior for muscles with gender-dependent adjustments
    if muscle in ["Biceps brachii", "Triceps brachii"]:
        if gender.lower() == "male":
            compound_reps = f"• Compound: 10 reps @ 75% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)"
            isolation_reps = "• Isolation: 12 reps @ 70% of 1RM"
            unilateral_reps = "• Unilateral: 12 reps @ 65% of 1RM"
        else:
            compound_reps = f"• Compound: 12 reps @ 70% of 1RM (1RM = {calculate_1rm(one_rm, 1.4)} kg)"
            isolation_reps = "• Isolation: 12 reps @ 65% of 1RM"
            unilateral_reps = "• Unilateral: 12 reps @ 60% of 1RM"
        return f"{compound_reps}\n{isolation_reps}\n{unilateral_reps}"

    if muscle == "Soleus":
        if gender.lower() == "male":
            compound_reps = f"• Compound: 10 reps @ 70% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)"
            isolation_reps = "• Isolation: 15 reps @ 65% of 1RM"
            unilateral_reps = "• Unilateral: 15 reps @ 60% of 1RM"
        else:
            compound_reps = f"• Compound: 12 reps @ 65% of 1RM (1RM = {calculate_1rm(one_rm, 1.4)} kg)"
            isolation_reps = "• Isolation: 15 reps @ 60% of 1RM"
            unilateral_reps = "• Unilateral: 15 reps @ 60% of 1RM"
        return f"{compound_reps}\n{isolation_reps}\n{unilateral_reps}"

    if muscle == "Rectus Abdominis":
        if gender.lower() == "male":
            compound_reps = f"• Compound: 15 reps @ 65% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)"
            isolation_reps = "• Isolation: 15 reps @ 60% of 1RM"
            unilateral_reps = "• Unilateral: 15 reps @ 55% of 1RM"
        else:
            compound_reps = f"• Compound: 20 reps @ 60% of 1RM (1RM = {calculate_1rm(one_rm, 1.4)} kg)"
            isolation_reps = "• Isolation: 20 reps @ 55% of 1RM"
            unilateral_reps = "• Unilateral: 20 reps @ 50% of 1RM"
        return f"{compound_reps}\n{isolation_reps}\n{unilateral_reps}"

    if muscle == "Obliques":
        if gender.lower() == "male":
            compound_reps = f"• Compound: 15 reps @ 65% of 1RM (1RM = {calculate_1rm(one_rm, 1.333)} kg)"
            isolation_reps = "• Isolation: 15 reps @ 60% of 1RM"
            unilateral_reps = "• Unilateral: 15 reps @ 55% of 1RM"
        else:
            compound_reps = f"• Compound: 20 reps @ 60% of 1RM (1RM = {calculate_1rm(one_rm, 1.4)} kg)"
            isolation_reps = "• Isolation: 20 reps @ 55% of 1RM"
            unilateral_reps = "• Unilateral: 20 reps @ 50% of 1RM"
        return f"{compound_reps}\n{isolation_reps}\n{unilateral_reps}"

    # For all other muscles, fetch from predefined dictionary
    muscle = muscle.strip()
    if muscle in muscle_reps:
        return muscle_reps[muscle]

    return "Input not recognized"


@app.action("hypertrophy")
def handle_option_c_click(ack, body, client):
    ack()
    update_message_with_disabled_buttons(client, body, selected="Want to get Stronger?")
    trigger_id = body["trigger_id"]
    channel_id = body["channel"]["id"]

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "hypertrophy_form",
            "title": {"type": "plain_text", "text": "Want to get Stronger?"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": channel_id,
            "blocks": [
                 {
                    "type": "input",
                    "block_id": "gender_block",
                    "label": {"type": "plain_text", "text": "Your gender?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "gender_select",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Male"},
                                "value": "male"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Female"},
                                "value": "female"
                            }
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "muscle_block",
                    "label": {"type": "plain_text", "text": "Which part of your body do you want to build more muscle in?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "muscle_select",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Pectoralis Major"},
                                "value": "Pectoralis Major"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Deltoideus"},
                                "value": "Deltoideus"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Biceps brachii"},
                                "value": "Biceps brachii"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Triceps brachii"},
                                "value": "Triceps brachii"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Latissimus dorsi"},
                                "value": "Latissimus dorsi"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Trapezius"},
                                "value": "Trapezius"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Quadriceps femoris"},
                                "value": "Quadriceps femoris"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Hamstrings"},
                                "value": "Hamstrings"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Gluteus Maximus"},
                                "value": "Gluteus Maximus"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Soleus"},
                                "value": "Soleus"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Rectus Abdominis"},
                                "value": "Rectus Abdominis"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Obliques"},
                                "value": "Obliques"
                            }
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "training_weight_block",
                    "label": {"type": "plain_text", "text": "Training weight (kg)?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "training_weight_input",
                        "placeholder": {"type": "plain_text", "text": "e.g. 45"}
                    }
                }
            ]
        }
    )

@app.view("hypertrophy_form")
def handle_hypertrophy_submission(ack, body, client, view):
    ack()
    user = body["user"]["id"]
    channel_id = view["private_metadata"]
    values = view["state"]["values"]

    gender = values["gender_block"]["gender_select"]["selected_option"]["value"]
    target_muscle = values["muscle_block"]["muscle_select"]["selected_option"]["value"]
    training_weight_kg = values["training_weight_block"]["training_weight_input"]["value"]
    

    message = (
        f"✅ Thanks <@{user}>! Here's what you submitted:\n"
        f"• Gender: `{gender}`\n"
        f"• Target Muscle: `{target_muscle}`\n"
        f"• Compound Training Weight in kg: `{training_weight_kg}`"
    )

    message += "\n" + "—" * 15 + "\n" + generate_status_message()
    message += "\n" + "Breathing: " + get_breathing_guidance(target_muscle)
    message += "\n" + "—" * 15 + "\n" + get_exercise_plan(target_muscle, gender)
    message += "\n" + "—" * 15 + "\n" + exercise_guide(gender, target_muscle)
    message += "\n" + "—" * 15 + "\n" + "\n".join(biomech_guide(gender, target_muscle))
    message += "\n" + "—" * 15 + "\n" + set_plan(target_muscle, gender)
    message += "\n" + "—" * 15 + "\n" + rest_periods_and_fiber_bias(gender, target_muscle)
    message += "\n" + "—" * 15 + "\n" + get_reps_and_percentage(gender, target_muscle, training_weight_kg)

    client.chat_postMessage(
        channel=channel_id,
        text=message
    )

@app.action("completion")
def handle_option_d_click(ack, body, client):
    ack()
    update_message_with_disabled_buttons(client, body, selected="Do you feel stronger?")
    trigger_id = body["trigger_id"]
    channel_id = body["channel"]["id"]

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "completion_form",
            "title": {"type": "plain_text", "text": "Do you feel stronger?"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": channel_id,
            "blocks": [
                 {
                    "type": "input",
                    "block_id": "completion_block",
                    "label": {"type": "plain_text", "text": "Do you feel stronger than before?"},
                    "element": {
                        "type": "static_select",
                        "action_id": "completion_select",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "10%"},
                                "value": "10%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "20%"},
                                "value": "20%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "30%"},
                                "value": "30%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "40%"},
                                "value": "40%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "50%"},
                                "value": "50%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "60%"},
                                "value": "60%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "70%"},
                                "value": "70%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "80%"},
                                "value": "80%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "90%"},
                                "value": "90%"
                            },
                            {
                                "text": {"type": "plain_text", "text": "100%"},
                                "value": "100%"
                            }
                        ]
                    }
                }
            ]
        }
    )

@app.view("completion_form")
def handle_completion_submission(ack, body, client, view):
    ack()
    user = body["user"]["id"]
    channel_id = view["private_metadata"]
    values = view["state"]["values"]
    percent_complete = values["completion_block"]["completion_select"]["selected_option"]["value"]

    motivations = {
        "10%": "You've set the tone! Precision, power, and purpose — it’s all unfolding. Keep your fire lit.",
        "20%": "Strength is in your hands. Every strict curl, every sharp breath is a declaration: you're becoming elite.",
        "30%": "Form is your foundation, discipline your fuel. You're locking in the blueprint of a champion.",
        "40%": "Muscle is earned, not given. Elbows tight, shoulders still — you’re building something unstoppable.",
        "50%": "Biceps burning, mind focused — you're sculpting strength rep by rep. 50% done, 100% determined.",
        "60%": "Mastery lives in details: tempo, tension, breath. You're not just working out — you're engineering greatness.",
        "70%": "Feel the fibers fire! Every squeeze, every stretch is another step toward peak performance.",
        "80%": "You're not curling weights — you're forging power. Precision meets perseverance — you own this grind.",
        "90%": "Leave nothing in the tank. Pure form, full force. This is where champions finish strong.",
        "100%": "Another mission crushed! Strength, skill, resilience — you’ve built it, earned it, and it’s only the beginning.",
    }

    message =  motivations[percent_complete]

    client.chat_postMessage(
        channel=channel_id,
        text=message
    )

# Flask setup
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/ping", methods=["GET"])
def ping_events():
    return "Pong", 200

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Run the server
if __name__ == "__main__":
    flask_app.run(port=3000)