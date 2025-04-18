## What the hell is this?
- This is a wrapper for the barq api.
- It includes the wrapper, an account manager, gemini wrapper, json database wrapper, bert interactions, and more
## Why?
- Was for fun. was for practice. it got to be too large and i dont have time for this so im going to work on other stuff
- someone else might be able to use it so i decided to publish it
## You should know...
- i tried to include what would be useful
- there are python examples that show scraping data, interacting with people using gemini
- there is no support, warranty, or license
- barq uses graphql and you can get full profile information in batches of 100 (wtf??)
## The way i set this up
- scrape wiki for top 50 cities in the us in terms of population (geo cords included)
- pass geo cords to barq and scan each city for about 900+ profiles
- this yeilds a lot of profiles, some duplicates
- which is why i created clean json to clean the output
- output is cleaned :star_struck:
- feed each persons bio into bert to calculate similarity score
- if score bigger than 0.85 (85%) then like their profile (not included in examples, the liking profile part (i lost the python file))
- wait a few days
- run example.py and now gemini is responding to messages sent to you by fellow barqians
- get banned because you nammed two variables similarly and sent your gemini query to a user :cry:
