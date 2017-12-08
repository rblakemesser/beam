# beam


Beam is an LED matrix controller with a web API.

On the back-end, I have a main loop that acts as a router for bibliopixel animations. The bibliopixel animation router operates in the main thread, while a flask API runs in a secondary thread on the same process. The front-end is written in react and hosted here: https://github.com/rblakemesser/beamdaddy

A version of this project won the "Mad Scientist" award at a Cratejoy Hackathon event in July 2017.

