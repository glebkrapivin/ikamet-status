# Ikamet-results

![alt](https://e-ikamet.goc.gov.tr/Styles/image/e-ikamet-logo-en.png)

A client for the Turkish website e-ikamet, that reduces the need to constantly check results for the residence permit application.

It is by no means a production code, just a small pet project to ease my life a for a bit. 
### Logic

1. Get residence application HTML, parse it to get server-side generated catpcha_id
2. Get captcha image
3. Solve captcha image locally or using a provider
4. Send a POST request to e-ikamet with solved captcha and application details, parse results
5. Send notification (in my example, to Telegram chat)

### TODOs:
- [ ] Better Error handling

### Env variables
#### **`env.list`**
```bash
CAPTCHA_TOKEN= # i'm using 2captcha solver
TELEGRAM_TOKEN= # to send notification

# application details
APPLICATION_ID= 
EMAIL=
PHONE_NUMBER=
PASSPORT_NUMBER=

LOG_LEVEL=
```

### Example usage (with docker)
```
docker build -t ikamet-results . 
docker run --env-file env.list ikamet-results
```
