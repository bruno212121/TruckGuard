from .. import mailsender
from flask import current_app, render_template
from flask_mail import Message
from smtplib import SMTPException 

def send_email(to, subject, template, **kwargs):
    #config mail
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    
    try:
        #send email
        #msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)

        result = mailsender.send(msg)
    except SMTPException as e:
        print(str(e))
        return "Error sending email", 500
    return "Email sent", 200