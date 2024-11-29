// Copyright (c) 2020 Anastasiia Birillo

const APP_DIR = require('path').dirname(require.main.filename);

const objectType = {
    MODELS: {
        configPath: `${APP_DIR}/configs/injection-configs/models`,
        filePath: `${APP_DIR}/models`
    },
    ROUTERS: {
        configPath: `${APP_DIR}/configs/injection-configs/routers`,
        filePath: `${APP_DIR}/routers`
    }
};

const injectModels = () => {
    const modelsConfig = require(objectType.MODELS.configPath);
    for (const model of modelsConfig)
        require(`${objectType.MODELS.filePath}/${model.path}`);
};

const injectRouters = (app, injector, agent) => {
    const routersConfig = require(objectType.ROUTERS.configPath);
    for (const router of routersConfig)
        require(`${objectType.ROUTERS.filePath}/${router.path}`)(app, injector, agent);
};


module.exports = {
    injectModels,
    injectRouters
};
