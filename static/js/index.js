function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

$(document).ready(() => {
    $('#public').prop("checked", true);
    $.ajax({
        type: 'GET',
        url: '/api/codes',
        success: (res) => {
            if (res != "403") {
                for (let code of res) {
                    $('#site-body').append(`
                        <div class="snippet">
                            <div class="snippet-title">
                                ${code.title ?? 'Snippet #' + code.code_id}
                            </div>
                            <div class="rollover-outer">
                                <div class="rollover">
                                    <pre>${escapeHtml(code.content)}</pre>
                                </div>
                            </div>
                        </div>
                    `);
                }
                $('.snippet').on('click', (e) => {
                    console.log(e);
                    var snippet = e.currentTarget.children[1].children[0].children[0].innerHTML;
                    navigator.clipboard.writeText(snippet).then(
                        () => {
                            $(e.currentTarget).addClass('good-flash');
                            setTimeout(() => {
                                $(e.currentTarget).removeClass('good-flash');
                            }, 1000);
                        }, 
                        () => {
                            $(e.currentTarget).addClass('bad-flash');
                            setTimeout(() => {
                                $(e.currentTarget).removeClass('bad-flash');
                            }, 1000);
                        }
                    );
                });
            }
        }
    });
});

$(document).on('paste', (e) => {
    requestAnimationFrame(() => {
        $('.upload-modal').addClass('visible');
    });
    $('#content').val(e.originalEvent.clipboardData.getData('text'));
});

$(document).on('click', (e) => {
    if (e.target == $('.upload-modal')[0]) {
        $('.upload-modal').removeClass('visible');
    }
});

$('#upload-snippet').on('click', (e) => {
    $.ajax({
        type: 'POST',
        url: '/api/codes',
        data: {
            title: $('#title').val(),
            content: $('#content').val(),
            visibility: $('input[name="visibility"]:checked').val()
        },
        success: (res) => {
            console.log(res);
        }
    })
});