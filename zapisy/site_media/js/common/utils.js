/**
 * @description determine if an array contains one or more items from another array.
 * @param {array} haystack the array to search.
 * @param {array} arr the array providing items to check for in the haystack.
 * @return {boolean} true|false if haystack contains at least one item from arr.
 */
function findOne(haystack, arr)
{
    return arr.some(function (v) {
        return haystack.indexOf(v) >= 0;
    });
}; 

function stackTrace() {
    var err = new Error();
    return err.stack;
}
