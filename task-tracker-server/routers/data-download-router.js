// Copyright (c) 2020 Anastasiia Birillo

const dataDownloadService = require('../services/data-download-service');

module.exports = (app) => {

    app.route('/api/data/download').get(async (req, res, next) => {
        const response = await dataDownloadService.dataDownload();
        const absolute_path = req.protocol + '://' + req.headers['host'] + response.path;
        res.json({
            path: absolute_path,
            isAll: response.isAll
        });

    });
};
