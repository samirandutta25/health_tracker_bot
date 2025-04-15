from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from dotenv import load_dotenv
import json
import os

# Load environment variables
load_dotenv()

# Initialize the Bolt App
app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

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



def estimate_life_expectancy(gender, age, tobacco_use, ldl):
    if None in [gender, age, tobacco_use, ldl]:
        return ""  # If any input is missing, return empty string
    tobacco_use = tobacco_use.lower()
    gender = gender.lower()
    # Base life expectancy based on gender
    base_le = 69 if gender == "male" else 72 if gender == "female" else 70

    # LDL score
    if ldl < 100:
        ldl_score = 0
    elif ldl < 130:
        ldl_score = -1
    elif ldl < 160:
        ldl_score = -2
    else:
        ldl_score = -3

    # Tobacco score
    tobacco_score = -5 if tobacco_use == "yes" else 0

    # Age factor and penalty
    age_factor = max(0, age - 40)
    age_penalty = -1 * (age_factor ** 1.05 * 0.09)

    # Risk multiplier
    risk_multiplier = (1.1 if tobacco_use == "yes" else 1) + (0.05 if ldl > 160 else 0)

    # Adjusted life expectancy
    adjusted_le = (base_le + ldl_score + tobacco_score + age_penalty) * (1 - (risk_multiplier - 1))

    # Extract years and months from adjusted life expectancy
    years = int(adjusted_le)
    months = round((adjusted_le - years) * 12, 0)

    # Return the result message
    result = (
        f"Estimated Life Expectancy: {years} years and {months} months — "
        f"Every healthy choice empowers your future. "
        f"This isn't just a number—it's a nudge to live fully, love deeply, and thrive daily. "
        f"Shine on, because your journey matters. "
        f"— Source: Dr. V. Mohan, MD, FACP, FRCP | Padma Shri (2012) | Chairman, Diabetes Research Centre | "
        f"Member, WHO Expert Panel | Lead, ICMR-INDIAB 2025"
    )

    return result

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


# Flask setup
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/ping", methods=["GET"])
def slack_events():
    return "Pong", 200

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Run the server
if __name__ == "__main__":
    flask_app.run(port=3000)