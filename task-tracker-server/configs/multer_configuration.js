// Copyright (c) 2020 Anastasiia Birillo

module.exports = (multer) => {

    const crypto = require('crypto');

    const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            cb(null, `${__dirname}/../uploads/`)
        },

        filename: function (req, file, cb) {
            const path = require('path');
            const currentDate = Date.now();
            const min = 0;
            const randomNumber = Math.random() * (currentDate - min) + min;
            const filename = randomNumber + '-' + currentDate + '-' + file.originalname;
            const hashedName = file.originalname.split(' ').join('_').split('.').slice(0, -1).join('.') + '_'
                + randomNumber + '_' +
                crypto.createHmac('sha1', crypto.createHmac('sha256', '0').update(file.mimetype).digest('hex').toString())
                .update(filename).digest('hex');
            cb(null, hashedName + path.extname(file.originalname));
        }
    });

    const upload = multer({
        storage: storage
    });

    return upload;
};
