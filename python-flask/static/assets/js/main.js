/*
	Massively by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

// Pagination Code
$(document).ready(function () {
    var currPageNumber = 1;
    var rowsShown = 5;
    var rowsTotal = $('#data tbody tr').length;
    if (rowsTotal <= rowsShown) {
        return;
    } else {
        $('#pagination-footer')[0].style.display = 'block';
    }
    var numPages = Math.ceil(rowsTotal / rowsShown);
    for (i = rowsTotal; i < numPages * rowsShown; i++) {
        $('#data tbody').append('<tr><td colspan="5"></td></tr>');
    }
    for (i = 0; i < numPages; i++) {
        var pageNum = i + 1;
        $('#pagination').append('<a class="page" rel="' + i + '">' + pageNum + '</a>');
    }
    $('#data tbody tr').hide();
    $('#data tbody tr').slice(0, rowsShown).show();
    $('#pagination a.page:first').addClass('active');
    $('#pagination a.page').bind('click', function () {
        if ($(this)[0].classList.contains('active')) {
            return;
        }
        currPageNumber = parseInt(this.textContent);
        $('#pagination a').removeClass('active');
        $(this).addClass('active');
        var currPage = $(this).attr('rel');
        var startItem = currPage * rowsShown;
        var endItem = startItem + rowsShown;
        $('#data tbody tr').css('opacity', '0.0').hide().slice(startItem, endItem).css('display', 'table-row').animate({opacity: 1}, 300);
        if (currPageNumber === 1) {
            $('#pagination a.previous')[0].style.opacity = "0";
        } else {
            $('#pagination a.previous')[0].style.opacity = "1";
        }
        if (currPageNumber === numPages) {
            $('#pagination a.next')[0].style.opacity = "0";
        } else {
            $('#pagination a.next')[0].style.opacity = "1";
        }
    });
    $('#pagination').append('<a class="next">Next</a>');
    $('#pagination a.previous').bind('click', function () {
        $('#pagination a.active')[0].previousElementSibling.click();
    });
    $('#pagination a.next').bind('click', function () {
        $('#pagination a.page.active')[0].nextElementSibling.click();
    });
});

// datetime input min value
$(document).ready(function () {
    function getFormattedCurrentDatetime() {
        const currentTime = new Date();
        currentTime.setTime(currentTime.getTime() - currentTime.getTimezoneOffset() * 60 * 1000);
        const date = currentTime.toJSON().split("T")[0];
        const hour = currentTime.toJSON().split("T")[1].split(":")[0];
        const minute = currentTime.toJSON().split("T")[1].split(":")[1];
        return date + "T" + hour + ":" + minute;
    }

    const dateTimeInput = $('[type="datetime-local"]');
    dateTimeInput.prop('min', getFormattedCurrentDatetime());
});

function getValueFromSerializedInput(serialized, name) {
    return serialized.filter(function (e) {
        return e.name === name;
    }).map(function (e) {
        if (e.value) {
            return e.value.split("\r\n");
        } else {
            return [null];
        }
    })[0];
}

// Shorten Link Form Submit
function shortenLinkFormSubmitted() {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            const response = JSON.parse(xhr.responseText);
            if (xhr.status === 201) {
                let shortenedUrl = (window.location.host.includes("develop") ? "dev.1wp.de/" : "1wp.de/") + response.path;
                let shortenedAHref = $('#shortened-link')[0];
                shortenedAHref.text = shortenedUrl;
                shortenedAHref.href = window.location.host.includes("5000") ? "//localhost:8080/" + response.path : "//" + shortenedUrl;

                $('#property-target-content')[0].innerHTML = response.urls;

                if (response.password === null) $('#property-password-row')[0].style.display = 'none';
                else $('#property-password-content')[0].innerHTML = response.password;

                if (response.date === null) $('#property-duration-row')[0].style.display = 'none';
                else $('#property-duration-content')[0].innerHTML = response.date;

                $('#property-masterKey-content')[0].innerHTML = response.masterKey;
                const masterKeyCookieKey = "storedMasterKeys";
                const masterKeyCookie = readCookie(masterKeyCookieKey);
                let storedMasterKeys = masterKeyCookie !== null ? JSON.parse(masterKeyCookie) : JSON.parse("{}");
                storedMasterKeys[response.path] = response.masterKey;
                document.cookie = masterKeyCookieKey + "=" + JSON.stringify(storedMasterKeys) + ";expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/";

                $('#input-form')[0].style.display = 'none';
                $('#shortened-link-container')[0].style.display = 'flex';
            }

            showToast(response.message, xhr.status);
        }
    };
    xhr.open("POST", "/api/url", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    const serialized = $("form").serializeArray();
    xhr.send(JSON.stringify({
        "urls": $('#input-multiple-bool')[0].checked ? getValueFromSerializedInput(serialized, "input-links") : getValueFromSerializedInput(serialized, "input-link"),
        "password": $('#input-password-bool')[0].checked ? getValueFromSerializedInput(serialized, "input-password-text")[0] : null,
        "endDurationDate": $('#input-duration-bool')[0].checked ? getValueFromSerializedInput(serialized, "input-duration-date")[0] : null,
        "wish": $('#input-wish-bool')[0].checked ? getValueFromSerializedInput(serialized, "input-wish-text")[0] : null,
        "length": $('#input-length-bool')[0].checked ? parseInt(getValueFromSerializedInput(serialized, "input-length-number")[0]) : null,
        "clickLimit": $('#input-click-limit-bool')[0].checked ? parseInt(getValueFromSerializedInput(serialized, "input-click-limit-number")[0]) : null
    }));
}

function loadQrCodeForShortenedUrl(shortenedUrl) {
    shortenedUrl = $('#shortened-link')[0].text;
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            const response = JSON.parse(xhr.responseText);
            if (xhr.status === 201) {
                let qrCodeImageElement = $('#qr-code-image')[0];
                // noinspection JSUnresolvedVariable
                qrCodeImageElement.src = "data:image/png;base64," + response.encodedImage;
                $('.qr-code-container').each(function () {
                    $(this)[0].style.display = "block";
                });
                // hide generating button
                $('.generate-qr-code-container')[0].style.display = "none";
                // enable Download button
                let qrCodeDownloadButton = $('#download-qr-code-button')[0];
                qrCodeDownloadButton.href = qrCodeImageElement.src;
                qrCodeDownloadButton.download = "qr.png";
            }

            showToast(response.message, xhr.status);
        }
    };
    xhr.open("POST", "/api/qr", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        "shortenedUrl": shortenedUrl
    }));
}

// Password Form Submit
function passwordFormSubmitted() {
    const urlPath = $('#password-url-path')[0].innerHTML;
    const password = $("form").serializeArray()[0].value;

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                let passwordCookieKey = "storedPasswords";
                const passwordCookie = readCookie(passwordCookieKey);
                let storedPasswords = passwordCookie !== null ? JSON.parse(passwordCookie) : JSON.parse("{}");
                storedPasswords[urlPath] = password;
                document.cookie = passwordCookieKey + "=" + JSON.stringify(storedPasswords) + ";expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/";
                window.location = urlPath;
            } else if (xhr.status === 401) {
                $("#input-password")[0].classList.add("input-wrong-password");
            }

            showToast(JSON.parse(xhr.responseText).message, xhr.status);
        }
    };
    xhr.open("POST", "/api/validate", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        "path": urlPath,
        "password": password
    }));
}

// MyLink Form Submit
function myLinkFormSubmitted() {
    // Store new link path and masterKey to Cookies
    let enteredPath = $("#input-myLink-path")[0].value;
    const enteredMasterKey = $("#input-myLink-masterKey")[0].value;

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                const masterKeyCookieKey = "storedMasterKeys";
                const masterKeyCookie = readCookie(masterKeyCookieKey);
                let storedMasterKeys = masterKeyCookie !== null ? JSON.parse(masterKeyCookie) : JSON.parse("{}");
                storedMasterKeys[enteredPath] = enteredMasterKey;
                document.cookie = masterKeyCookieKey + "=" + JSON.stringify(storedMasterKeys) + ";expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/";
                $("#input-myLink-path")[0].value = "";
                $("#input-myLink-masterKey")[0].value = "";
                location.reload();
            } else if (xhr.status === 401) {
                $("#input-myLink-path")[0].classList.add("input-wrong-password");
                $("#input-myLink-masterKey")[0].classList.add("input-wrong-password");
            }

            showToast(JSON.parse(xhr.responseText).message, xhr.status);
        }

    };
    xhr.open("POST", "/api/validate", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        "path": enteredPath,
        "masterKey": enteredMasterKey
    }));
}

function showToast(message, status) {
    new Notify({
        type: 3,
        title: ((status >= 200 && status <= 299) ? 'Success' : 'Error') + ' (' + status + ')',
        text: message,
        status: (status >= 200 && status <= 299) ? 'success' : 'error',
        autoclose: true,
        autotimeout: 5000
    });
}

function editLinkFormSubmitted() {
    const serialized = $("form").serializeArray();
    let oldPath = $('#input-edit-path')[0].placeholder;
    let newPath = getValueFromSerializedInput(serialized, "input-edit-path")[0];

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200 && oldPath !== newPath) {
                const masterKeyCookieKey = "storedMasterKeys";
                const masterKeyCookie = readCookie(masterKeyCookieKey);
                let storedMasterKeys = masterKeyCookie !== null ? JSON.parse(masterKeyCookie) : JSON.parse("{}");
                storedMasterKeys[newPath] = storedMasterKeys[oldPath];
                delete storedMasterKeys[oldPath];
                document.cookie = masterKeyCookieKey + "=" + JSON.stringify(storedMasterKeys) + ";expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/";
                $('#input-edit-path')[0].placeholder = newPath;
            }

            showToast(JSON.parse(xhr.responseText).message, xhr.status);
        }
    };
    xhr.open("PUT", "/api/url", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        "path": oldPath,
        "newPath": newPath,
        "passwordPlaceholder": $('#input-edit-password')[0].placeholder,
        "clickLimit": getValueFromSerializedInput(serialized, "input-edit-click-limit"),
        "password": getValueFromSerializedInput(serialized, "input-edit-password"),
        "urls": getValueFromSerializedInput(serialized, "input-edit-target"),
        "endDurationDate": getValueFromSerializedInput(serialized, "input-edit-date"),
        "masterKey": JSON.parse(readCookie("storedMasterKeys"))[oldPath]
    }));
}

function deletePressed(link) {
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: 'button primary',
            cancelButton: 'button'
        },
        buttonsStyling: false
    });

    swalWithBootstrapButtons.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!'
    }).then((result) => {
        if (result.isConfirmed) {
            deleteLink(link, swalWithBootstrapButtons);
        } else if (
            /* Read more about handling dismissals below */
            result.dismiss === Swal.DismissReason.cancel
        ) {
            swalWithBootstrapButtons.fire(
                'Cancelled',
                'Your imaginary file is safe.',
                'error'
            );
        }
    });
}

function deleteLink(link, swalWithBootstrapButtons) {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                const masterKeyCookieKey = "storedMasterKeys";
                const masterKeyCookie = readCookie(masterKeyCookieKey);
                let storedMasterKeys = masterKeyCookie !== null ? JSON.parse(masterKeyCookie) : JSON.parse("{}");
                delete storedMasterKeys[link];
                document.cookie = masterKeyCookieKey + "=" + JSON.stringify(storedMasterKeys) + ";expires=Fri, 31 Dec 9999 23:59:59 GMT;path=/";

                swalWithBootstrapButtons.fire(
                    'Deleted!',
                    'Your file has been deleted.',
                    'success'
                ).then((result) => {
                    if (result.isConfirmed) {
                        location.reload();
                    }

                });
            } else {
                showToast(JSON.parse(xhr.responseText).message, xhr.status);
            }
        }
    };
    xhr.open("DELETE", "/api/url", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({
        "path": link,
        "masterKey": JSON.parse(readCookie("storedMasterKeys"))[link]
    }));
}

// https://stackoverflow.com/a/1599291
function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// Wrong Password
function removeWrongPasswordClass() {
    let wrongPasswordInput = $('.input-wrong-password')[0];
    if (wrongPasswordInput !== undefined && wrongPasswordInput.classList.contains("input-wrong-password")) wrongPasswordInput.classList.remove("input-wrong-password");
}

// Clear input field
function passwordInputClicked(passwordInput) {
    if (passwordInput.value !== "") {
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
                confirmButton: 'button primary',
                cancelButton: 'button'
            },
            buttonsStyling: false
        });
        swalWithBootstrapButtons.fire({
            title: 'Changing old password?',
            text: "Saving the adaption will overwrite the old password.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, change it!',
            cancelButtonText: 'No, cancel!'
        }).then((result) => {
            if (result.isConfirmed) {
                passwordInput.onclick = null;
                passwordInput.placeholder = "";
                passwordInput.value = "";
            } else if (
                /* Read more about handling dismissals below */
                result.dismiss === Swal.DismissReason.cancel
            ) {
                passwordInput.disabled = true;
                swalWithBootstrapButtons.fire(
                    'Cancelled',
                    'The old password is locked.',
                    'error'
                );
            }
        });
    }
}

// Enable pattern validation for textarea inputs https://stackoverflow.com/a/28229685
$(document).ready(function () {
    var errorMessage = "Please match the requested format.";

    $(this).find("textarea").on("input change propertychange", function () {

        var pattern = $(this).attr("pattern");

        if (typeof pattern !== typeof undefined && pattern !== false) {
            var patternRegex = new RegExp("^" + pattern.replace(/^\^|\$$/g, '') + "$", "g");

            hasError = !$(this).val().match(patternRegex);

            if (typeof this.setCustomValidity === "function") {
                this.setCustomValidity(hasError ? errorMessage : "");
            } else {
                $(this).toggleClass("error", !!hasError);
                $(this).toggleClass("ok", !hasError);

                if (hasError) {
                    $(this).attr("title", errorMessage);
                } else {
                    $(this).removeAttr("title");
                }
            }
        }

    });
});

(function ($) {

    var $window = $(window),
        $body = $('body'),
        $wrapper = $('#wrapper'),
        $header = $('#header'),
        $nav = $('#nav'),
        $main = $('#main'),
        $navPanelToggle, $navPanel, $navPanelInner;

    // Breakpoints.
    breakpoints({
        default: ['1681px', null],
        xlarge: ['1281px', '1680px'],
        large: ['981px', '1280px'],
        medium: ['737px', '980px'],
        small: ['481px', '736px'],
        xsmall: ['361px', '480px'],
        xxsmall: [null, '360px']
    });

    /**
     * Applies parallax scrolling to an element's background image.
     * @return {jQuery} jQuery object.
     */
    $.fn._parallax = function (intensity) {

        var $window = $(window),
            $this = $(this);

        if (this.length == 0 || intensity === 0)
            return $this;

        if (this.length > 1) {

            for (var i = 0; i < this.length; i++)
                $(this[i])._parallax(intensity);

            return $this;

        }

        if (!intensity)
            intensity = 0.25;

        $this.each(function () {

            var $t = $(this),
                $bg = $('<div class="bg"></div>').appendTo($t),
                on, off;

            on = function () {

                $bg
                    .removeClass('fixed')
                    .css('transform', 'matrix(1,0,0,1,0,0)');

                $window
                    .on('scroll._parallax', function () {

                        var pos = parseInt($window.scrollTop()) - parseInt($t.position().top);

                        $bg.css('transform', 'matrix(1,0,0,1,0,' + (pos * intensity) + ')');

                    });

            };

            off = function () {

                $bg
                    .addClass('fixed')
                    .css('transform', 'none');

                $window
                    .off('scroll._parallax');

            };

            // Disable parallax on ..
            if (browser.name == 'ie'			// IE
                || browser.name == 'edge'			// Edge
                || window.devicePixelRatio > 1		// Retina/HiDPI (= poor performance)
                || browser.mobile)					// Mobile devices
                off();

            // Enable everywhere else.
            else {

                breakpoints.on('>large', on);
                breakpoints.on('<=large', off);

            }

        });

        $window
            .off('load._parallax resize._parallax')
            .on('load._parallax resize._parallax', function () {
                $window.trigger('scroll');
            });

        return $(this);

    };

    // Play initial animations on page load.
    $window.on('load', function () {
        window.setTimeout(function () {
            $body.removeClass('is-preload');
        }, 100);
    });

    // Scrolly.
    $('.scrolly').scrolly();

    // Background.
    $wrapper._parallax(0.925);

    // Nav Panel.

    // Toggle.
    $navPanelToggle = $(
        '<a href="#navPanel" id="navPanelToggle">Menu</a>'
    )
        .appendTo($wrapper);

    // Change toggle styling once we've scrolled past the header.
    $header.scrollex({
        bottom: '5vh',
        enter: function () {
            $navPanelToggle.removeClass('alt');
        },
        leave: function () {
            $navPanelToggle.addClass('alt');
        }
    });

    // Panel.
    $navPanel = $(
        '<div id="navPanel">' +
        '<nav>' +
        '</nav>' +
        '<a href="#navPanel" class="close"></a>' +
        '</div>'
    )
        .appendTo($body)
        .panel({
            delay: 500,
            hideOnClick: true,
            hideOnSwipe: true,
            resetScroll: true,
            resetForms: true,
            side: 'right',
            target: $body,
            visibleClass: 'is-navPanel-visible'
        });

    // Get inner.
    $navPanelInner = $navPanel.children('nav');

    // Move nav content on breakpoint change.
    var $navContent = $nav.children();

    breakpoints.on('>medium', function () {

        // NavPanel -> Nav.
        $navContent.appendTo($nav);

        // Flip icon classes.
        $nav.find('.icons, .icon')
            .removeClass('alt');

    });

    breakpoints.on('<=medium', function () {

        // Nav -> NavPanel.
        $navContent.appendTo($navPanelInner);

        // Flip icon classes.
        $navPanelInner.find('.icons, .icon')
            .addClass('alt');

    });

    // Hack: Disable transitions on WP.
    if (browser.os == 'wp'
        && browser.osVersion < 10)
        $navPanel
            .css('transition', 'none');

    // Intro.
    var $intro = $('#intro');

    if ($intro.length > 0) {

        // Hack: Fix flex min-height on IE.
        if (browser.name == 'ie') {
            $window.on('resize.ie-intro-fix', function () {

                var h = $intro.height();

                if (h > $window.height())
                    $intro.css('height', 'auto');
                else
                    $intro.css('height', h);

            }).trigger('resize.ie-intro-fix');
        }

        // Hide intro on scroll (> small).
        breakpoints.on('>small', function () {

            $main.unscrollex();

            $main.scrollex({
                mode: 'bottom',
                top: '25vh',
                bottom: '-50vh',
                enter: function () {
                    $intro.addClass('hidden');
                },
                leave: function () {
                    $intro.removeClass('hidden');
                }
            });

        });

        // Hide intro on scroll (<= small).
        breakpoints.on('<=small', function () {

            $main.unscrollex();

            $main.scrollex({
                mode: 'middle',
                top: '15vh',
                bottom: '-15vh',
                enter: function () {
                    $intro.addClass('hidden');
                },
                leave: function () {
                    $intro.removeClass('hidden');
                }
            });

        });

    }

})(jQuery);
