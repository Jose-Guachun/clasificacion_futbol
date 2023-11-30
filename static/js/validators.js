$(function () {
    var input = document.getElementsByClassName("myInput").value;
    //Solo números
    $(".soloNumeros").keypress(function (event) {
        var input = event.target;
        var tecla = event.which || event.keyCode;

        if (tecla >= 48 && tecla <= 57) {
            // Permitir dígitos numéricos
            return true;
        } else {
            // Evitar que se ingresen otros caracteres
            event.preventDefault();
            return false;
        }
    })
    //Solo letras sin ningun espacio ni caracteres especiales
    $(".soloLetras").keypress(function (event) {
        var input = event.target;
        var tecla = event.which || event.keyCode;

        if ((tecla >= 65 && tecla <= 90) || (tecla >= 97 && tecla <= 122)) {
            // Permitir letras mayúsculas y minúsculas
            return true;
        } else {
            // Evitar que se ingresen otros caracteres
            event.preventDefault();
            return false;
        }
    })
    //Solo letras con espacios y tildes
    $(".soloLetrasET").keypress(function (event) {
        var input = event.target;
        var tecla = event.which || event.keyCode;
        var caracter = String.fromCharCode(tecla);

        if (/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$/.test(caracter)) {
            // Permitir letras, espacios y tildes
            return true;
        } else {
            // Evitar que se ingresen otros caracteres
            event.preventDefault();
            return false;
        }
    })
})

//Validación de cédula ecuatoriana
function validarCedula(cedula) {
    if (typeof (cedula) == 'string' && cedula.length == 10 && /^\d+$/.test(cedula)) {
        var digitos = cedula.split('').map(Number);
        var codigo_provincia = digitos[0] * 10 + digitos[1];
        if (codigo_provincia >= 1 && (codigo_provincia <= 24 || codigo_provincia == 30)) {
            var digito_verificador = digitos.pop();
            var digito_calculado = digitos.reduce(
                function (valorPrevio, valorActual, indice) {
                    return valorPrevio - (valorActual * (2 - indice % 2)) % 9 - (valorActual == 9) * 9;
                }, 1000) % 10;
            return digito_calculado === digito_verificador;
        }
    }
    return false;
}

//Solo números
function soloNumeros(event) {
    var input = event.target;
    var tecla = event.which || event.keyCode;

    if (tecla >= 48 && tecla <= 57) {
        // Permitir dígitos numéricos
        return true;
    } else {
        // Evitar que se ingresen otros caracteres
        event.preventDefault();
        return false;
    }
}

//Solo letras sin ningún espacio ni caracteres especiales
function soloLetras(event) {
    var input = event.target;
    var tecla = event.which || event.keyCode;
    if ((tecla >= 65 && tecla <= 90) || (tecla >= 97 && tecla <= 122)) {
        // Permitir letras mayúsculas y minúsculas
        return true;
    } else {
        // Evitar que se ingresen otros caracteres
        event.preventDefault();
        return false;
    }
}

//Solo letras con espacios y tildes
function soloLetrasET(event) {
    var input = event.target;
    var tecla = event.which || event.keyCode;
    var caracter = String.fromCharCode(tecla);

    if (/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$/.test(caracter)) {
        // Permitir letras, espacios y tildes
        return true;
    } else {
        // Evitar que se ingresen otros caracteres
        event.preventDefault();
        return false;
    }
}