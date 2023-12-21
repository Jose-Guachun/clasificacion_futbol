from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string

def send_email(titulo, cuerpo, email, data, template, qr_url='', lector_qr=''):
    context={'qr_url': qr_url,'data':data, 'lector_qr': lector_qr}

    # template=get_template('correo.html')
    # content=template.render(context)
    content = render_to_string(template, context)
    email=EmailMultiAlternatives(
        titulo,
        cuerpo,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    return HttpResponse('Correo enviado exitosamente')