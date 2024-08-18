# SimpleTM
Flask &amp; Sqlite3 based TM Server

## Important Note
This project is no longer maintained!

There is a complete new version of SimpleTM called SimpleTM2, which is free but **not open sourced**. SimpleTM2 is now the version running on [simpletm.jscrosoft.com](https://simpletm.jscrosoft.com).

SimpleTM will not be maintained afterwards, but its existing API is still be implemented by SimpleTM2. So it is safe to use SimpleTM2 as a replacement of SimpleTM. 

If you are interest in maintaining this open sourced version of SimpleTM, please contact me.

#### why SimpleTM2 is not open sourced
I am afraid some corporations/groups who do translation work as a business will use my code for profit (as the code quality of SimpleTM2 is already close to business level). 

## run
```
pip install -r requirements.txt
[PROTOCAL=<http/https>] [BASE_URL=<ip/dns>] flask run -h <ip> -p <port>
```
[] means optional

## TODO
- User can change other user's permission on the project that has admin permission,
but an admin cannot change another admin's permission.

- Admin can delete game
