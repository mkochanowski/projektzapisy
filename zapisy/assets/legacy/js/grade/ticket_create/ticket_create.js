/*
 required: Big Integers
 http://www.leemon.com/crypto/BigInt.html
 */

if (typeof Ticket != 'undefined') {
} else {
    var Ticket = new Object();
}
Ticket.create = Object();
Ticket.create.init = function () {
    $("#progressbar").progressbar({ value:0 });
    Ticket.create.t_array = new Array();
    Ticket.create.m_array = new Array();
    Ticket.create.unblindst_array = new Array();
    Ticket.create.unblindt_array = new Array();
    Ticket.create.k_array = new Array();
    Ticket.create.RAND_BITS = 512;
    Ticket.create.used = false;

    $("#connection_choice_button").click(function (event) {
        event.preventDefault();
        if (Ticket.create.used) {
            return false;
        }
        Ticket.create.used = true;

        Ticket.create.step1();
    })
}

// Request public keys from the server
Ticket.create.step1 = function () {
    dataString = $("#connection_choice").serialize()
    $("#progressbar").progressbar("option", "value", 10);
    $.ajax({
        type:"POST",
        url:"/grade/ticket/ajax_tickets1",
        dataType:'json',
        data:dataString,
        success:Ticket.create.step2
    });
    return false;
}

// Once we have the public keys, use them to generate
// tickets, then send them to the server for signing
Ticket.create.step2 = function (keys) {
    $("#progressbar").progressbar("option", "value", 30);
    $.each(keys, Ticket.create.t_generator);
    var hidden = document.createElement('input')
    hidden.name = 'ts'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.t_array)
    $("#connection_choice").append(hidden);
    dataString = $("#connection_choice").serialize()
    $.ajax({
        type:"POST",
        url:"/grade/ticket/ajax_tickets2",
        dataType:'json',
        data:dataString,
        success:Ticket.create.step3
    });
}

// The server signed our generated tickets and sent
// them to us; Now we unblind the signed ticket by
// multiplying by inverse of r, and then send both
// ticket and its signature to the server to do
// rendering for us(this should be done client side)

Ticket.create.step3 = function (unblinds) {
    $("#progressbar").progressbar("option", "value", 70);
    $.each(unblinds, Ticket.create.unblinds_generator);

    var hidden = document.createElement('input')
    hidden.name = 'unblindst'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.unblindst_array)
    $("#connection_choice").append(hidden);
    var hidden = document.createElement('input')
    hidden.name = 'unblindt'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.unblindt_array)
    $("#connection_choice").append(hidden);
    $("#progressbar").progressbar("option", "value", 100);
    $('#connection_choice').submit();
}

Ticket.create.unblinds_generator = function (index, unblind) {
    if (unblind[1] == "Nie jesteś przypisany do tej ankiety") {
        Ticket.create.unblindst_array.push(unblind[1])
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
    else if (unblind[1] == "Bilet już pobrano") {
        Ticket.create.unblindst_array.push(unblind[1])
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
    else {
        var ticketSignature = unblind[1][0];

        var st = str2bigInt(ticketSignature, 10, 10)
        var n = str2bigInt(unblind[1][1], 10, 10)
        var e = str2bigInt(unblind[1][2], 10, 10)
        var rk = inverseMod(Ticket.create.k_array[index], n)
        Ticket.create.unblindst_array.push(bigInt2str(multMod(st, rk, n), 10))
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10))
    }
}

// This is where core of our crypto happens
// m and k are generated randomly with exactly same bit length as n,
// then the ticket is computed as SHA256(m) * k^e mod n
// SHA256(m) means that we convert int m to string with base 10,
// compute SHA256 of it, and then convert it back to int
Ticket.create.t_generator = function (key, val) {
    $.each(val, function (nr, g) {
        var n = str2bigInt(g[0], 10, 10);
        var e = str2bigInt(g[1], 10, 10);
        var bits = bitSize(n);
        do
        {
            var m = randBigInt(bits, 1);
            var k = randBigInt(bits, 1);
        } while ( greater(k, n) || greater(m, n) || !equalsInt(GCD(k, n), 1) );

        Ticket.create.k_array.push(k);
        Ticket.create.m_array.push(m);
        var m_sha256 = str2bigInt(forge_sha256(bigInt2str(m, 10)), 16);
        var k_pow_e = powMod(k, e, n);
        var t = multMod(m_sha256, k_pow_e, n);

        Ticket.create.t_array.push(bigInt2str(t, 10))
    });

}

$(Ticket.create.init)
