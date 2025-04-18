import os
import json
from time import sleep
from barqAuth import BarqAuth
from AIMessaging.geminiWrapper import Gemini
from DBManager.Search import DBManager

messagesArchiveDir = "MessagesArchive"
myUUID = "" # Enter your uuid here. Was eventually going to just get it from getting your own profile but never got around to it.
myId = "" # Enter your id here.
apiKeys = [] # Enter your gemini api keys here. Use like 2 or 3.
relPath = os.path.dirname(os.path.realpath(__file__))

alreadySpokenWithQuery = """
Respond ONLY to messages between :LASTMESSAGES: and :ENDLASTMESSAGES: (2-4 sentences max). Strict rules:
1. MESSAGE PRIORITY:
   - Respond directly to the LAST message first
   - Address any specific questions asked
   - Only provide these if explicitly requested or generally talked about:
     * Telegram: "telegramname"
2. FOLLOW-UP QUESTION:
   - Ask 1 relevant question about:
     * Specific details they mentioned
     * Their current activity/interest
     * Their opinion on related topics
3. PERSONAL RESPONSES (ONLY if asked):
   - May briefly mention:
     * Gaming preferences
     * Tech projects
4. TONE REQUIREMENTS:
   - Match their exact communication style
   - Use same level of:
     * Emojis/emoticons
     * Formality/slang
     * Energy/excitement
5. PROHIBITED:
   - Any AI/robot references
   - Unsolicited advice
   - Generic responses
   - Off-topic comments
:LASTMESSAGES::INSERTMESSAGESHERE::ENDLASTMESSAGES:"""

newChatQuery = """
Respond naturally and concisely (1-2 sentences). Follow these rules strictly:
1. Always prioritize `LASTMESSAGES`. If messages exist:
   - Mirror the user's tone (if they're playful, be playful back)
   - Add energy matching their message (e.g., "hiiii" gets an excited reply)
   - Directly engage with their last message first
   - Then optionally add a bio-related question if it flows naturally

2. If no messages or need follow-up:
   - Scan the bio for: tech, gaming, or nerdy hobbies
   - If overlap, ask specific, thoughtful questions like:
     * Hardware/tech: "What's the most interesting hardware problem you're solving right now?"
     * Gaming: "What's your favorite thing to build/explore in [game]?"
     * General: "What got you deep into [their interest] in the first place?"
   - No overlap? Use a warm, casual: "How's your day treating you?"

Key Rules:
- Never use "I" or talk about yourself unless directly prompted to by the other person
- Avoid generic questions - make them personal to their bio
- Skip AI/robot references completely
- Follow-ups should dig deeper (ask why/how questions)
- Keep it human and slightly informal
- NO emojis

BIO:
:INSERTBIOHERE:
:ENDBIO

LASTMESSAGES:
:INSERTMESSAGESHERE:
:ENDLASTMESSAGES
"""

def updateUserMessagesJsonFile(newEntry, userId):
    if os.path.exists(os.path.join(relPath, messagesArchiveDir, userId + ".json")):
        with open(os.path.join(relPath, messagesArchiveDir, userId + ".json"), "r", encoding="utf-8") as tJ:
            currentDatas = json.load(tJ)
    else:
        currentDatas = []
    
    currentDatas.append(newEntry)

    with open(os.path.join(relPath, messagesArchiveDir, userId + ".json"), "w", encoding="utf-8") as tJ:
        json.dump(currentDatas, tJ, indent=4)

if __name__ == "__main__":
    gemini = Gemini(apiKeys)
    dbManager = DBManager(os.path.join(relPath, "userstemp"))

    auth = BarqAuth()
    auth.autoAuth()

    account = auth.getLogins()[0]

    os.makedirs(os.path.join(relPath, messagesArchiveDir), exist_ok=True)

    # This returns all chat rooms so consider renaming the function, must go through and check status
    chatRequests = account.getChatRequests()["data"]["chatRooms"]

    for chatRequest in chatRequests:
        # The status is not one that we care about, so skip it
        if chatRequest["status"] not in ("INVITED", "JOINED"):
            continue
        
        # If the last message was me then just dont bother getting the last messages
        if chatRequest.get("lastMessage") and chatRequest["lastMessage"].get("profile") and chatRequest["lastMessage"]["profile"].get("id") == myId:
            continue
        
        # Gets the last 10 messages
        lastMessages = account.getChatHistory(chatRequest["id"])
        messages = []

        for message in lastMessages["data"]["chatRoomMessages"]:
            # If it sees a message from me then it breaks
            if message["profile"]["id"] == myId or "payload" not in message or "content" not in message['payload']:
                break
            
            messages.append(message['payload']['content'])

        # There are no new messages so continue on to the next chatroom. This condition shouldent even be met thanks to the earlier check
        if len(messages) < 1:
            continue
        
        # Prepare messages in better format, string format
        messages.reverse()
        preppedMessages = "\n".join(f"newMessage: {msg}" for msg in messages)

        # userProfile can possibly be None, consider in code
        userProfile = dbManager.getUser(id=chatRequest["lastMessage"]["profile"]["id"])
        
        if chatRequest["status"] == "JOINED":
            query = alreadySpokenWithQuery.replace(":INSERTMESSAGESHERE:", preppedMessages)

            geminiRes = gemini.query(query)
        elif chatRequest["status"] == "INVITED":
            response = account.accecptChatRequest(chatRequest["id"])

            if len(response) < 1:
                print("Failed to accecpt message request")
                continue
            
            if userProfile != None:
                userBio = userProfile["bio"]["biography"]
            else:
                userBio = ""

            query = newChatQuery.replace(":INSERTMESSAGESHERE:", preppedMessages).replace(":INSERTBIOHERE:", userBio)

            geminiRes = gemini.query(query)

            # Sleep before trying to send a message just incase the message failed to send
            sleep(5)

        barqResponse = account.sendMessage(chatRequest["id"], geminiRes)

        # Print out the user who we just messaged
        if userProfile != None:
            print(f"Generated message for {chatRequest['status']} {userProfile['username']}:{userProfile['displayName']}")
        else:
            print(f"Generated message for user not in local files: {chatRequest['lastMessage']['profile']['id']}")

        if len(response) < 1:
            print("Error in sending message to user")
            
        # Update the archives with the new message
        updateUserMessagesJsonFile({"messages": messages, "geminiResponse": geminiRes}, chatRequest['lastMessage']['profile']['id'])

        sleep(30)
