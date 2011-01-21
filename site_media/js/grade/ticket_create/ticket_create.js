/*
    required: Big Integers
    http://www.leemon.com/crypto/BigInt.html 
*/

if (typeof Ticket == 'undefined')
    Ticket = new Object();﻿

Ticket.create = Object()
Ticket.create.init   = function()
{
    Ticket.create.t_array        = new Array();
    Ticket.create.m_array        = new Array();
    Ticket.create.unblindst_array = new Array();
    Ticket.create.unblindt_array = new Array();
    Ticket.create.k_array        = new Array();
    Ticket.create.RAND_BITS      = 512;
    $("#connection_choice_button").click(Ticket.create.step1);
    
}


Ticket.create.step1  = function()
{
    dataString = $("#connection_choice").serialize()
    $.ajax({
        type: "POST",
        url: "grade/ticket/ajax_ticets1",
        async: false,
        dataType: 'json',
        data: dataString,
        success: Ticket.create.step2
    });
}

Ticket.create.step2  = function(keys)
{
    $.each(keys, Ticket.create.t_generator);
    var hidden = document.createElement('input')
    hidden.name = 'ts'
    hidden.type = 'hidden'
    hidden.value = JSON.stringify(Ticket.create.t_array)
    $("#connection_choice").append(hidden);
    dataString = $("#connection_choice").serialize()
    $.ajax({
        type: "POST",
        url: "grade/ticket_create/ajax_ticets2",
        async: false,
        dataType: 'json',
        data: dataString,
        success: Ticket.create.step3
    });
}

Ticket.create.step3  = function(unblinds)
{
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
}

Ticket.create.unblinds_generator = function(index, unblind)
{
    if (unblind[1] == "Nie masz uprawnień do tej ankiety")
    {
        Ticket.create.unblindst_array.push(unblind[1])
    }
    else if (unblind[1] == "Bilet już pobrano")
    {
        Ticket.create.unblindst_array.push(unblind[1])
    }
    else
    { 
        var st  = str2bigInt(unblind[1][0], 10, 10)
        var n   = str2bigInt(unblind[1][1], 10, 10)
        var e   = str2bigInt(unblind[1][2], 10, 10)
        var rk  = inverseMod( Ticket.create.k_array[index], n )
        Ticket.create.unblindst_array.push( bigInt2str(multMod(mod(st, n), mod(rk, n), n ), 10) )
        Ticket.create.unblindt_array.push( bigInt2str (powMod(Ticket.create.m_array[index], e , n)  ), 10)
    }   
}

Ticket.create.t_generator = function(key, val)
{
    var m = randBigInt( 512, 0 )
    $.each(val, function(nr, g)
    {
        var n = str2bigInt(g[0], 10, 10)
        var e = str2bigInt(g[1], 10, 10)
        var bits = bitSize(n)
        
        do
        {
            var k = randBigInt(bits, 0)
        } while((greater(k, n) || greater(int2bigInt(2, 2, 1), k)) && ! equalsInt(GCD(k, n), 1)) ;

        Ticket.create.k_array.push(k);
        Ticket.create.m_array.push(m);
        var a = mod(m, n)
        var b = powMod( k, e, n )
        var t = multMod( a, b, n )
            
        Ticket.create.t_array.push(bigInt2str(t, 10))
    });

}

$(Ticket.create.init)
