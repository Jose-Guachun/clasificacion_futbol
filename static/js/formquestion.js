var method_req = "POST";
var _enc = $('*[data-datoseguro=true]').toArray();
var cargando = '<i class="fas fa-cog fa-spin" role="status" aria-hidden="true"></i>';
var error_btn2 = '<i class="fas fa-check-circle" role="status" aria-hidden="true"></i> Guardar';
var urlDefault = window.location.toString().split(window.location.host.toString())[1];
console.log(urlDefault)
var __enc = [];
for (var i = 0; i < _enc.length; i++) {
    __enc.push($(_enc[i]).attr('name'));
}
var inputsEncrypted = __enc.join('|');

if ($(".miEditor").length){
    // Selecciona el elemento del DOM que contiene el editor
    var miEditor = document.querySelector(".miEditor");
     // Instancia el editor Quill
    var quill = new Quill(miEditor, {
      modules: {
        toolbar: [
          [{header: [1, 2, false]}],
          [{font: []}],
          ["bold", "italic", "underline", "strike"],
          [{size: ["small", false, "large", "huge"]}],
          [{list: "ordered"}, {list: "bullet"}],
          [{color: []}, {background: []}, {align: []}],
          ["link", "image", "code-block", "video"]
        ]
      },
      theme: "snow"
    });
}

$(function () {
    $('form:not([method=GET], [method=get])').submit(function (event) {
        event.preventDefault();
        if (typeof addItemsFormData === 'function') {
            addItemsFormData();
        }
        const formData = $(this)
        const btnSubmit = $("#submit")
        const _url = formData.find('input[name=urlsubmit]').length ? formData.find('input[name=urlsubmit]').val() : urlDefault;
        const pk = formData.find('input[name=pk]').length ? parseInt(formData.find('input[name=pk]').val()) : 0;
        const action = formData.find('input[name=action]').length ? formData.find('input[name=action]').val() : false;
        console.log(_url)
        console.log(formData.attr('enctype'))
        var _form = new FormData(formData[0]);
        if (pk !== 0) {
            if (_form.has('pk')) {
                _form.set('pk', pk.toString());
            } else {
                _form.append('pk', pk.toString());
            }

        }
        if (action !== false) {
            if (_form.has('action')) {
                _form.set('action', action);
            } else {
                _form.append('action', action);
            }
        }
        const listInputsEnc = inputsEncrypted.split('|');
        for (var i = 0; i < listInputsEnc.length; i++) {
            if (_form.has(listInputsEnc[i])) {
                _form.set(listInputsEnc[i], doRSA(_form.get(listInputsEnc[i])));
            }
        }
        try {
            _form.append("lista_items1", JSON.stringify(lista_items1));
        } catch (err) {
            console.log(err.message);
        }
        $.ajax({
            type: method_req,
            url: _url,
            data: _form,
            dataType: 'json',
            enctype: formData.attr('enctype'),
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function (xhr, settings) {
                btnSubmit.html(cargando);
                btnSubmit.attr("disabled", true);
                bloqueointerface();
            }
        }).done(function (data) {
            // Manejar la respuesta del servidor
            $.unblockUI();
            if (data.result === true) {
                if (data.url_redirect) {
                    localStorage.clear();
                    localStorage.setItem('sessionid', data.sessionid);
                    window.name = data.sessionid;
                    location.href = data.url_redirect;
                } else {
                    $(".formularios").modal('hide');
                    if (data.msg_success) {
                        $.unblockUI();
                        Swal.fire(data.mensaje, '', 'success')
                    } else {
                        location.reload();
                    }
                }
            } else if (data.message_top) {
                $("#message_top").html(`${data.message_top}`);
                $("#text-alerta").removeClass('d-none')
            } else if (data.data_return) {
                alertaSuccess(data.mensaje)
                btnSubmit.html(error_btn2);
                btnSubmit.attr("disabled", false);
                // ActualizarTabla(data.data)
            } else {
                if (data.form) {
                    $(".errorField").empty()
                    data.form.forEach(function (val, indx) {
                        var keys = Object.keys(val);
                        keys.forEach(function (val1, indx1) {
                            $("#errorField" + val1).html(`${val[val1]}`);
                        });
                    });
                }
                alertaDanger(data.mensaje);
                btnSubmit.html(error_btn2);
                btnSubmit.attr("disabled", false);
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            // Manejar el error de la solicitud Ajax
            mensajeDanger('Conexión', 'Error de conexión')
            $.unblockUI();

        });
    })
})
