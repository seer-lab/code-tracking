// Copyright (c) 2020 Anastasiia Birillo

const intelLogger = require('intel');

const fileService = require('../services/file-service');
const diService = require('../services/data-item-service');
const userService = require('../services/user-service');
const LOGGER_NAME = require('../consts/consts').LOGGER_NAME;
const atiService = require('../services/activity-tracker-item-service');

const logger = intelLogger.getLogger(LOGGER_NAME);
const APP_DIR = require('path').dirname(require.main.filename) + '/';

const dataDownload = async () => {
    const rootDir = './data';
    fileService.initDirectory(rootDir);

    logger.info(`${new Date()}: ...starting get all users`);
    const users = await userService.getAllUsers();
    logger.info(`${new Date()}: ${users.length} users was received successfully`);
    let countNotEmptyUsers = 0;
    let countHandledUsers = 0;
    for(const user of users) {
        logger.info(`${new Date()}: ...starting handle user with id ${user.externalStudentId}`);
        if (user.data && user.data.length > 0) {
            countNotEmptyUsers += 1;
            const userDirectory = `${rootDir}/user_${user.externalStudentId}`
            fileService.createDirectory(userDirectory);
            for(const data of user.data) {
                const dataItem = await diService.getDiByExternalId(Number(data.dataItemKey));
                if (!dataItem) {
                    logger.info(`${new Date()}: data item with id ${data.dataItemKey} does not exist`);
                    continue
                }
                const taskFullName = dataItem.codePath.split('/').pop();
                const taskName = taskFullName.slice(0, taskFullName.indexOf('_'));
                const currentPath = `${userDirectory}/${taskName}`;
                fileService.createDirectory(currentPath);
                copyFile(dataItem.codePath, currentPath);

                const activityTrackerItem = await atiService.getAtiByExternalId(Number(data.activityTrackerKey));
                if (!activityTrackerItem) {
                    logger.info(`${new Date()}: activity tracker item with id ${data.activityTrackerKey} does not exist`);
                } else {
                    if (activityTrackerItem.codePath) {
                        copyFile(activityTrackerItem.codePath, currentPath);
                    }
                }
            }

        }
        countHandledUsers += 1;
    }

    logger.info(`${new Date()}: ...is creating archive`);
    const resultPath = await fileService.createArchive(APP_DIR + rootDir.substr(2));
    logger.info(`${new Date()}: ...is deleting tmp folder`);
    await fileService.deleteDirectory(APP_DIR + rootDir.substr(2));

    return {
        path: resultPath,
        isAll: countHandledUsers === users.length
    }
};

const copyFile = (oldPath, newPath) => {
    const sourcePath = getFileSystemPath(oldPath, 'uploads');
    const destinationPath = sourcePath.replace('/uploads', newPath.substr(1));
    return !!fileService.copyFile(sourcePath, destinationPath);
};

const getFileSystemPath = (path, word) => {
    const index = path.indexOf(word);
    if (index !== -1)
        return APP_DIR + path.substr(index);
    return path;
};

module.exports = {
    dataDownload
};
