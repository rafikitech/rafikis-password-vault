# rafikis-password-vault

Rafiki's Password Vault

This simple password manager is used to store email and passwords within one location  and allow copy and pasting for convenience. The site requires 2 factor authentication with a user password and email confirmation code for every login attempt. 

To handle many web development headaches and security concerns, django was used. Django's cryptography and fernet modules ensure data is stored in database in encrpyted form and fetch for the authenticated user to be viewed in plaintext. Fernet uses 128-bit AES in CBC mode with PKCS#7 padding and uses a SHA-256 HMAC for authentication. This algorithm takes in the version number of fernet, timestamp, unique initialization vector, ciphertext, and HMAC to generate a fernet token. This secure token can then be transmitted accross networks/applications and can be decrpyed with the same key and initialization vector. This combination provides reliable security of confidentiality, integrity, and availability.

Django's mechanize and favicon  modules are used to scrape url's of added sites to find the Title name and Site Icon to display for user. 

This is a "learning to web develop" project, starting with learning how to put simple text on a big screen. There are design and styling problems that would be better to be fixed with more time, such as the header shadow box disappearing after closing modules without sending a request. 

FEATURES TO ADD IN FUTURE:
-Edit credentials button under Actions tab => similar methodology as used for add credentials model but would need to check and verify correct account and site is being updated. More time needed to troubleshoot.

-Passwords should be in an 'input type=password' in order to hide password details. User is then not able to interact with (copy to clipboard) while type is password. 
    Possible solutions:
    -Add copy to clipboard button: execCommand featured deprecated and difficulties using new navigator.clipboard API from mozilla developers. Adding to clipboard seen as inherently insecure. Multiple methods attempted but none work yet.
    -Add toggle visibility button: have javascript listen for toggle button that would switch password box from  type=password to type=text to allow interaction. Also references to possible vulnerabilites by javascript handling the text box.

-Forgot Password page/function: If user is registered, have a forgot password option to send password reset code or module link to handle changing user password in database. More time required.

-Cleaner styling and design choices

-Issues with decoupling secret keys and deploying to hosting server. Attempts broke running code and troubleshot back to a running virtual environment server. Will keep this project in development phase to continue working on above features/issues.
