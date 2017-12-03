var Signal = () => {
    var obj = {
        'slots': [],
        'register': (slot) => {
            obj.slots.push(slot);
        },
        'trigger': (args) => {
            for (var idx in obj.slots) {
                obj.slots[idx].apply(null, args);
            }
        },
    };
    return obj;
};

var signals = {
    'input.submit': Signal(),
    'video.complete': Signal(),
};

var section1 = {
    'init': () => {
        $('#submit').click(() => {
            signals['input.submit'].trigger();
        });
        signals['input.submit'].register(section1.onSubmit);
    },
    'onSubmit': () => {
        var data = {
            'url': $('#input_input').val()
        };
        $.post('./data', data, () => {
            signals['video.complete'].trigger();
        });
    },
};

var section2 = {
    'init': () => {
        signals['input.submit'].register(section2.onSubmit);
        signals['video.complete'].register(section2.onComplete);
    },
    'onSubmit': () => {
        $('#loading').show();
        $('#result').hide();
    },
    'onComplete': () => {
        $('#loading').hide();
        $('#result').show();
    },
};

var navigation = {
    'init': () => {
        signals['input.submit'].register(navigation.onSubmit);
    },
    'onSubmit': () => {
        document.getElementById('a2').click();
    },
};

$(function () {
    section1.init();
    section2.init();
    navigation.init();
});