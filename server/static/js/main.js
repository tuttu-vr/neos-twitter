var copyToClipboard = function(element, idName) {
    var copyTarget = document.getElementById(idName);
    copyTarget.select();
    document.execCommand("Copy");
    element.textContent = "Copied!"
}
