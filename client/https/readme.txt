In order to have the green lock with these self-signed certificate,
you have to import the Root Certificate Autohority in your browser.

For that go in your browser parameter and search for manage certificates : 
- Go in the autohorities tab and import txChatRCA.crt
- Go in your certificates tab and import txChatRCA.p12, there is no password

Now the lock should be green meaning that your certificates are valid