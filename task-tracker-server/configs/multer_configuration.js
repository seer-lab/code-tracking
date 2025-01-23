// JavaScript
const path = require('path');
const crypto = require('crypto');

module.exports = (multer) => {
    const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            cb(null, `${__dirname}/../uploads/`);
        },
        filename: function (req, file, cb) {
            const currentDate = Date.now();
            const min = 0;
            const randomNumber = Math.random() * (currentDate - min) + min;
            const filename = randomNumber + '-' + currentDate + '-' + file.originalname;
            const hashedName = file.originalname.split(' ').join('_').split('.').slice(0, -1).join('.') + '_'
                + randomNumber + '_' +
                crypto.createHmac('sha1', crypto.createHmac('sha256', '0').update(file.mimetype).digest('hex').toString())
                .update(filename).digest('hex');
            const relativePath = `uploads/${hashedName + path.extname(file.originalname)}`;
            const formattedPath = `http://localhost:3000/${relativePath.replace(/\\/g, '/')}`;
            cb(null, formattedPath);
        }
    });

    const upload = multer({
        storage: storage
    });

    return upload;
};