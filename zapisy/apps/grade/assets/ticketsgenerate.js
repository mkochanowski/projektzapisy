import * as jquery from "jquery";
import "jquery-ui/ui/widgets/progressbar";
import { bigInt2str, bitSize, equalsInt,
    GCD, greater, inverseMod, multMod, powMod,
    randBigInt, str2bigInt } from "BigInt";
import * as sha256 from "node-forge/lib/sha256";

var $ = jquery;


/* ==================================================== */
/* ======== modified copy of hasWideChar.js =========== */
/* ==================================================== */

/* custom written function to determine if string is ASCII or UTF-8 */
var hasWideChar = function(str) {
    for( var i = 0; i < str.length; i++ ){
        if ( str.charCodeAt(i) >>> 8 ) return true;
    }
    return false;
};


/* ==================================================== */
/* ======= modified copy of wrapper.js ================ */
/* ==================================================== */

// custom written wrapper
// automatically sets encoding to ASCII or UTF-8
var forge_sha256 = function(str) {
    var o = sha256.create();
    o.update(
        str,
        hasWideChar(str)?'utf8':undefined);
    return o.digest().toHex();
};



var TicketCreate = function() {
    this.init = function () {
        $("#progressbar").progressbar({ value:0 });
        this.m_dict = {};
        this.unblindst_array = new Array();
        this.unblindt_array = new Array();
        this.k_dict = {};
        this.pubkeys_dict = {};
        this.poll_info_array = new Array();
        this.used = false;
        this.signing_requests = new Array();

        var that = this;
        $("#tickets_generate_button").click((event) => {
            event.preventDefault();
            if (that.used) {
                return false;
            }
            that.used = true;

            that.step1();
        });
    };

    this.unblinds_generator = (that => ((_index, signing_request_response) => {
        var signature = str2bigInt(signing_request_response.signature, 10);
        var pubkey = that.pubkeys_dict[signing_request_response.id];
        var n = pubkey.n;
        var k_inverse = inverseMod(that.k_dict[signing_request_response.id], n);
        that.unblindst_array.push(bigInt2str(multMod(signature, k_inverse, n), 10));
        that.unblindt_array.push(bigInt2str(that.m_dict[signing_request_response.id], 10));
    }))(this);

    // This is where core of our crypto happens
    // m and k are generated randomly with exactly same bit length as n,
    // then the ticket is computed as SHA256(m) * k^e mod n
    // SHA256(m) means that we convert int m to string with base 10,
    // compute SHA256 of it, and then convert it back to int
    this.tickets_generator = (that => ((_index, poll_data) => {
        var n = str2bigInt(poll_data.key.n, 10, 10);
        var e = str2bigInt(poll_data.key.e, 10, 10);
        that.pubkeys_dict[poll_data.poll_info.id] = {
            n: n,
            e: e
        };

        that.poll_info_array.push(poll_data.poll_info);

        var bits = bitSize(n);
        do
        {
            var m = randBigInt(bits, 1);
            var k = randBigInt(bits, 1);
        } while ( greater(k, n) || greater(m, n) || !equalsInt(GCD(k, n), 1) );

        that.k_dict[poll_data.poll_info.id] = k;
        that.m_dict[poll_data.poll_info.id] = m;
        var m_sha256 = str2bigInt(forge_sha256(bigInt2str(m, 10)), 16);
        var k_pow_e = powMod(k, e, n);
        var t = multMod(m_sha256, k_pow_e, n);

        that.signing_requests.push({
            id: poll_data.poll_info.id,
            ticket: bigInt2str(t, 10)
        });
    }))(this);

    this.to_plaintext = function() {
        var res = '';
        var that = this;
        $.each(this.unblindt_array, function(index, ticket) {
            var poll_info = that.poll_info_array[index];
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
            res += that.unblindst_array[index] + ' &#10;';
            res += '-'.repeat(34) + ' &#10;';
        });
        return res;
    };


    // Request public keys and poll info from the server
    this.step1 = function () {
        $("#progressbar").progressbar("option", "value", 10);
        $.ajax({
            type: "POST",
            url: "/grade/ticket/ajax_get_keys",
            cache: false,
            processData: false,
            contentType: false,
            data: new FormData(document.getElementById("tickets_generate")),
            success: this.step2
        });
       return false;
    };

    // Once we have the public keys, use them to generate
    // tickets, then send them to the server for signing
    this.step2 = (that => (data => {
        $("#progressbar").progressbar("option", "value", 30);
        $.each(data['poll_data'], that.tickets_generator);

        let signing_requests = JSON.stringify({
            signing_requests: that.signing_requests
        });
        $.ajax({
            type: "POST",
            url: "/grade/ticket/ajax_sign_tickets",
            dataType: 'json',
            headers: {'X-Csrftoken': document.cookie.match(
                new RegExp('(^| )csrftoken=([^;]+)'))[2]},
            data: signing_requests,
            success: that.step3,
        });
    }))(this);

    // The server signed our generated tickets and sent
    // them to us; Now we unblind the signed ticket by
    // multiplying by inverse of r, and then send both
    // ticket and its signature to the server to do
    // rendering for us(this should be done client side)

    this.step3 = (that => ((signing_request_responses) => {
        $("#progressbar").progressbar("option", "value", 70);
        $.each(signing_request_responses, that.unblinds_generator);

        $('#pregen').css('display', 'none');
        $('#postgen').css('display', '');
        $('#keys')[0].innerHTML = that.to_plaintext();
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
    }))(this);
};


$(document).ready(() => {
    if (typeof Ticket != 'undefined') {
    } else {
        var Ticket = new Object();
    }

    Ticket.create = new TicketCreate();
    Ticket.create.init();
});
