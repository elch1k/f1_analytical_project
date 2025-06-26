# F1 Stat in Telegram bot
**A little preface:** This project inherits from my previous idea of a summarized F1 statistic in a [Tableau dashboard](https://public.tableau.com/app/profile/dmytro.nesterenko5916/viz/F1analyticaldashboards/Intro).

This MVP of the F1 Analytical Bot is designed to provide enthusiasts with data-driven insights into the world of Formula 1. It streamlines complex F1 statistics into an easily digestible format, accessible with a Telegram interface.

The project is structured into three interconnected core components:
--
**ETL process:** this foundational component is responsible for the systematic acquisition, preparation, and DB storage (PostgreSQL) of F1 data.  
**Analytical research:** This is where the raw F1 data is transformed into actionable insights.  
**Telegram bot:** This component serves as the user-facing interface, allowing interaction with the F1 analytical part and data (bot [url](https://t.me/f1analitics_bot)).  

The project's core components are now designed to operate independently. The [analytical module](https://github.com/elch1k/f1_analytical_project/blob/main/analytical_part/f1_eda.ipynb) functions autonomously, leveraging a CSV data lake that is populated by the ETL process. Similarly, the [ETL process](https://github.com/elch1k/f1_analytical_project/tree/main/etl_process) only can be executed independently of the Telegram bot. You can run the ETL process by executing `main.py` from the etl_process directory. The [Telegram bot](https://github.com/elch1k/f1_analytical_project/tree/main/bot) itself incorporates several analytical functions, which were developed and refined during the dedicated analytical research phase of the project. Unfortunately, the bot is not yet deployed and can only be accessed by running it locally. But you can see a preview of how the bot works:

![gif_example](https://github.com/elch1k/f1_analytical_project/blob/main/gif/tg_bot_example.gif)

My future goals include integrating the ETL process directly with the Telegram bot interface, deploying the bot to a server for uninterrupted remote access, and expanding the variety of analytical reports available to users for greater flexibility.
