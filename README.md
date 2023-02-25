# Cubelles Surf Bot
Telegram bot that predicts surf waves. You could find the public bot: [@cubesurf_bot](https://t.me/cubesurf_bot)

Commands:
- "/predict": Waves prediction for the next 4 days.

There is a rate limit, if request limit is exceded bot will be disabled. Contact [@davidciria](https://t.me/davidciria) if the bot is not working.

# Software Architecture
The bot is designed in two Amazon Web Services (AWS) Lambda Functions:
- **cubesurf_bot:** Lambda that creates the prediction messages and sends them to users/groups.
- **cubesurf_bot_responses:** Lambda that manages bot requests.

## APIs
- Waves: [https://www.puertos.es/](https://www.puertos.es/)
- Weather: [https://www.aemet.es/](https://www.aemet.es/)