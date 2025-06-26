# F1 Stat in Telegram bot
**A little preface:** This project inherits from my previous idea of a summarized F1 statistic in a [Tableau dashboard](https://public.tableau.com/app/profile/dmytro.nesterenko5916/viz/F1analyticaldashboards/Intro).

This MVP of the F1 Analytical Bot is designed to provide enthusiasts with data-driven insights into the world of Formula 1. It streamlines complex F1 statistics into an easily digestible format, accessible with a Telegram interface.
--
The project is structured into three interconnected core components:
**ETL process:** this foundational component is responsible for the systematic acquisition, preparation, and DB storage (PostgreSQL) of F1 data.
**Analytical research:** This is where the raw F1 data is transformed into actionable insights.
**Telegram bot:** This component serves as the user-facing interface, allowing interaction with the F1 analytical part and data.
The project's core components are now designed to operate independently. The analytical module functions autonomously, leveraging a CSV data lake that is populated by the ETL (Extract, Transform, Load) process. Similarly, the ETL process can be executed independently of the Telegram bot. The Telegram bot itself incorporates several analytical functions, which were developed and refined during the dedicated analytical research phase of the project. Our immediate goal is to integrate the ETL process directly with the Telegram bot interface. This integration will allow administrators to gather and import new data directly into the database storage via the bot, and offer users a comprehensive suite of analytical reports directly through the bot's interface.
