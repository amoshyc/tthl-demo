function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

var Signal = () => {
    var obj = {
        'slots': [],
        'register': (slot) => {
            obj.slots.push(slot);
        },
        'trigger': (...args) => {
            for (var idx in obj.slots) {
                obj.slots[idx].apply(null, args);
            }
        },
    };
    return obj;
};

var signals = {
    'input.submit': Signal(), // When send button is clicked
    'video.complete': Signal(), // When highlight is generated
};

var section1 = {
    'init': () => {
        $('#submit').click(() => {
            signals['input.submit'].trigger();
        });
        $('#input input').keyup((e) => {
            if (e.keyCode == 13) {
                signals['input.submit'].trigger();
            }
        });
        signals['input.submit'].register(section1.submit);
    },
    'submit': () => {
        var data = {
            'url': $('#input_input').val()
        };
        $.post('./data', data, (ret) => {
            signals['video.complete'].trigger(ret);
        });
    },
};

var section2 = {
    'init': () => {
        signals['input.submit'].register(section2.onSubmit);
        signals['video.complete'].register(section2.onComplete);
        $('#loading').hide();
        $('result').hide()
    },
    'onSubmit': () => {
        $('#loading').show();
        $('#result').hide();
    },
    'onComplete': (data) => {
        $('#loading').hide();
        $('#result').show();

        $('#v30 video').attr('src', 'result/v30.mp4');
        $('#hl video').attr('src', 'result/hl.mp4');
    },
};

var section3 = {
    'init': () => {
        signals['input.submit'].register(section3.onSubmit);
        signals['video.complete'].register(section3.onComplete);
        $('#images').hide();
    },
    'onSubmit': () => {
        $('#images').hide();
        for (var i = 0; i < 30; i++) {
            var elem = $('#images > img').eq(i);
            elem.attr('src', '');
            elem.removeClass('pred-true');
        }
    },
    'onComplete': (data) => {
        var pred = data['pred'];
        for (var i in pred) {
            var elem = $('#images > img').eq(i);
            elem.attr('src', 'result/players/' + pad(i, 2) + '.jpg');
            if (pred[i]) {
                elem.addClass('pred-true');
            }
        }
        $('#images').show();
    },
};

var navigation = {
    'init': () => {
        signals['input.submit'].register(navigation.onSubmit);
    },
    'onSubmit': () => {
        // To trigger smooth scroll, don't use $('#a2').click()
        document.getElementById('a2').click();
    },
};

$(function () {
    section1.init();
    section2.init();
    section3.init();
    navigation.init();
});