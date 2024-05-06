from .. import mailsender
from flask import current_app, render_template
from flask_mail import Message
from smtplib import SMTPException 

def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    #msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    try:
        mailsender.send(msg)
    except SMTPException as e:
        print(e)
        return "Error sending email", 500