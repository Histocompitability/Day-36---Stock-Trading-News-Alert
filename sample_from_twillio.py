import os
from twilio.rest import Client

for i in range (10):
    os.environ["ACCOUNT_SID"] = "AC81aad1bee85f1e88250f8504570cd0f6"
    os.environ["AUTH_TOKEN"] = "cf5b4c1dcbf9908f51c2b7f5292d99e7"
    client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"))

    message = client.messages \
        .create(
        body="А мене спамити спамити не переспамити)))",
        from_='+13185350660',
        to='+380971804834'
    )

    print(message.sid)