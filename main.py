import os
import roslibpy
import roslibpy.actionlib
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_gpt_response(question):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a scavenger hunt robot."},
            {"role": "user", "content": question}
        ]
    )
    return completion.choices[0].message

def go_to_pos(target, action_client):
    global move_goal
    print("Going to position", target)
    message = {
        "target_pose": {
            "header": {"frame_id": "map"},
            "pose": {
                "position": {"x": target[0], "y": target[1], "z": 0.0},
                "orientation": {"x": 0.0, "y": 0.0, "z": target[2], "w": target[3]},
            },
        }
    }
    move_goal = roslibpy.actionlib.Goal(action_client, message)
    move_goal.send()

def main():
    # Define the landmark coordinates dictionary
    landmark_coordinates = {
        "Chair": (0.303, 1.644, -0.233, 0.973),
        "Fridge": (-1.780, -5.208, -0.773, 0.635),
        "Circle": (-0.323, -14.675, 0.182, 0.983),
        "Couch": (-1.842, 6.651, 0.998, -0.057),
        "Microwave": (-0.828, -5.359, -0.780, 0.626),
        "TV": (0.150, 6.926, -0.094, 0.996),
        "Sink": (-0.233, -5.299, -0.058, 0.856),
        "Whiteboard": (6.961, -11.716, -0.720, 0.694),
        "Door": (-3.3916, -4.66, 0.996, -0.085),
        "Fountain": (-14.024, -7.108, 0.007, 1.000),
        "Longhorn": (4.889, -1.310, -0.016, 1.000)
    }

    ros_client = roslibpy.Ros(host='localhost', port=9090)

    try:
        ros_client.run()
        print("Connected to ROS successfully!")
    except roslibpy.RosTimeoutError as e:
        print("Failed to connect to ROS:", e)
        ros_client.run()

    action_client = roslibpy.actionlib.ActionClient(
        ros_client, "/move_base", "move_base_msgs/MoveBaseAction"
    )

    while True:
        # Ask user to input a question
        question = input("Ask a question: ")
        
        # Get response from ChatGPT
        response = get_gpt_response(question)
        print(response.content)

        # Check if any landmark is mentioned in the response
        for landmark, coords in landmark_coordinates.items():
            if landmark in response.content:
                go_to_pos(coords, action_client)
                break
        else:
            print("No landmark mentioned in the response.")

if __name__ == "__main__":
    main()
