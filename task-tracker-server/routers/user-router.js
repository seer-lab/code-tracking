// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../consts/consts').BASE_URL;
const userController = require('../controllers/user-controller');

module.exports = (app, upload) => {

    app.route(`${BASE_URL.USER}`).post(async (req, res, next) => {
        const response = await userController.createUser();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData().id)
        }
    });

    app.route(`${BASE_URL.USER}/:id`).put( async (req, res, next) => {
        const response = await userController.addData(req.params.id, req.body.diId, req.body.atiId);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });

    app.route(`${BASE_URL.USER}/all`).get(async (req, res, next) => {
        const response = await userController.getAllUsers();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            let users = [];
            for(const user of response){
                users.push(user.getPublicData());
            }
            res.json(users);
        }
    });

    app.route(`${BASE_URL.USER}/:id`).get(async (req, res, next) => {
        const response = await userController.getUserByExternalId(req.params.id);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(response.getPublicData())
        }
    });
};
