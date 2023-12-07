from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View

from users.models import Persona, Pais, Provincia


class ViewSet(View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action')
        context['persona'] = request.user.persona_set.get(status=True)
        context['viewactivo'] = 'usuarios'
        if action:
            if action == 'cargarprovincias':
                try:
                    id = int(request.GET['id'])
                    pais = Pais.objects.get(id=id)
                    resp = [{'value': qs.pk, 'text': f"{qs.nombre}"}
                            for qs in pais.provincias()]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

            if action == 'cargarciudades':
                try:
                    id = int(request.GET['id'])
                    provincia = Provincia.objects.get(id=id)
                    resp = [{'value': qs.pk, 'text': f"{qs.nombre}"}
                            for qs in provincia.ciudades()]
                    return JsonResponse({'result': True, 'data': resp})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': f'Error: {ex}'})

        return HttpResponseRedirect(request.path)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']

        return JsonResponse({"result": False, "mensaje": u"Solicitud Incorrecta."})