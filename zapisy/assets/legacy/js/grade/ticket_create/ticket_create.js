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
    Ticket.create.pubkeys_array = new Array();
    Ticket.create.poll_info_array = new Array();
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

// Request public keys and poll info from the server
Ticket.create.step1 = function () {
    $("#progressbar").progressbar("option", "value", 10);
    $.ajax({
        type:"POST",
        url:"/grade/ticket/ajax_tickets1",
        dataType:'json',
        success:Ticket.create.step2
    });
    return false;
}

// Once we have the public keys, use them to generate
// tickets, then send them to the server for signing
Ticket.create.step2 = function (data) {
    $("#progressbar").progressbar("option", "value", 30);
    $.each(data, Ticket.create.t_generator);
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

    $('#pregen').css('display', 'none');
    $('#postgen').css('display', '');
    $('#keys')[0].innerHTML = Ticket.create.to_plaintext();
    $('#copy-keys').click(() => {
        var el = document.getElementById("keys");
        var range = document.createRange();
        range.selectNodeContents(el);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand('copy');
        sel.removeAllRanges();
    });
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
        var st = str2bigInt(unblind.signature, 10);
        var pubkey = Ticket.create.pubkeys_array[index];
        var n = pubkey.n;
        var rk = inverseMod(Ticket.create.k_array[index], n);
        Ticket.create.unblindst_array.push(bigInt2str(multMod(st, rk, n), 10));
        Ticket.create.unblindt_array.push(bigInt2str(Ticket.create.m_array[index], 10));
    }
}

// This is where core of our crypto happens
// m and k are generated randomly with exactly same bit length as n,
// then the ticket is computed as SHA256(m) * k^e mod n
// SHA256(m) means that we convert int m to string with base 10,
// compute SHA256 of it, and then convert it back to int
Ticket.create.t_generator = function (key, poll_data) {
    var n = str2bigInt(poll_data.key.n, 10, 10);
    var e = str2bigInt(poll_data.key.e, 10, 10);
    Ticket.create.pubkeys_array.push({
        n: n,
        e: e
    });

    Ticket.create.poll_info_array.push(poll_data.poll_info);

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

}

Ticket.create.to_plaintext = function() {
    var res = '';
    $.each(Ticket.create.unblindt_array, function(index, ticket) {
        var poll_info = Ticket.create.poll_info_array[index];
        res += '[' + poll_info.title + '] ';
        if (!poll_info.course_name) {
            res += 'Ankieta ogólna &#10;';
        } else {
            res += poll_info.course_name + ' &#10;';
            res += poll_info.type + ': ';
            res += poll_info.teacher_name + ' &#10;';
        }
        res += 'id: ' + poll_info.id + ' &#10;';
        res += ticket + ' &#10;';
        res += Ticket.create.unblindst_array[index] + ' &#10;';
        res += '-'.repeat(34) + ' &#10;';
    });
    return res;
}

$(Ticket.create.init)
