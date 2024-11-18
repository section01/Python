"use strict";

window.onload = () => {
    let date = new Date();
    let today = [];
    today.push(`00${date.getFullYear()}`.slice(-4));
    today.push(`00${date.getMonth() + 1}`.slice(-2));
    document.getElementById("condition").value = today.join("-");
}