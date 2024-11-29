// Copyright (c) 2020 Anastasiia Birillo

const BASE_URL = require('../consts/consts').BASE_URL;
const taskController = require('../controllers/task-controller');

module.exports = (app, upload) => {

    app.route(`${BASE_URL.TASK}`).post(async (req, res, next) => {
        const response = await taskController.createTask(req.body.key.toLowerCase(), req.body.descriptions, req.body.examples);
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.TASK}/all`).get(async (req, res, next) => {
        const response = await taskController.getAllTasks();
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            let tasks = [];
            for(const task of response){
                tasks.push(await task.getAsyncPublicData());
            }
            res.json(tasks);
        }
    });

    app.route(`${BASE_URL.TASK}/:key`).get(async (req, res, next) => {
        const response = await taskController.getTaskByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

    app.route(`${BASE_URL.TASK}/:key`).delete(async (req, res, next) => {
        const response = await taskController.deleteTaskByKey(req.params.key.toLowerCase());
        if (response.error) {
            res.status(response.error.code);
            res.json(response.error.content);
            res.end();
        } else {
            res.json(await response.getAsyncPublicData())
        }
    });

};
