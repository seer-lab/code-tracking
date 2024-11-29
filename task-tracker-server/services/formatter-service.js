// Copyright (c) 2020 Anastasiia Birillo

const toLowerCase = (str) => {
    return str.toLowerCase()
};

const dropLastWhile = (str, char=':') => {
    for (let i = str.length - 1; i > 0; i--) {
        if (str[i] !== char) {
            return str.substring(0, i + 1)
        }
    }
    return ""
};

const toLowerCaseWithColon = (str) => {
    return toLowerCase(dropLastWhile(str, ':') + ':')
};

const toCapitalize = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1)
};

const applyFormatter = (obj, keysToApply, formatter) => {
    for(const key of keysToApply) {
        if (obj[key]) {
            obj[key] = formatter(obj[key])
        }
    }
    return obj;
};

// Subtract: array1 - array2
const subtractArrays = (array1, array2) => {
    return array1.filter(n => !array2.includes(n));
};

module.exports = {
    toLowerCase,
    toCapitalize,
    subtractArrays,
    applyFormatter,
    toLowerCaseWithColon
};
