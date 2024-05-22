from pyboy import PyBoy
from openai import OpenAI
import threading
import time
import base64
import random

# globals
LAST_RESPONSE = "TITLE SCREEN | PREVGOAL | INPUTS | NEW GOAL"
GOAL = "PLAY POKEMON"

client = OpenAI(
    api_key="LOL",
)

def get_response():
    time.sleep(1)
    global LAST_RESPONSE
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
  messages=[
    {
      "role": "user",
      "temperature": 1,
      "content": [
        {"type": "text", 
          "text":
          "The image attached is an in-progress screenshot of pokemon blue." +
          "First, briefly describe what you see on the screen, including exits, doors, and paths, with positions relative to the player. Then, add a | symbol" +
          "Next, consider your goal: " + GOAL + " Print your goal and add a | symbol."
          "You need to choose input based on two factors - the screenshot attached and the goal." +
          "Referencing the position of items in screenshot and the goal, give up to three inputs to be executed, seperated by commas, choosing from UP LEFT DOWN RIGHT A B SELECT START."+
          "Imemdiately add another | symbol and then print the new, updated goal based on the screenshot." +
          "Also, Text boxes can be advanced by issuing an A command. Do not use any newlines."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64," + encode_image("temp.png"),
          },
        },
      ],
    }
  ],
    max_tokens=200)
    LAST_RESPONSE = chat_completion.choices[0].message.content

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def runEmulator():
    global LAST_RESPONSE
    global GOAL
    last_press = []
    pyboy = PyBoy('pokemon.gb')
    pyboy.set_emulation_speed(0) # No speed limit

    send_next = 0
    while True:
        if(send_next > 0 and len(last_press) > 0):
            try:
                pyboy.button(last_press[0].strip())
            except:
                pass
        if(send_next == 0 and len(last_press) > 0):
            print("finished pressing " + last_press[0].strip())
            last_press.pop(0)
            send_next = 15
        pyboy.tick() # Process at least one frame to let the game register the input
        time.sleep(1/60)
        send_next -= 1
        if(LAST_RESPONSE != None):
        # check if GPT has reponse. trigger it.
            try:
                last_press = LAST_RESPONSE.split("|")[2].strip().split(",")
                GOAL = LAST_RESPONSE.split("|")[3]
            except:
                pass
            print("---")
            print(LAST_RESPONSE)
            LAST_RESPONSE = None
            send_next = 30 # wait 60 seconds.
        if(send_next == 0 and len(last_press) == 0):
            pyboy.screen.image.save("temp.png")
            x = threading.Thread(target=get_response)
            x.start()
                                 
runEmulator()