// Form
$(document).ready(function () {
    // advanced settings visibility
    $('#advanced-settings-button').bind('click', function () {
        $(this)[0].text = 'Advanced Settings';
        let newHeadline = document.createElement('div');
        newHeadline.style.fontSize = $(this)[0].style.fontSize;
        newHeadline.innerHTML = $(this)[0].innerHTML;
        $(this)[0].parentNode.replaceChild(newHeadline, $(this)[0]);
        $('.advanced-settings').each(function () {
            $(this)[0].style.display = 'block';
        })
    });

    let multipleLinkBool = $('#input-multiple-bool');

    // checkbox visibility
    function adjustAllInputVisibilities() {
        let inputPasswordText = $('#input-password-text')[0];
        let inputPasswordBoolChecked = $('#input-password-bool').checked;
        inputPasswordText.style.display = inputPasswordBoolChecked ? 'block' : 'none';
        inputPasswordText.disabled = !inputPasswordBoolChecked;

        let inputDurationDate = $('#input-duration-date')[0];
        let inputDurationDateBoolChecked = $('#input-duration-bool').checked;
        inputDurationDate.style.display = inputDurationDateBoolChecked ? 'block' : 'none';
        inputDurationDate.disabled = !inputDurationDateBoolChecked;

        let inputWishText = $('#input-wish-text')[0];
        let inputWishBoolChecked = $('#input-wish-bool').checked;
        inputWishText.style.display = inputWishBoolChecked ? 'block' : 'none';
        inputWishText.disabled = !inputWishBoolChecked;

        let inputLengthNumber = $('#input-length-number')[0];
        let inputLengthBoolChecked = $('#input-length-bool').checked;
        inputLengthNumber.style.display = inputLengthBoolChecked ? 'block' : 'none';
        inputLengthNumber.disabled= !inputLengthBoolChecked;

        let inputClickLimitNumber = $('#input-click-limit-number')[0];
        let inputClickLimitBoolChecked = $('#input-click-limit-bool').checked;
        inputClickLimitNumber.style.display = inputClickLimitBoolChecked ? 'block' : 'none';
        inputClickLimitNumber.disabled = !inputClickLimitBoolChecked;

        let inputLink = $('#input-link')[0];
        inputLink.style.display = multipleLinkBool.checked ? 'none' : 'block';
        $('#input-link-label')[0].style.display = multipleLinkBool.checked ? 'none' : 'block';
        inputLink.required = !multipleLinkBool.checked;
        let inputMultipleLink = $('#input-multiple-link')[0];
        inputMultipleLink.style.display = multipleLinkBool.checked ? 'block' : 'none';
        $('#input-multiple-link-label')[0].style.display = multipleLinkBool.checked ? 'block' : 'none';
        inputMultipleLink.required = multipleLinkBool.checked;
    }

    function adjustTextInputsVisibility() {
        let nextSibling = $(this)[0].nextElementSibling.nextElementSibling;
        nextSibling.style.display = $(this)[0].checked ? 'block' : 'none';
        nextSibling.disabled = !$(this)[0].checked;
    }

    function adjustMultipleLinkTextareaVisibility() {
        let inputLink = $('#input-link')[0];
        inputLink.style.display = multipleLinkBool[0].checked ? 'none' : 'block';
        inputLink.disabled = multipleLinkBool[0].checked;
        $('#input-link-label')[0].style.display = multipleLinkBool[0].checked ? 'none' : 'block';
        inputLink.required = !multipleLinkBool[0].checked;
        let inputMultipleLink = $('#input-multiple-link')[0];
        inputMultipleLink.style.display = multipleLinkBool[0].checked ? 'block' : 'none';
        inputMultipleLink.disabled = !multipleLinkBool[0].checked;
        $('#input-multiple-link-label')[0].style.display = multipleLinkBool[0].checked ? 'block' : 'none';
        inputMultipleLink.required = multipleLinkBool[0].checked;
    }

    $('#input-form')[0].addEventListener('reset', adjustAllInputVisibilities);
    const inputCheckboxes = $('#input-form input:checkbox:not(#input-multiple-bool)');
    inputCheckboxes.each(adjustTextInputsVisibility);
    inputCheckboxes.bind('click', adjustTextInputsVisibility);
    adjustMultipleLinkTextareaVisibility();
    multipleLinkBool.bind('click', adjustMultipleLinkTextareaVisibility);

    // shortened link button
    $('#copy-shortened-link-button').bind('click', function () {
        const shortenedLinkText = $('#shortened-link')[0].text;
        navigator.clipboard.writeText(shortenedLinkText);
        $(this)[0].text = "Link Copied";
    });
});
