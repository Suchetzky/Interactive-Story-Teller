import time
import openai
from PIL import Image
import urllib.request
from openai import OpenAI
from io import BytesIO

print(
    "Embark on an epic journey as a Pokémon trainer in our game.\n"
    "Capture your first Pokémon, and face the ultimate\n"
    "challenge – a Squadron pokemon battle.\n")



client = OpenAI(
    api_key=open("API_KEY", "r").read(),)


assistant = client.beta.assistants.create(
    name="Pokemon story teller",
    instructions="1. you a story/situation teller that helps a player in a "
                 "pokemon game to continue his journey."
                 "2. the player starts in israeli Air force base, "
                 "small base with only 2 "
                 "buildings, one is a f35 squadron and one is the Shekem,"
                 "where ypu can find only food and drinks. there is"
                 "also a grass."
                 "3. the player can move in 4 directions"
                 "4. the player can catch 1 pokemon from generation 1"
                 "5. the player can battle only the pokemon Squadron leader"
                 "6. the player can encounter pokemons in the grass "
                 "7. keep the game going until the player reaches the "
                 "squadron and wins the Squadron leader with pokemon fight "
                 "and become the champion. he can fight only if he catches "
                 "a pokemon first"
                 "8. most answer with maximum of 10 words"
                 "9. push the player reach the end of the game, where he "
                 "catches a pokemon, go to the squadron,"
                 " fight the squadron leader, "
                 "wins a pokemon match and becomes the champion"
                 "he can enter the squadron only if he already caught a "
                 "pokemon"
                 "10. after the player become champion he cant do anything "
                 "else, the game is over"
                 "11. the squadron leader has 1 rare pokemon, an F35 plane "
                 "that has fire and air attacks",

    tools=[{"type": "code_interpreter"}],
    model="gpt-3.5-turbo-1106"
)

thread = client.beta.threads.create()

while True:
    uesr_sentance = input("young trainer, type your next move: ")

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            print("Prof.Oak" + ": " + messages.data[0].content[0].text.value)

            response = client.images.generate(
                model="dall-e-3",
                prompt="make a photo in the concept of "
                       "pokemon Fire Red game out of this sentence: " +
                       messages.data[0].content[0].text.value,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download the image from the URL using urllib
            with urllib.request.urlopen(image_url) as url:
                img_data = url.read()
                # Save the image data to a file
                filename = 'pokemon_image.jpg'
                with open(filename, 'wb') as f:
                    f.write(img_data)

            # Open and display the image using PIL
            img = Image.open(filename)
            img.show()

            # client.beta.assistants.delete(assistant.id)

            break
        else:
            print("Professor Oak thinks...")
            time.sleep(5)
